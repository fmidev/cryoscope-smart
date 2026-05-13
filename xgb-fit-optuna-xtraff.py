#!/usr/bin/env python3
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
# CHANGED: added cohen_kappa_score and recall_score
from sklearn.metrics import f1_score, classification_report, cohen_kappa_score, recall_score
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
import matplotlib.pyplot as plt
import optuna, os, sys, joblib, json, shap
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

'''
Optuna hyperparameter optimization for XGBoost IBA soil moisture classifier.
(Includes oversampling and class weighting to handle imbalanced classes.)
Trains and saves best model, SHAP analysis, confusion matrix, and metrics.

Usage: python xgb-iba-optuna.py <study_number>
'''

study_number = sys.argv[1]
studyName = f'xgb_waterinyourboots_{study_number}'
print(f"Study name: {studyName}")

class_names = ['Very dry', 'Dry', 'Moist', 'Wet', 'Extremely wet']

# ====================================================================
# CHANGED: Optuna optimization metric configuration
# Choose the metric Optuna maximizes. All metrics are reported in
# the evaluation regardless of which one is used for optimization.
#   'qwk'          - Quadratic Weighted Kappa (ordinal-aware, recommended)
#   'macro_f1'     - Macro-averaged F1 score (original)
#   'macro_recall' - Macro-averaged recall (emphasises not missing classes)
#   'composite'    - 0.6 * QWK + 0.4 * Macro F1
# ====================================================================
OPTIMIZATION_METRIC = 'qwk'

METRIC_DISPLAY_NAMES = {
    'qwk':          'Quadratic Weighted Kappa',
    'macro_f1':     'Macro F1',
    'macro_recall': 'Macro Recall',
    'composite':    '0.6 * QWK + 0.4 * Macro F1',
}

def compute_score(y_true, y_pred, metric=OPTIMIZATION_METRIC):
    """Single-value scoring function for Optuna."""
    if metric == 'qwk':
        return cohen_kappa_score(y_true, y_pred, weights='quadratic')
    elif metric == 'macro_f1':
        return f1_score(y_true, y_pred, average='macro')
    elif metric == 'macro_recall':
        return recall_score(y_true, y_pred, average='macro')
    elif metric == 'composite':
        return (0.6 * cohen_kappa_score(y_true, y_pred, weights='quadratic')
                + 0.4 * f1_score(y_true, y_pred, average='macro'))
    else:
        raise ValueError(f"Unknown OPTIMIZATION_METRIC: {metric}")

def compute_all_metrics(y_true, y_pred):
    """Compute all relevant metrics for reporting."""
    return {
        'macro_f1':     f1_score(y_true, y_pred, average='macro'),
        'macro_recall': recall_score(y_true, y_pred, average='macro'),
        'qwk':          cohen_kappa_score(y_true, y_pred, weights='quadratic'),
    }

print(f"Optimization metric: {METRIC_DISPLAY_NAMES[OPTIMIZATION_METRIC]}")
# ====================================================================

# paths
optuna_dir = '/home/smartmet/copernicus/IBAML/'
mod_dir = f'{optuna_dir}/models/'
res_dir = f'{optuna_dir}/results/'
os.makedirs(mod_dir, exist_ok=True)
os.makedirs(res_dir, exist_ok=True)

os.chdir(optuna_dir)

input_file = f'{optuna_dir}xtraff_training_data_filled.csv'

# Columns used in training (not used are commented out)
use_cols=[#'time', 'latitude', 'longitude', 'latlon_id', 'certainty', 'date', 'closest_hour', 'answer',
          'class_target', 'accuracy_own',
          'swi1', 'swi2',
          'clay_0-5cm', 'clay_5-15cm', 'clay_15-30cm',
          'sand_0-5cm', 'sand_5-15cm', 'sand_15-30cm',
          'silt_0-5cm', 'silt_5-15cm', 'silt_15-30cm',
          'soc_0-5cm', 'soc_5-15cm', 'soc_15-30cm',
          'dtm_height', 'dtm_aspect', 'dtm_slope',
          'twi', 'tri',
          'cvh', 'lake_cover', 'land_cover', 'tvh', 'urban_cover', 'cvl', 'lake_depth', 'soiltype', 'tvl',
          #'laihv_era5l', 'lailv_era5l',
          'rsn', 'sd', 
          'skt', 'sp', 'src', 'stl1', 'stl2',# 'stl3', 'stl4',
          'swvl1', 'swvl2', 'swvl3', #'swvl4',
          't2', 'td2', 'u10', 'v10',
          'e', 'ep', 'ro', 'sf', 'slhf', 'sro', 'sshf', 'ssr', 'ssrd', 'ssro',
          'str', 'strd', #'t24max', 't24min', 
          'tp', #'kx', 'lsp',
          'q700', 't700', 'u700','v700', 'z700', 
          'q850', 't850', 'u850', 'v850', 'z850', 
          'q925', 't925', 'u925', 'v925', 'z925',
          #'laihv_ecc', 'lailv_ecc',
          #'DayOfYear',
          'laihv', 'lailv',
          'doy_sin', 'doy_cos']

