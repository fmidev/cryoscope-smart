#!/usr/bin/env python3
import os, requests, json, time
import pandas as pd

# scrip to fetch era5 pressure level features for adjusted skt times
iba_dir='yourpath'
era5_dir='yourpath/era5/'

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

 
era5_pl_features = {
    't500': 'T-K:ERA5:5081:2:500:1:0', # 500hPa temperature
    't700': 'T-K:ERA5:5081:2:700:1:0', # 700hPa temperature
    't850': 'T-K:ERA5:5081:2:850:1:0', # 850hPa temperature
    't925': 'T-K:ERA5:5081:2:925:1:0', # 925hPa temperature
    'z500': 'Z-M2S2:ERA5:5081:2:500:1:0', # 500hPa geopotential height
    'z700': 'Z-M2S2:ERA5:5081:2:700:1:0', # 700hPa geopotential height
    'z850': 'Z-M2S2:ERA5:5081:2:850:1:0', # 850hPa geopotential height
    'z925': 'Z-M2S2:ERA5:5081:2:925:1:0', # 925hPa geopotential height
    'u500': 'U-MS:ERA5:5081:2:500:1:0', # 500hPa u wind component
    'u700': 'U-MS:ERA5:5081:2:700:1:0', # 700hPa u wind component
    'u850': 'U-MS:ERA5:5081:2:850:1:0', # 850hPa u wind component
    'u925': 'U-MS:ERA5:5081:2:925:1:0', # 925hPa u wind component
    'v500': 'V-MS:ERA5:5081:2:500:1:0', # 500hPa v wind component
    'v700': 'V-MS:ERA5:5081:2:700:1:0', # 700hPa v wind component
    'v850': 'V-MS:ERA5:5081:2:850:1:0',  # 850hPa v wind component
    'v925': 'V-MS:ERA5:5081:2:925:1:0',  # 925hPa v wind component
    'q500': 'Q-KGKG:ERA5:5081:2:500:1:0', # 500hPa specific humidity
    'q700': 'Q-KGKG:ERA5:5081:2:700:1:0', # 700hPa specific humidity
    'q850': 'Q-KGKG:ERA5:5081:2:850:1:0',  # 850hPa specific humidity
    'q925': 'Q-KGKG:ERA5:5081:2:925:1:0'  # 925hPa specific humidity
    }

# --- Timeseries query for INSTANT features --- #
hours_list = [f"{i:02d}" for i in range(24)] # all hours of day
hours=",".join(hours_list)

start='20250101T000000'
end='20251101T000000' 

# Time series query for instant features
for pair in era5_pl_features.items():
    feat,fmikey=pair
    print(feat)
    q1 = (
        "http://smartmet.xyz:8080/timeseries"
        f"?latlons={latlons_param}"
        f"&param=time,latitude,longitude,{fmikey}"
        f"&starttime={start}Z&endtime={end}Z&hour={hours}"
        "&format=json&precision=full&timeformat=sql"
        )
    print(q1) # for "debugging" in browser
    response=requests.get(url=q1)
    results_json=json.loads(response.content)
    df1=pd.DataFrame(results_json)   
    # change column names to feats
    df1.columns = ['time', 'latitude', 'longitude', feat]
    # add latlon_id column based on latitude and longitude matching obsloc_dict
    def get_latlon_id(row):
        lat = row['latitude']
        lon = row['longitude']
        for latlon_id, (user_lat, user_lon) in obsloc_dict.items():
            if lat == user_lat and lon == user_lon:
                return latlon_id
        return None

    df1['latlon_id'] = df1.apply(get_latlon_id, axis=1)
    print(df1)
    # save to csv for each latlon_id
    for latlon_id, df_group in df1.groupby('latlon_id'):
        output_file = os.path.join(era5_dir, f'era5_{feat}_2025_pressure_{latlon_id}.csv')
        df_group.to_csv(output_file, index=False)
