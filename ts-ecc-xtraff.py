#!/usr/bin/env python3

import time, warnings, requests, os, json
import pandas as pd
warnings.simplefilter(action='ignore', category=FutureWarning)
### SmarMet-server timeseries query to fetch static ECC parameters to training data for machine learning

iba_dir='yourpath'
ecc_dir='yourpath/ecc/'

# --- Read in location information from observations --- # 
obs_file=os.path.join(iba_dir, 'ibahavainnot_processed.csv')
# read latlon_id as string to preserve leading zeros
df_obs=pd.read_csv(obs_file, dtype={'latlon_id': str})

# ml area is 83N to 25S to -30W to 50E (ERA5L data available), drop latlon outside this area
df_obs = df_obs[(df_obs['latitude'] <= 83) & (df_obs['latitude'] >= -25) &
                (df_obs['longitude'] >= -30) & (df_obs['longitude'] <= 50)]
print(df_obs)

# make a dictionary where latlon_id is key and (user_latitude, user_longitude) is value but if user_latitude or user_longitude is nan, then use latitude, longitude instead
obsloc_dict = {}
for index, row in df_obs.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    user_lat = row['user_latitude']
    user_lon = row['user_longitude']
    if pd.isna(user_lat) or pd.isna(user_lon):
        obsloc_dict[row['latlon_id']] = (lat, lon)
    else:
        obsloc_dict[row['latlon_id']] = (user_lat, user_lon)

# build one comma-sep latlons string for ts query
user_coords_flat = [str(v) for pair in obsloc_dict.values() for v in pair]
latlons_param= ",".join(user_coords_flat)
# DEBUGGING with one location: create str until second , in latlons_param for user latlons
#latlons_param = ",".join(latlons_param.split(",")[:6])
#print(latlons_param)

### ecc parameters
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

source='smartmet.xyz:8080'
hour='00'
start='data' # static values have different dates for available data at smartmet-desm
end='data'

for pair in pardict.items():
    feat,fmikey=pair
    print(feat)
    q1 = (
        "http://smartmet.xyz:8080/timeseries"
        f"?latlons={latlons_param}"
        f"&param=time,latitude,longitude,{fmikey} as {feat}"
        f"&starttime={start}&endtime={end}"
        "&format=json&precision=full&timeformat=sql"
        )
    #print(q1) # for "debugging" in browser
    response=requests.get(url=q1)
    results_json=json.loads(response.content)
    df1=pd.DataFrame(results_json)   
    # add latlon_id column based on latitude and longitude matching obsloc_dict
    def get_latlon_id(row):
        lat = row['latitude']
        lon = row['longitude']
        for latlon_id, (user_lat, user_lon) in obsloc_dict.items():
            if lat == user_lat and lon == user_lon:
                return latlon_id
        return None

    df1['latlon_id'] = df1.apply(get_latlon_id, axis=1)
    # change time to be always 2025-01-01 12:00:00
    df1['time'] = '2025-01-01 12:00:00'
    df1['time'] = pd.to_datetime(df1['time'])
    print(df1)
    # save to csv for each feat
    output_file = os.path.join(ecc_dir, f'ecc_{feat}_static_alllocs.csv')
    df1.to_csv(output_file, index=False)

    #for latlon_id, df_group in df1.groupby('latlon_id'):
    #    output_file = os.path.join(iba_dir, f'ecc_{feat}_static_{latlon_id}.csv')
    #    df_group.to_csv(output_file, index=False)