# Read in training data
df = pd.read_csv(input_file, usecols=use_cols)
print(df)

# Drop columns that are entirely NaN
df = df.dropna(axis=1, how='all')

print(f"Dataset shape: {df.shape}")
print(f"Class distribution:\n{df['class_target'].value_counts().sort_index()}")

# Split to features (X) and target (y)
X = df.drop(columns=['class_target'])
y = df['class_target']

print(X.columns.tolist())
print(f"Features: {len(X.columns)}")

### 2-way stratified split: train / validation
X_train, X_valid, y_train, y_valid = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
print(f"Train: {len(X_train)}, Valid: {len(X_valid)}")
print(f"  Train classes: {dict(y_train.value_counts().sort_index())}")
print(f"  Valid classes:  {dict(y_valid.value_counts().sort_index())}")

# Handle class imbalance by oversampling in the training set
def oversample_minority_classes(X_train, y_train, target_ratio=0.5):
    df_train = X_train.copy()
    df_train['class_target'] = y_train.values

    class_counts = df_train['class_target'].value_counts()
    majority_count = class_counts.max()
    target_count = int(majority_count * target_ratio)

    oversample_log = []
    frames = [df_train]
    for cls, count in class_counts.items():
        if count < target_count:
            deficit = target_count - count
            df_minority = df_train[df_train['class_target'] == cls]
            df_upsampled = df_minority.sample(n=deficit, replace=True, random_state=42)
            frames.append(df_upsampled)
            msg = f"  Oversampled class {cls} ({class_names[cls]}): {count} -> {count + deficit}"
            print(msg)
            oversample_log.append(msg)

    df_oversampled = pd.concat(frames, ignore_index=True)
    df_oversampled = df_oversampled.sample(frac=1, random_state=42).reset_index(drop=True)

    y_out = df_oversampled['class_target']
    X_out = df_oversampled.drop(columns=['class_target'])
    return X_out, y_out, oversample_log


print("\nOversampling minority classes (training set only)...")
X_train_os, y_train_os, oversample_log = oversample_minority_classes(X_train, y_train, target_ratio=0.5)
print(f"After oversampling: {len(X_train_os)} samples")
print(f"Class distribution:\n{y_train_os.value_counts().sort_index()}")

# Compute balanced class weights as sample weights
classes = np.unique(y_train_os)
weights = compute_class_weight(class_weight='balanced', classes=classes, y=y_train_os)
class_weights = dict(zip(classes, weights))
sample_weights = y_train_os.map(class_weights)
print(f"Class weights: {class_weights}")

# Optuna objective function for hyperparameter tuning and finding best model parameters
def objective(trial):
    params = {
        'objective': 'multi:softmax',
        'num_class': 5,
        'eval_metric': 'mlogloss',
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.005, 0.3, log=True),
        'n_estimators': trial.suggest_int('n_estimators', 500, 1500,step=100),
        'subsample': trial.suggest_float('subsample', 0.5, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
        'gamma': trial.suggest_float('gamma', 0.0, 5.0),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
        'reg_alpha': trial.suggest_float('reg_alpha', 0.0, 2.0),
        'reg_lambda': trial.suggest_float('reg_lambda', 0.5, 10.0),
        'early_stopping_rounds': 50,
        'verbosity': 0,
    }

    model = xgb.XGBClassifier(**params)

    model.fit(
        X_train_os, y_train_os,
        sample_weight=sample_weights,
        eval_set=[(X_valid, y_valid)],
        verbose=False,
    )

    y_pred = model.predict(X_valid)
    # CHANGED: use compute_score() with configurable metric
    score = compute_score(y_valid, y_pred)
    return score

