#!/usr/bin/env python3
import time, warnings, requests, os, json
import pandas as pd
# ECC data for Water in Your Boots? observation locations with SmartMet timeseries API
# Output csv files
# (IBA Arctic Wildfire Preparedness & Terrain trafficability)

iba_dir='/home/smartmet/copernicus/IBAML/'
ecc_dir='/home/smartmet/copernicus/IBAML/ecc/'

# Read in location information from observations
obs_file=os.path.join(iba_dir, 'iba_observations_2025_processed.csv') 
df_obs=pd.read_csv(obs_file, dtype={'latlon_id': str})

print(df_obs)

# Build dict: latlon_id -> (lat, lon) 
obsloc_dict = {}
for index, row in df_obs.iterrows():
    obsloc_dict[row['latlon_id']] = (row['latitude'], row['longitude'])

# build one comma-sep latlons string for ts query
user_coords_flat = [str(v) for pair in obsloc_dict.values() for v in pair]
latlons_param= ",".join(user_coords_flat)
# DEBUGGING with just a few locations
#latlons_param = ",".join(latlons_param.split(",")[:6])
#print(latlons_param)

# ecc static parameters
pardict = {
    'lake_cover':'CL-0TO1:ECC:5059:1:0:0', # lake cover
    'cvh':'CVH-N:ECC:5059:1:0:0', # high vegetation cover
    'cvl':'CVL-N:ECC:5059:1:0:0', # low vegetation cover 
    'lake_depth':'DL-M:ECC:5059:1:0:0', # lake total depth
    'land_cover':'LC-0TO1:ECC:5059:1:0:0', # land cover
    'soiltype':'SOILTY-N:ECC:5059:1:0:0', # soil type
    'urban_cover':'CUR-0TO1:ECC:5059:1:0:0', # urban cover fraction    
    'tvh':'TVH-N:ECC:5059:1:0:0', # type of high vegetation
    'tvl':'TVL-N:ECC:5059:1:0:0' # type of low vegetation
}

hour='00'
start='data' # static values have different dates for available data at smartmet server, data will fetch the available
end='data'

for pair in pardict.items():
    feat,fmikey=pair
    print(feat)
    q1 = (
        "http://smartmet.xyz:8080/timeseries"
        f"?latlons={latlons_param}" # use wkt MULTIPOINT in the future!!
        f"&param=time,latitude,longitude,{fmikey} as {feat}"
        f"&starttime={start}&endtime={end}"
        "&format=json&precision=full&timeformat=sql&origintime=20000101T000000"
        )
    #print(q1) # for "debugging" in browser
    response=requests.get(url=q1)
    results_json=json.loads(response.content)
    df1=pd.DataFrame(results_json)   

    # change time to be always 2025-01-01 12:00:00
    df1['time'] = '2025-01-01 12:00:00'
    df1['time'] = pd.to_datetime(df1['time'])
    # change latitude longitude type to str
    df1['latitude'] = df1['latitude'].astype(str)
    df1['longitude'] = df1['longitude'].astype(str)
    print(df1)
    # save to csv for each feat
    output_file = os.path.join(ecc_dir, f'ecc_{feat}_static_alllocs.csv')
    df1.to_csv(output_file, index=False)

# fetch ecc laihv lailv for 2020
laidict = {
    'laihv_ecc': 'LAI_HV-M2M2:ECC:5059:1:0:0',
    'lailv_ecc': 'LAI_LV-M2M2:ECC:5059:1:0:0'
}

for feat, fmikey in laidict.items():
    print(feat)
    q1 = (
        "http://smartmet.xyz:8080/timeseries"
        f"?latlons={latlons_param}" # use wkt MULTIPOINT in the future!!
        f"&param=utctime,latitude,longitude,{fmikey} as {feat}"
        f"&starttime=20200101T000000Z&endtime=20210101T000000Z&hour=0"
        "&format=json&precision=full&timeformat=sql&tz=utc&origintime=20000101T000000"
        )
    response=requests.get(url=q1)
    results_json=json.loads(response.content)
    df1=pd.DataFrame(results_json)   

    # change latitude longitude type to str to avoid precision issues when merging later
    df1['latitude'] = df1['latitude'].astype(str)
    df1['longitude'] = df1['longitude'].astype(str)
    print(df1)
    # save to csv for each feat
    output_file = os.path.join(ecc_dir, f'ecc_{feat}_2020_alllocs.csv')
    df1.to_csv(output_file, index=False)