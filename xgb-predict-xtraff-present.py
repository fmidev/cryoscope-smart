import xarray as xr
import time, sys
import numpy as np
import xgboost as xgb
import warnings
import pandas as pd

# Soil moisture class prediction with XGBoost for EC-ENS present model (ECXENS) 300m grid
# Run with: ./get-ec-ens.sh year month day
# (AK 2026)

warnings.filterwarnings("ignore")

path = '/home/users/smartmet/data/'

# Load model
mod_dir = f'{path}ML/models/'
mod_name = 'xgb_iba_soilmoistureclass_model_xgb-soilmoistureclass_FINALMODEL.json'
fitted_mdl = xgb.XGBClassifier()
fitted_mdl.load_model(mod_dir + mod_name)

feats = fitted_mdl.get_booster().feature_names
print(feats)

# Input files and output file
sfc = sys.argv[1]            # sfc+sde file (300m)
disacc = sys.argv[2]         # disaccumulated file (300m)
pl = sys.argv[3]             # pressure level file (300m)
laihv_file = sys.argv[4]     # laihv (300m)
lailv_file = sys.argv[5]     # lailv (300m)
swis_file = sys.argv[6]      # actual swi1 and swi2 satellite obs (300m)
soilgrids_file = sys.argv[7] # soilgrids (300m)
ecc_file = sys.argv[8]       # all ECC variables in one file (300m)
twi_file = sys.argv[9]       # topographic wetness index (300m)
oceanmask_file = sys.argv[10] # ocean mask
height = sys.argv[11]        # DTM height (300m)
aspect = sys.argv[12]        # DTM aspect (300m)
slope = sys.argv[13]         # DTM slope (300m)
tri_file = sys.argv[14]      # DTM TRI (300m)
output = sys.argv[15]        # output nc file

# Load datasets 

# sfc+sde surface variables: 2t, 2d, rsn, sd, sde, sp, u10, v10
sfc_rename = {'d2m': 'td2', 't2m': 't2', 'rsn': 'rsn', 'sd': 'sd', 'sde': 'sde',
              'sp': 'sp', 'u10': 'u10', 'v10': 'v10'}
sfc_ds = xr.open_dataset(sfc, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': '',
                    'filter_by_keys': {'typeOfLevel': 'surface'}}
)[sfc_rename.keys()].rename_vars(sfc_rename)

# sfc depth below land variables: stl1, swvl1, swvl2, swvl3
stl1_ds = xr.open_dataset(sfc, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': '',
                    'filter_by_keys': {'shortName': 'stl1'}})
swvl1_ds = xr.open_dataset(sfc, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': '',
                    'filter_by_keys': {'shortName': 'swvl1'}})
swvl2_ds = xr.open_dataset(sfc, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': '',
                    'filter_by_keys': {'shortName': 'swvl2'}})
swvl3_ds = xr.open_dataset(sfc, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': '',
                    'filter_by_keys': {'shortName': 'swvl3'}})

# disaccumulated variables: e, tp, slhf, sshf, ro, sro, ssro, str, strd, ssr, ssrd, sf
disacc_ds = xr.open_dataset(disacc, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': '',
                    'filter_by_keys': {'typeOfLevel': 'surface'}})

# pressure level variables: t, u, v, z, q at 700, 850, 925 hPa
pl700_rename = {'t': 't700', 'u': 'u700', 'v': 'v700', 'z': 'z700', 'q': 'q700'}
pl700_ds = xr.open_dataset(pl, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': '',
                    'filter_by_keys': {'level': 700}}).rename_vars(pl700_rename)
pl850_rename = {'t': 't850', 'u': 'u850', 'v': 'v850', 'z': 'z850', 'q': 'q850'}
pl850_ds = xr.open_dataset(pl, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': '',
                    'filter_by_keys': {'level': 850}}).rename_vars(pl850_rename)
pl925_rename = {'t': 't925', 'u': 'u925', 'v': 'v925', 'z': 'z925', 'q': 'q925'}
pl925_ds = xr.open_dataset(pl, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': '',
                    'filter_by_keys': {'level': 925}}).rename_vars(pl925_rename)

# laihv
laihv_ds = xr.open_dataset(laihv_file, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': ''}
).rename_vars({'lai_hv': 'laihv'})

# lailv
lailv_ds = xr.open_dataset(lailv_file, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': ''}
).rename_vars({'lai_lv': 'lailv'})

# swi2
swi2_ds = xr.open_dataset(swis_file, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': '',
                    'filter_by_keys': {'shortName': 'swi2'}})
# swi1
swi1_ds = xr.open_dataset(swis_file, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': '',
                    'filter_by_keys': {'shortName': 'swi1'}})

