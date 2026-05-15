#!/usr/bin/env python3
import os, requests, json
import pandas as pd
import numpy as np
from urllib.parse import quote_plus

# ERA5L data for Water in Your Boots? observation locations with SmartMet timeseries API
# Output csv files
# (IBA Arctic Wildfire Preparedness & Terrain trafficability)

iba_dir='/home/smartmet/copernicus/IBAML'
era5l_dir='/home/smartmet/copernicus/IBAML/era5l/mlsmart/'

source='http://ml.harvesterseasons.com:8080' # testing fetching from another SmarMet server with similar setup to smartmet.xyz

def parse_array_string(s):
    # Convert SmartMet's '[41.82 41.83 ...]' string into a list of floats.
    if not isinstance(s, str):
        return s
    s = s.strip()
    if s.startswith('['):
        s = s[1:]
    if s.endswith(']'):
        s = s[:-1]
    out = []
    for tok in s.split():
        try:
            out.append(float(tok))
        except ValueError:
            out.append(np.nan)
    return out


def explode_response(df1, feat):
    # Parse the three list-like columns from strings to lists, then explode.
    for col in ('latitude', 'longitude', feat):
        df1[col] = df1[col].apply(parse_array_string)
    df1 = df1.explode(['latitude', 'longitude', feat], ignore_index=True)
    df1['latitude'] = df1['latitude'].astype(str)
    df1['longitude'] = df1['longitude'].astype(str)
    return df1

# Read in location information from observations 
obs_file=os.path.join(iba_dir, 'iba_observations_2025_processed.csv') 
df_obs=pd.read_csv(obs_file, dtype={'latlon_id': str})

# Build dict: latlon_id -> (lat, lon)
obsloc_dict = {}
for index, row in df_obs.iterrows():
    obsloc_dict[row['latlon_id']] = (row['latitude'], row['longitude'])

# Batching setup (to avoid too long URLs and server timeouts)
locations = list(obsloc_dict.values())   # list of (lat, lon) tuples
batch_size = 2000
n_batches = (len(locations) + batch_size - 1) // batch_size
print(f"Total {len(locations)} locations -> {n_batches} batches of up to {batch_size}")

# ERA5L instant features
era5l_features = {
    't2': 'T2-K:ERA5L:5078:1:0:1:0',
    'td2': 'TD2-K:ERA5L:5078:1:0:1:0',
    'laihv_era5l': 'LAI_HV-M2M2:ERA5L:5078:1:0:1:0',
    'lailv_era5l': 'LAI_LV-M2M2:ERA5L:5078:1:0:1:0',
    'sp': 'PGR-PA:ERA5L:5078:1:0:1:0',
    'sd': 'SD-M:ERA5L:5078:1:0:1:0',
    'rsn': 'SND-KGM3:ERA5L:5078:1:0:1:0',
    'swvl1': 'SOILWET-M3M3:ERA5L:5078:9:7:1:0',
    'swvl2': 'SWVL2-M3M3:ERA5L:5078:9:1820:1:0',
    'swvl3': 'SWVL3-M3M3:ERA5L:5078:9:7268:1:0',
    #'swvl4': 'SWVL4-M3M3:ERA5L:5078:9:25855:1:0',
    'stl1': 'STL1-K:ERA5L:5078:9:7:1:0',
    'stl2': 'TSOIL-K:ERA5L:5078:9:1820:1:0',
    #'stl3': 'STL3-K:ERA5L:5078:9:7268:1:0',
    #'stl4': 'STL4-K:ERA5L:5078:9:25855:1:0',
    'u10': 'U10-MS:ERA5L:5078:1:0:1:0',
    'v10': 'V10-MS:ERA5L:5078:1:0:1:0',
    'skt': 'SKT-K:ERA5L:5078:1:0:1:0',
    'src': 'SRC-M:ERA5L:5078:1:0:1:0',
}

# ERA5L 24h aggregated features (daily at hour 00)
era5l_24h_features = {
    'tp': 'RR-M:ERA5L:5078:1:0:1:0',
    'e': 'EVAP-M:ERA5L:5078:1:0:1:0',
    'ep': 'EVAPP-M:ERA5L:5078:1:0:1:0',
    'sf': 'SNACC-KGM2:ERA5L:5078:1:0:1:0',
    'ro': 'RO-M:ERA5L:5078:1:0:1:0',
    'sro': 'SRO-M:ERA5L:5078:1:0:1:0',
    'ssro': 'SSRO-M:ERA5L:5078:1:0:1:0',
    'sshf': 'FLSEN-JM2:ERA5L:5078:1:0:1:0',
    'ssr': 'RNETSWA-JM2:ERA5L:5078:1:0:1:0',
    'str': 'RNETLWA-JM2:ERA5L:5078:1:0:1:0',
    'slhf': 'FLLAT-JM2:ERA5L:5078:1:0:1:0',
    'ssrd': 'RADGLOA-JM2:ERA5L:5078:1:0:1:0',
    'strd': 'RADLWA-JM2:ERA5L:5078:1:0:1:0',
}