# Run Optuna study
study = optuna.create_study(
    study_name=studyName,
    storage="sqlite:///iba_optuna.sqlite3",
    direction="maximize",
    load_if_exists=True,
)
study.optimize(objective, n_trials=100)

# Optuna optimization history plot (dashboard not working)
# CHANGED: dynamic metric label in plot
metric_label = METRIC_DISPLAY_NAMES[OPTIMIZATION_METRIC]
trials = study.trials
trial_numbers = [t.number for t in trials]
trial_values = [t.value if t.value is not None else np.nan for t in trials]
best_so_far = pd.Series(trial_values).cummax()

fig, ax = plt.subplots(figsize=(10, 5))
ax.scatter(trial_numbers, trial_values, s=15, alpha=0.6, label=f'Trial {metric_label}')
ax.plot(trial_numbers, best_so_far, color='red', linewidth=1.5, label='Best so far')
ax.set_xlabel('Trial number')
ax.set_ylabel(metric_label)
ax.set_title(f'Optuna Optimization History ({metric_label}) — {studyName}')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()

plot_file = os.path.join(optuna_dir, f'optuna_history_{studyName}')
plt.savefig(plot_file + '.png', dpi=200)
plt.savefig(plot_file + '.svg')
plt.close()
print(f"Optimization history plot saved to {plot_file}.png/.svg")

# Results summary
print("\n" + "=" * 60)
print("BEST TRIAL")
print("=" * 60)
trial = study.best_trial
# CHANGED: dynamic metric name in printout
print(f"{metric_label} (validation): {trial.value:.4f}")
print(f"Params: {trial.params}")

# Retrain final model with best params
best_params = trial.params
best_params['num_class'] = 5
best_params['eval_metric'] = 'mlogloss'
best_params['early_stopping_rounds'] = 50
best_params['verbosity'] = 1

final_model = xgb.XGBClassifier(**best_params)
final_model.fit(
    X_train_os, y_train_os,
    sample_weight=sample_weights,
    eval_set=[(X_valid, y_valid)],
    verbose=50,
)

# Save model, study and feature list
final_model.save_model(f'{mod_dir}xgb_iba_soilmoistureclass_model_{studyName}.json')
joblib.dump(study, f'{mod_dir}xgb_iba_soilmoistureclass_study_{studyName}.pkl')
feature_list_file = f'{mod_dir}xgb_iba_features_{studyName}.json'
with open(feature_list_file, 'w') as fout:
    json.dump(final_model.get_booster().feature_names, fout, indent=2)
print(f"Feature list saved to {feature_list_file}")


