```mermaid
%%{init: {"flowchart": {"subGraphTitleMargin": {"top": 10, "bottom": 10}, "nodeSpacing": 45, "rankSpacing": 60, "padding": 12}, "themeCSS": ".nodeLabel, .nodeLabel * { text-align: left !important; } .cluster-label, .cluster-label * { font-weight: 700 !important; font-size: 15px !important; } .node rect, .node polygon { rx: 8; ry: 8; } .cluster rect { rx: 12; ry: 12; }"}}%%
flowchart LR
    features["<div style='text-align:left'><b>Features</b><br/>──────────<br/>Predictor datasets shared across all streams: <br/>• Reanalysis (ERA5-Land, ERA5, CARRA)<br/>• Copernicus DEM<br/>• Soilgrids<br/>• Others list here<br/>Use source-specified yamls to build tailored training data sets from all available features.</div>"]
    subgraph tdp["<b>Training data processing</b><br/>per prediction goal type"]
        direction TB
        ecens["<div style='text-align:left'><b>Prediction goal type:<br/>EC-ENS 15-day forecasts</b><br/>──────────────────<br/>Several reanalysis matching features</div>"]
        sf["<div style='text-align:left'><b>Prediction goal type:<br/>SF 215-day forecasts</b><br/>──────────────────<br/>Limited reanalysis matching features</div>"]
        cmip["<div style='text-align:left'><b>Prediction goal type:<br/>CMIP climate projections</b><br/>──────────────────<br/>Only a few reanalysis matching features</div>"]
        history["<div style='text-align:left'><b>Prediction goal type:<br/>History</b><br/>──────────<br/>All reanalysis matching with update frequency lagging</div>"]
    end
    subgraph xgb["<b>XGBoost model training</b>"]
        direction TB
        mod1["<div style='text-align:left'><b>EC-ENS Models</b><br/>──────────<br/>XGBoost with training data reanalysis features matching EC-ENS features</div>"]
        mod2["<div style='text-align:left'><b>SF Models</b><br/>──────────<br/>XGBoost with training data reanalysis features matching SF features</div>"]
        mod3["<div style='text-align:left'><b>CMIP models</b><br/>──────────<br/>XGBoost with training data reanalysis features matching CMIP features</div>"]
        mod4["<div style='text-align:left'><b>History models</b><br/>──────────<br/>XGBoost with training data reanalysis features matching (latest updated) reanalysis features</div>"]
    end
    subgraph pp["<b>Prediction production</b>"]
        direction TB
        pred1["<div style='text-align:left'><b>EC-ENS (sm.cryo-scope.eu)</b><br/>──────────<br/>1. Download and pre-process raw data from Mars daily. Set up data to SmartMet server.  <br/>2. Run XGBoost predictions from one shell script; separate python scripts per model target. All use same input files to avoid several tmp files.<br/><br/>Alt server name: smart.nsdc.fmi.fi</div>"]
        pred2["<div style='text-align:left'><b>SF (smartmet.xyz)</b><br/>──────────<br/>1. Download and pre-process raw data from CDS monthly. Set up data to SmartMet server.  <br/>2. Run XGBoost predictions from one shell script; separate python scripts per model target. All use same input files to avoid several tmp files.<br/><br/>Alt server name: desm.harvesterseasons.com</div>"]
        pred3["<div style='text-align:left'><b>CMIP6</b><br/>──────────<br/>(text to come)</div>"]
        pred4["<div style='text-align:left'><b>History</b><br/>──────────<br/>(text to come)</div>"]
    end
    ec_dl["<div style='text-align:left'><b>EC-ENS download<br/>get-ec-ens.sh</div>"]
    ec_wf["<div style='text-align:left'><b>EC-ENS XGBoost<br/>run-xgb-ec-ens.sh</div>"]
    sf_dl["<div style='text-align:left'><b>SF download<br/>get-seasonal.sh</div>"]
    sf_wf["<div style='text-align:left'><b>SF XGBoost<br/>run-xgb-seasonal.sh</div>"]
    cm_dl["<div style='text-align:left'><b>CMIP6 processing</b></div>"]
    cm_wf["<div style='text-align:left'><b>CMIP6 XGBoost</b></div>"]
    hist_dl["<div style='text-align:left'><b>History processing<br/>get-history.sh</div>"]
    hist_wf["<div style='text-align:left'><b>History XGBoost<br/>run-xgb-history.sh</div>"]

    ec_py1["<b>target predictions 1<br/>python script"]
    ec_py2["<b>target predictions 2<br/>python script"]
    ec_py3["<b>etc<br/>python script"]
    sf_py1["<b>target predictions 1<br/>python script"]
    sf_py2["<b>target predictions 2<br/>python script"]
    sf_py3["<b>etc<br/>python script"]
    cm_py1["<b>target predictions 1<br/>python script"]
    cm_py2["<b>target predictions 2<br/>python script"]
    cm_py3["<b>etc<br/>python script"]
    hist_py1["<b>target predictions 1<br/>python script"]
    hist_py2["<b>target predictions 2<br/>python script"]
    hist_py3["<b>etc<br/>python script"]

    d_tdp["<div style='text-align:left'><b>Training data processing</b><br/>──────────<br/>Builds prediction type matched training data set to locations specified by training target variable. Feature overlap (reanalysis vs. prediction target type) decreases from EC-ENS to CMIP.<br/><br/>Included steps: <br/>• Acquiring the target feature with at least location and time information<br/>• Downloading data from SmartMet server(s) with python script(s)<br/>• Fetching data with gdallocationinfo from s3<br/>•  Merging all input features and target to one csv file: training data input file. Add time-dependent features (such as sine of day of year).<br/>• Explanatory Data Analysis (EDA) on training data set <br/></div>"]
    d_xgb["<div style='text-align:left'><b>XGBoost model training</b><br/>──────────<br/>Training the model with XGBoost. If input training features, train/test splitting method, and hyperparameter options (objective, regression/classification, etc) are read in from a separate file, this could be one script to rule them all. <br/><br/>Included steps: <br/>• Optimal splitting of all training data to train and test sets: KFold, TimeseriesCV, other? Validation is carried out separately in prediction phase.<br/>• Optuna + XGBoost hyperparameter tuning and saving the best trained model <br/>• SHAP analysis and other model metrics<br/>• Feature engineering (read feature names used in training a specific model from file)</div>"]
    d_pp["<div style='text-align:left'><b>XGBoost Prediction Production</b><br/>──────────<br/>Operational inference. For each stream the pipeline downloads and pre-processes the latest raw data, then runs the trained XGBoost models to generate the target predictions, all sharing the same raw input files.<br/><br/>Included steps: <br/>• Download raw data and preprocess. <br/>• Run XGBoost predictions <br/>• Set new data to SmartMet server</div>"]

    features --> ecens
    features --> sf
    features --> cmip
    features --> history
    ecens --> mod1
    sf --> mod2
    cmip --> mod3
    history --> mod4
    mod1 --> pred1
    mod2 --> pred2
    mod3 --> pred3
    mod4 --> pred4
    pred1 --> ec_dl
    pred2 --> sf_dl
    pred3 --> cm_dl
    pred4 --> hist_dl
    ec_dl --> ec_wf
    sf_dl --> sf_wf
    cm_dl --> cm_wf
    hist_dl --> hist_wf
    ec_wf --> ec_py1
    ec_wf --> ec_py2
    ec_wf --> ec_py3
    sf_wf --> sf_py1
    sf_wf --> sf_py2
    sf_wf --> sf_py3
    cm_wf --> cm_py1
    cm_wf --> cm_py2
    cm_wf --> cm_py3
    hist_wf --> hist_py1
    hist_wf --> hist_py2
    hist_wf --> hist_py3

    %% invisible links to align each description under its stage column (anchored to History row so it does not drag the top stream down)
    d_tdp ~~~ d_xgb ~~~ d_pp ~~~ hist_dl

    classDef feat fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#075985;
    classDef ec fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#166534;
    classDef seas fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e;
    classDef clim fill:#ede9fe,stroke:#7c3aed,stroke-width:2px,color:#5b21b6;
    classDef hist fill:#fce7f3,stroke:#db2777,stroke-width:2px,color:#9d174d;
    class features feat;
    class ecens,mod1,pred1,ec_dl,ec_wf,ec_py1,ec_py2,ec_py3 ec;
    class sf,mod2,pred2,sf_dl,sf_wf,sf_py1,sf_py2,sf_py3 seas;
    class cmip,mod3,pred3,cm_dl,cm_wf,cm_py1,cm_py2,cm_py3 clim;
    class history,mod4,pred4,hist_dl,hist_wf,hist_py1,hist_py2,hist_py3 hist;

    style d_tdp fill:#ffffff,stroke:#475569,stroke-width:2px,color:#1e293b
    style d_xgb fill:#ffffff,stroke:#525252,stroke-width:2px,color:#262626
    style d_pp fill:#ffffff,stroke:#0f766e,stroke-width:2px,color:#134e4a
    style tdp fill:#f8fafc,stroke:#475569,stroke-width:2px,color:#1e293b
    style xgb fill:#fafafa,stroke:#525252,stroke-width:2px,color:#000000