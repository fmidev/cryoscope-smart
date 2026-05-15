#!/usr/bin/env python3
import os, requests, json
import pandas as pd

# ERA5 data for Water in Your Boots? observation locations with SmartMet timeseries API
# Output csv files
# (IBA Arctic Wildfire Preparedness & Terrain trafficability)

iba_dir='/home/smartmet/copernicus/IBAML'
era5_dir='/home/smartmet/copernicus/IBAML/era5/'

# Read in location information from observations
obs_file=os.path.join(iba_dir, 'iba_observations_2025_processed.csv') 
df_obs=pd.read_csv(obs_file, dtype={'latlon_id': str})

# Build dict: latlon_id -> (lat, lon) 
obsloc_dict = {}
for index, row in df_obs.iterrows():
    obsloc_dict[row['latlon_id']] = (row['latitude'], row['longitude'])

# Batching setup (fetch locations in batches to avoid too long URLs and server timeouts)
locations = list(obsloc_dict.values())   # list of (lat, lon) tuples
batch_size = 2000 # This already contains all IBA locations
n_batches = (len(locations) + batch_size - 1) // batch_size
print(f"Total {len(locations)} locations -> {n_batches} batches of up to {batch_size}")

# ERA5 pressure-level features
era5_features = {
    #'t500': 'T-K:ERA5:5081:2:500:1:0', # Temperature
    't700': 'T-K:ERA5:5081:2:700:1:0',
    't850': 'T-K:ERA5:5081:2:850:1:0',
    't925': 'T-K:ERA5:5081:2:925:1:0',
    #'z500': 'Z-M2S2:ERA5:5081:2:500:1:0', # Geopotential
    'z700': 'Z-M2S2:ERA5:5081:2:700:1:0',
    'z850': 'Z-M2S2:ERA5:5081:2:850:1:0',
    'z925': 'Z-M2S2:ERA5:5081:2:925:1:0',
    #'u500': 'U-MS:ERA5:5081:2:500:1:0', # U component of wind
    'u700': 'U-MS:ERA5:5081:2:700:1:0',
    'u850': 'U-MS:ERA5:5081:2:850:1:0',
    'u925': 'U-MS:ERA5:5081:2:925:1:0',
    #'v500': 'V-MS:ERA5:5081:2:500:1:0', # V component of wind
    'v700': 'V-MS:ERA5:5081:2:700:1:0',
    'v850': 'V-MS:ERA5:5081:2:850:1:0',
    'v925': 'V-MS:ERA5:5081:2:925:1:0',
    #'q500': 'Q-KGKG:ERA5:5081:2:500:1:0', # Specific humidity
    'q700': 'Q-KGKG:ERA5:5081:2:700:1:0',
    'q850': 'Q-KGKG:ERA5:5081:2:850:1:0',
    'q925': 'Q-KGKG:ERA5:5081:2:925:1:0',
}

# Easiest to fetch all hours of day and merge later to closest observation hour
hours_list = [f"{i:02d}" for i in range(24)]
hours = ",".join(hours_list)

start = '20250101T000000' # Observation campaign started March 2025 so could be adjusted
end   = '20251101T000000' # Campaign run until October 2025

# Loop through batches
for batch_idx in range(n_batches):
    batch_num = batch_idx + 1   # 1-indexed for filenames
    batch_locs = locations[batch_idx * batch_size : (batch_idx + 1) * batch_size]
    coords_flat = [str(v) for pair in batch_locs for v in pair]
    latlons_param = ",".join(coords_flat)

    print(f"\n=== Batch {batch_num}/{n_batches} ({len(batch_locs)} locations) ===")

    # Timeseries queries per feature
    for feat, fmikey in era5_features.items():
        out = os.path.join(era5_dir, f'era5_{feat}_2025_all-{batch_num}.csv')
        if os.path.exists(out):
            print(f'  skipping (exists): {feat}')
            continue
        print(f'  fetching: {feat}')
        q1 = (
            "http://smartmet.xyz:8080/timeseries"
            f"?latlons={latlons_param}" # better to use wkt MULTIPOINT in the future!!
            f"&param=time,latitude,longitude,{fmikey}"
            f"&starttime={start}Z&endtime={end}Z&hour={hours}"
            "&format=json&precision=full&timeformat=sql"
        )
        response = requests.get(url=q1)
        df1 = pd.DataFrame(json.loads(response.content))
        df1.columns = ['time', 'latitude', 'longitude', feat]
        df1['latitude'] = df1['latitude'].astype(str) # later merge on latitude and longitude as strings to avoid precision issues
        df1['longitude'] = df1['longitude'].astype(str)
        df1.to_csv(out, index=False) # save output for each feature and batch