# CHANGED: evaluate_and_save now returns and prints all three metrics
def evaluate_and_save(model, X_data, y_data, dataset_label, studyName, res_dir, class_names):
    y_pred = model.predict(X_data)
    all_metrics = compute_all_metrics(y_data, y_pred)

    report_str = classification_report(y_data, y_pred, target_names=class_names)
    print(f"\n{'=' * 60}")
    print(f"CLASSIFICATION REPORT — {dataset_label} (n={len(y_data)})")
    print(f"{'=' * 60}")
    print(report_str)
    print(f"  Macro F1:                  {all_metrics['macro_f1']:.4f}")
    print(f"  Macro Recall:              {all_metrics['macro_recall']:.4f}")
    print(f"  Quadratic Weighted Kappa:  {all_metrics['qwk']:.4f}")

    # Save metrics CSV (per-class report + summary metrics row)
    report_dict = classification_report(y_data, y_pred, target_names=class_names, output_dict=True)
    df_report = pd.DataFrame(report_dict).transpose()
    # Append the additional summary metrics as a separate row
    df_report.loc['quadratic_weighted_kappa'] = [np.nan, np.nan, all_metrics['qwk'], np.nan]
    metrics_file = f'{res_dir}xgb_iba_metrics_{dataset_label}_{studyName}.csv'
    df_report.to_csv(metrics_file, index=True, index_label="class")
    print(f"Metrics saved to {metrics_file}")

    # Confusion matrix
    cm = confusion_matrix(y_data, y_pred)
    fig, ax = plt.subplots(figsize=(8, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    disp.plot(ax=ax, cmap='Blues', values_format='d')
    ax.set_title(f'Confusion Matrix — {dataset_label} — {studyName}')
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    cm_file = f'{res_dir}iba_confusion_matrix_{dataset_label}_{studyName}'
    plt.savefig(cm_file + '.png', dpi=200)
    plt.savefig(cm_file + '.svg')
    plt.close()
    print(f"Confusion matrix saved to {cm_file}.png/.svg")

    return report_str, all_metrics


# CHANGED: callers now receive dict of all metrics instead of just macro F1
report_train, metrics_train = evaluate_and_save(
    final_model, X_train, y_train, "train", studyName, res_dir, class_names)
report_valid, metrics_valid = evaluate_and_save(
    final_model, X_valid, y_valid, "valid", studyName, res_dir, class_names)
report_full, metrics_full = evaluate_and_save(
    final_model, X, y, "full", studyName, res_dir, class_names)


# Save summary txt: oversampling info + classification reports
summary_file = f'{res_dir}xgb_iba_summary_{studyName}.txt'
with open(summary_file, 'w') as f:
    f.write(f"Study: {studyName}\n")
    f.write(f"Input file: {input_file}\n")
    # CHANGED: log which optimization metric was used
    f.write(f"Optimization metric: {METRIC_DISPLAY_NAMES[OPTIMIZATION_METRIC]} "
            f"(key: {OPTIMIZATION_METRIC})\n")
    f.write(f"Dataset shape: {df.shape}\n")
    f.write(f"Features: {len(X.columns)}\n")
    f.write(f"Feature list: {list(X.columns)}\n\n")

    f.write("=" * 60 + "\n")
    f.write("CLASS DISTRIBUTION (full dataset)\n")
    f.write("=" * 60 + "\n")
    for cls_idx in sorted(y.unique()):
        cnt = (y == cls_idx).sum()
        f.write(f"  {cls_idx} ({class_names[cls_idx]}): {cnt}\n")

    f.write(f"\nTrain: {len(X_train)}, Valid: {len(X_valid)}\n")
    f.write(f"Train classes: {dict(y_train.value_counts().sort_index())}\n")
    f.write(f"Valid classes:  {dict(y_valid.value_counts().sort_index())}\n\n")

    f.write("=" * 60 + "\n")
    f.write("OVERSAMPLING (training set only, target_ratio=0.5)\n")
    f.write("=" * 60 + "\n")
    for line in oversample_log:
        f.write(line + "\n")
    f.write(f"After oversampling: {len(X_train_os)} samples\n")
    f.write(f"Class distribution after oversampling:\n")
    for cls_idx in sorted(y_train_os.unique()):
        cnt = (y_train_os == cls_idx).sum()
        f.write(f"  {cls_idx} ({class_names[cls_idx]}): {cnt}\n")
    f.write(f"Class weights: {class_weights}\n\n")

    f.write("=" * 60 + "\n")
    f.write("BEST OPTUNA TRIAL\n")
    f.write("=" * 60 + "\n")
    # CHANGED: dynamic label
    f.write(f"{metric_label} (validation, Optuna): {trial.value:.4f}\n")
    f.write(f"Params: {json.dumps(trial.params, indent=2)}\n\n")

    # CHANGED: include all three metrics for each split
    for label, metrics, report in [
        ("train", metrics_train, report_train),
        ("valid", metrics_valid, report_valid),
        ("full",  metrics_full,  report_full),
    ]:
        n = {'train': len(y_train), 'valid': len(y_valid), 'full': len(y)}[label]
        f.write("=" * 60 + "\n")
        f.write(f"CLASSIFICATION REPORT — {label} (n={n})\n")
        f.write("=" * 60 + "\n")
        f.write(report + "\n")
        f.write(f"Macro F1:                  {metrics['macro_f1']:.4f}\n")
        f.write(f"Macro Recall:              {metrics['macro_recall']:.4f}\n")
        f.write(f"Quadratic Weighted Kappa:  {metrics['qwk']:.4f}\n\n")

print(f"\nSummary saved to {summary_file}")

# SHAP analysis for train (raw, not oversampled), valid, and full dataset
max_shap_display = 40
model_features = final_model.get_booster().feature_names
feature_names = np.array(model_features)
explainer = shap.TreeExplainer(final_model)

def prepare_shap_data(X_input, model_features):
    # Align input data columns to model features
    X_out = X_input.copy()
    X_out = X_out[[col for col in X_out.columns if col in model_features]]
    for col in model_features:
        if col not in X_out.columns:
            X_out[col] = 0
    return X_out[model_features]

def run_shap_analysis(X_data, explainer, dataset_label, studyName, res_dir, class_names, feature_names, max_shap_display):
    print(f"\n--- SHAP analysis: {dataset_label} (n={len(X_data)}) ---")

    shap_values = explainer(X_data)
    values = shap_values.values

    if values.ndim == 3:
        shap_values_agg = np.mean(np.abs(values), axis=2)
    else:
        shap_values_agg = np.abs(values)

    # Bar plot — global feature importance
    plt.figure(figsize=(12, 8))
    shap.summary_plot(
        shap_values_agg, X_data,
        plot_type="bar", max_display=max_shap_display, show=False
    )
    plt.title(f"SHAP Mean Feature Importance — {dataset_label}")
    plt.tight_layout()
    bar_file = f'{res_dir}iba_shap_summary_bar_{dataset_label}_{studyName}'
    plt.savefig(bar_file + '.png', dpi=200)
    plt.savefig(bar_file + '.svg')
    plt.close()
    print(f"  Bar plot: {bar_file}.png/.svg")

    # Beeswarm per class
    n_classes = values.shape[2] if values.ndim == 3 else 1
    for class_idx in range(n_classes):
        if n_classes > 1:
            shap_vals_class = shap_values[:, :, class_idx]
        else:
            shap_vals_class = shap_values.values

        plt.figure(figsize=(12, 8))
        shap.summary_plot(
            shap_vals_class, X_data,
            max_display=max_shap_display, show=False
        )
        plt.title(f"SHAP Beeswarm — {class_names[class_idx]} — {dataset_label}")
        plt.tight_layout()
        beeswarm_file = f'{res_dir}iba_shap_beeswarm_{class_idx}_{dataset_label}_{studyName}'
        plt.savefig(beeswarm_file + '.png', dpi=200)
        plt.savefig(beeswarm_file + '.svg')
        plt.close()
        print(f"  Beeswarm class {class_idx}: {beeswarm_file}.png/.svg")

    # Numeric importance CSVs
    if values.ndim == 3:
        global_importance = np.abs(values).mean(axis=(0, 2))
        per_class_importance = np.abs(values).mean(axis=0)

        df_global = pd.DataFrame({
            "feature": feature_names,
            "mean_abs_shap": global_importance,
        }).sort_values("mean_abs_shap", ascending=False)

        df_per_class = pd.DataFrame(
            per_class_importance,
            columns=[class_names[i] for i in range(values.shape[2])],
        )
        df_per_class.insert(0, "feature", feature_names)
    else:
        global_importance = np.abs(values).mean(axis=0)
        df_global = pd.DataFrame({
            "feature": feature_names,
            "mean_abs_shap": global_importance,
        }).sort_values("mean_abs_shap", ascending=False)
        df_per_class = None

    df_global.to_csv(f'{res_dir}iba_shap_global_importance_{dataset_label}_{studyName}.csv', index=False)
    if df_per_class is not None:
        df_per_class.to_csv(f'{res_dir}iba_shap_importance_per_class_{dataset_label}_{studyName}.csv', index=False)

    # Save raw SHAP values
    np.savez_compressed(
        f'{res_dir}iba_shap_values_{dataset_label}_{studyName}.npz',
        shap_values=values,
        base_values=shap_values.base_values,
        data=X_data.to_numpy(),
        feature_names=feature_names,
    )
    print(f"  Saved CSVs and npz for {dataset_label}")


# Prepare datasets (raw X_train without oversampling!)
X_shap_train = prepare_shap_data(X_train, model_features)
X_shap_valid = prepare_shap_data(X_valid, model_features)
X_shap_full = prepare_shap_data(X, model_features)

# Run SHAP for each dataset
run_shap_analysis(X_shap_train, explainer, "train", studyName, res_dir,
                  class_names, feature_names, max_shap_display)

run_shap_analysis(X_shap_valid, explainer, "valid", studyName, res_dir,
                  class_names, feature_names, max_shap_display)

run_shap_analysis(X_shap_full, explainer, "full", studyName, res_dir,
                  class_names, feature_names, max_shap_display)