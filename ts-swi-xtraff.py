#!/usr/bin/env python3

import time, warnings, requests, os, json
import pandas as pd
import functions as fcts
warnings.simplefilter(action='ignore', category=FutureWarning)

# SWI data for Water in Your Boots? observation locations with SmartMet timeseries API
# Output csv files
# (IBA Arctic Wildfire Preparedness & Terrain trafficability)

iba_dir='/home/smartmet/copernicus/IBAML'
swis_dir='/home/smartmet/copernicus/IBAML/swis/'

#  Read in location information from observations
obs_file=os.path.join(iba_dir, 'iba_observations_2025_processed.csv')
df_obs=pd.read_csv(obs_file, dtype={'latlon_id': str})

print(df_obs)

# Build dict: latlon_id -> (lat, lon)
obsloc_dict = {}
for index, row in df_obs.iterrows():
    obsloc_dict[row['latlon_id']] = (row['latitude'], row['longitude'])

#  Loop through batches (to avoid too long URLs and server timeouts)
locations = list(obsloc_dict.values())   # list of (lat, lon) tuples
batch_size = 2000
n_batches = (len(locations) + batch_size - 1) // batch_size
print(f"Total {len(locations)} locations -> {n_batches} batches of up to {batch_size}")

#  SWI predictands
swis = {
    'swi1': 'interpolate_t(SWI1:SWI:5059:1:0:0/2d/2d)', # interpolation in time +- 2 days to fill in NaN values for missing data points
    'swi2': 'interpolate_t(SWI2:SWI:5059:1:0:0/2d/2d)',
    #'swi3': 'interpolate_t(SWI3:SWI:5059:1:0:0/2d/2d)',
    #'swi4': 'interpolate_t(SWI4:SWI:5059:1:0:0/2d/2d)',
}

start = '20250101T120000'
end   = '20251101T120000'

# Outer batch loop
for batch_idx in range(n_batches):
    batch_num = batch_idx + 1   # 1-indexed for filenames
    batch_locs = locations[batch_idx * batch_size : (batch_idx + 1) * batch_size]
    coords_flat = [str(v) for pair in batch_locs for v in pair]
    latlons_param = ",".join(coords_flat)

    print(f"\n=== Batch {batch_num}/{n_batches} ({len(batch_locs)} locations) ===")

    for feat, fmikey in swis.items():
        feat_dir = os.path.join(swis_dir, feat)
        os.makedirs(feat_dir, exist_ok=True)
        out = os.path.join(feat_dir, f'swis_{feat}_2025_all-{batch_num}.csv')
        if os.path.exists(out):
            print(f'  skipping (exists): {feat}')
            continue
        print(f'  fetching: {feat}')
        q1 = (
            "http://smartmet.xyz:8080/timeseries"
            f"?latlons={latlons_param}"
            f"&param=time,latitude,longitude,{fmikey} as {feat}"
            f"&starttime={start}Z&endtime={end}Z&hour=12"
            "&format=json&precision=full&timeformat=sql&origintime=20000101T000000"
        )
        response = requests.get(url=q1)
        df1 = pd.DataFrame(json.loads(response.content))
        df1.columns = ['time', 'latitude', 'longitude', feat]
        df1['latitude'] = df1['latitude'].astype(str)
        df1['longitude'] = df1['longitude'].astype(str)
        df1.to_csv(out, index=False)