# ERA5LD 24h aggregated features
era5ld_tmax = {'t24max': 'T2-K:ERA5LD:5078:1:0:1'}
era5ld_tmin = {'t24min': 'T2-K:ERA5LD:5078:1:0:1'}

# Instant features for all hours of day (to be merged later to closest observation hour)
hours_list = [f"{i:02d}" for i in range(24)]
hours = ",".join(hours_list)

start_inst='20250101T000000'
end_inst='20251101T000000'

start_d='20250101T113000'
end_d='20251101T000000'

# Loop through batches
for batch_idx in range(n_batches):
    batch_num = batch_idx + 1   # 1-indexed for filenames
    batch_locs = locations[batch_idx * batch_size : (batch_idx + 1) * batch_size]

    wkt_raw = "MULTIPOINT(" + ",".join(f"{lon} {lat}" for lat, lon in batch_locs) + ")"
    wkt_param = quote_plus(wkt_raw)

    print(f"\n=== Batch {batch_num}/{n_batches} ({len(batch_locs)} locations) ===")

    # Instant features
    for feat, fmikey in era5l_features.items():
        out = os.path.join(era5l_dir, f'era5l_{feat}_2025_all-{batch_num}.csv')
        if os.path.exists(out):
            print(f'  skipping (exists): {feat}')
            continue
        print(f'  fetching instant: {feat}')
        q1 = (
            f"{source}/timeseries"
            f"?wkt={wkt_param}"
            f"&param=time,latitude,longitude,{fmikey}"
            f"&starttime={start_inst}Z&endtime={end_inst}Z&hour={hours}"
            "&format=json&precision=full&timeformat=sql"
        )
        response = requests.get(url=q1)
        df1 = pd.DataFrame(json.loads(response.content))
        df1.columns = ['time', 'latitude', 'longitude', feat]
        df1 = explode_response(df1, feat)
        print(df1.dropna())
        df1.to_csv(out, index=False)

    # 24h aggregated features
    for feat, fmikey in era5l_24h_features.items():
        out = os.path.join(era5l_dir, f'era5l_{feat}_2025_24hagg_all-{batch_num}.csv')
        if os.path.exists(out):
            print(f'  skipping (exists): {feat}')
            continue
        print(f'  fetching 24h: {feat}')
        q1 = (
            f"{source}/timeseries"
            f"?wkt={wkt_param}"
            f"&param=utctime,latitude,longitude,{fmikey}" # utctime to get daily aggregates
            f"&starttime={start_inst}Z&endtime={end_inst}Z&hour=00"
            "&format=json&precision=full&timeformat=sql&tz=utc"
        )
        response = requests.get(url=q1)
        df1 = pd.DataFrame(json.loads(response.content))
        df1.columns = ['time', 'latitude', 'longitude', feat]
        df1 = explode_response(df1, feat)
        print(df1.dropna())
        df1.to_csv(out, index=False)

    source='http://smartmet.xyz:8080' # ERA5LD data only from smartmet.xyz
    # ERA5LD daily max and min features are separated by origintime parameter in queries!
    # ERA5LD daily max
    for feat, fmikey in era5ld_tmax.items():
        out = os.path.join(era5l_dir, f'era5l_{feat}_2025_24hagg_all-{batch_num}.csv')
        if os.path.exists(out):
            print(f'  skipping (exists): {feat}')
            continue
        print(f'  fetching tmax: {feat}')
        q1 = (
            f"{source}/timeseries"
            f"?wkt={wkt_param}"
            f"&param=utctime,latitude,longitude,{fmikey}"
            f"&starttime={start_d}Z&endtime={end_d}Z&hour=12"
            "&format=json&precision=full&timeformat=sql&tz=utc&origintime=20000101T000000"
        )
        response = requests.get(url=q1)
        df1 = pd.DataFrame(json.loads(response.content))
        df1.columns = ['time', 'latitude', 'longitude', feat]
        df1 = explode_response(df1, feat)
        print(df1.dropna())
        df1.to_csv(out, index=False)

    # ERA5LD daily min
    for feat, fmikey in era5ld_tmin.items():
        out = os.path.join(era5l_dir, f'era5l_{feat}_2025_24hagg_all-{batch_num}.csv')
        if os.path.exists(out):
            print(f'  skipping (exists): {feat}')
            continue
        print(f'  fetching tmin: {feat}')
        q1 = (
            f"{source}/timeseries"
            f"?wkt={wkt_param}"
            f"&param=utctime,latitude,longitude,{fmikey}"
            f"&starttime={start_d}Z&endtime={end_d}Z&hour=12"
            "&format=json&precision=full&timeformat=sql&tz=utc&origintime=20000201T000000"
        )
        response = requests.get(url=q1)
        df1 = pd.DataFrame(json.loads(response.content))
        df1.columns = ['time', 'latitude', 'longitude', feat]
        df1 = explode_response(df1, feat)
        print(df1.dropna())
        df1.to_csv(out, index=False)