# soilgrids: clay, sand, silt, soc at 0-5, 5-15, 15-30 cm
namesSG5 = {'scfr': 'clay_0-5cm', 'ssfr': 'sand_0-5cm', 'soilp': 'silt_0-5cm', 'stf': 'soc_0-5cm'}
namesSG15 = {'scfr': 'clay_5-15cm', 'ssfr': 'sand_5-15cm', 'soilp': 'silt_5-15cm', 'stf': 'soc_5-15cm'}
namesSG30 = {'scfr': 'clay_15-30cm', 'ssfr': 'sand_15-30cm', 'soilp': 'silt_15-30cm', 'stf': 'soc_15-30cm'}
soilg_ds = xr.open_dataset(soilgrids_file, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': ''})
soilg_ds5 = soilg_ds.where((soilg_ds.depthBelowLand <= 0.10), drop=True
    ).rename_vars(namesSG5).squeeze(["depthBelowLand"], drop=True)
soilg_ds15 = soilg_ds.where((soilg_ds.depthBelowLand <= 0.20) & (soilg_ds.depthBelowLand >= 0.10), drop=True
    ).rename_vars(namesSG15).squeeze(["depthBelowLand"], drop=True)
soilg_ds30 = soilg_ds.where((soilg_ds.depthBelowLand <= 0.40) & (soilg_ds.depthBelowLand >= 0.20), drop=True
    ).rename_vars(namesSG30).squeeze(["depthBelowLand"], drop=True)

# ECC — all variables in one combined file (300m)
namesECC = {'cl': 'lake_cover', 'vegdiff': 'urban_cover', 'dl': 'lake_depth',
              'lsm': 'land_cover', 'slt': 'soiltype'}
ecc_ds = xr.open_dataset(ecc_file, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': ''}
).rename_vars(namesECC)

# TWI
twi_ds = xr.open_dataset(twi_file, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': ''}
).rename_vars({'swit': 'twi'})

# DTM height, aspect, slope
height_ds = xr.open_dataset(height, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': ''}
).rename_vars({'h': 'dtmheight'})
aspect_ds = xr.open_dataset(aspect, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': ''}
).rename_vars({'anor': 'dtmaspect'})
slope_ds = xr.open_dataset(slope, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': ''}
).rename_vars({'slor': 'dtmslope'})

# TRI
tri_ds = xr.open_dataset(tri_file, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': ''}
).rename_vars({'sdordiff': 'tri'})

# Ocean mask — ERA5-Land temperature field, NaN over ocean
oceanmask_ds = xr.open_dataset(oceanmask_file, engine='cfgrib',
    backend_kwargs={'time_dims': ('valid_time', 'verifying_time'), 'indexpath': ''})
# Rename 
omask_varname = list(oceanmask_ds.data_vars)[0]
oceanmask_ds = oceanmask_ds.rename_vars({omask_varname: 'oceanmask'})

# --- Merge all datasets ---
ds = xr.merge([
    sfc_ds, stl1_ds, swvl1_ds, swvl2_ds, swvl3_ds,
    disacc_ds,
    pl700_ds, pl850_ds, pl925_ds,
    laihv_ds, lailv_ds, swi1_ds, swi2_ds,
    soilg_ds5, soilg_ds15, soilg_ds30,
    ecc_ds,
    twi_ds,
    tri_ds,
    height_ds, aspect_ds, slope_ds,
    oceanmask_ds
], compat='override')

df = ds.to_dataframe().reset_index()

df['closest_hour'] = df.valid_time.dt.hour
df['accuracy_own'] = 1

# Store grid for final result
df_grid = df[['valid_time', 'latitude', 'longitude']]
df_grid['swi1'] = np.nan
df_grid = df_grid.set_index(['valid_time', 'latitude', 'longitude'])

# Apply ocean mask: drop ocean points (NaN in oceanmask temperature field)
df = df.dropna(subset='oceanmask')
df = df.drop(columns=['oceanmask'])

#print(df)
df_result = df[['valid_time', 'latitude', 'longitude']]

# Reorder columns to match model input
df = df[feats]

# Predict soil moisture class with XGBoost
prediction = fitted_mdl.predict(df)

df_result['swi1'] = prediction.tolist()
# Map class to percentage to match SWI1 definition
# Very dry: 0 -> 10%, Dry: 1 -> 25%, Moist: 2 -> 50%, Wet: 3 -> 75%, Extremely wet: 4 -> 90%
df_result['swi1'] = df_result['swi1'].replace({0: 10, 1: 25, 2: 50, 3: 75, 4: 90})
df_result.set_index(['valid_time', 'latitude', 'longitude'], inplace=True)

result_fin = df_grid.fillna(df_result)

ds = result_fin.to_xarray()
nc = ds.to_netcdf(output)

print(result_fin)
print(result_fin.dropna())