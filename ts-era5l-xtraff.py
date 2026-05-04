#!/usr/bin/env python3

import os, requests, json
import pandas as pd

# IBA timseseries era5l fetch script
# ERA5L data for IBA observation locations
# remember to run this in screen session if not debugging

iba_dir='yourpath' # change names to your paths
era5l_dir='yourpath/era5l/'

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

# --- ERA5L instant features --- # 
# ml name : fmi-key 
era5l_features = {
    #'t2': 'T2-K:ERA5L:5078:1:0:1:0', # 2m temperature
    #'td2': 'TD2-K:ERA5L:5078:1:0:1:0', # 2m dewpoint temperature
    #'laihv': 'LAI_HV-M2M2:ERA5L:5078:1:0:1:0', # leaf area incease high vegetation
    #'lailv': 'LAI_LV-M2M2:ERA5L:5078:1:0:1:0', # leaf area incease low vegetation
    #'sp': 'PGR-PA:ERA5L:5078:1:0:1:0', # surface pressure
    #'sd': 'SD-M:ERA5L:5078:1:0:1:0', # snow depth m of water equivalent ## fill
    #'rsn': 'SND-KGM3:ERA5L:5078:1:0:1:0', # snow density ## fill
    #'swvl1': 'SOILWET-M3M3:ERA5L:5078:9:7:1:0', # volumetric soil water layer 1 ## fill
    #'swvl2': 'SWVL2-M3M3:ERA5L:5078:9:1820:1:0', # volumetric soil water layer 2 ## fill
    #'swvl3': 'SWVL3-M3M3:ERA5L:5078:9:7268:1:0', # volumetric soil water layer 3 ## fill
    #'swvl4': 'SWVL4-M3M3:ERA5L:5078:9:25855:1:0', # volumetric soil water layer 4 ## fill
    #'stl1': 'STL1-K:ERA5L:5078:9:7:1:0', # soil temperature layer 1
    #'u10': 'U10-MS:ERA5L:5078:1:0:1:0', # 10m u wind component
    #'v10': 'V10-MS:ERA5L:5078:1:0:1:0' # 10m v wind component
}

# --- ERA5L 24h aggregated features (daily at hour 00) --- #
era5l_24h_features = {
    #'tp': 'RR-M:ERA5L:5078:1:0:1:0', # total precipitation
    #'e': 'EVAP-M:ERA5L:5078:1:0:1:0', # evaporation
    #'sf': 'SNACC-KGM2:ERA5L:5078:1:0:1:0', # snow fall ## fill
    #'ro': 'RO-M:ERA5L:5078:1:0:1:0', # runoff
    #'ssro': 'SSRO-M:ERA5L:5078:1:0:1:0', # subsurface runoff
    #'sshf': 'FLSEN-JM2:ERA5L:5078:1:0:1:0', # surface sensible heat flux
    #'ssr': 'RNETSWA-JM2:ERA5L:5078:1:0:1:0', # surface net solar radiation
    #'str': 'RNETLWA-JM2:ERA5L:5078:1:0:1:0', # surface net thermal radiation
    #'slhf': 'FLLAT-JM2:ERA5L:5078:1:0:1:0',   # surface latent heat flux
    #'ssrd': 'RADGLOA-JM2:ERA5L:5078:1:0:1:0', # surface solar radiation downwards
    #'strd': 'RADLWA-JM2:ERA5L:5078:1:0:1:0', # surface thermal radiation downwards

    'aslr': 'ALBEDOSLR-0TO1:ERA5L:5078:1:0:1', # albedo with solar angle correction
    'asn': 'ASN-0TO1:ERA5L:5073:1:0:1:0', # snow albedo
    'es': 'ES-M:ERA5L:5073:1:0:1:0', # snow evaporation
    'ebs': 'EVABS-M:ERA5L:5073:1:0:0', # evaporation from bare soil
    'eow': 'EVAOW-M:ERA5L:5073:1:0:0', # evaporation from open water excluding oceans
    'ep': 'EVAPP-M:ERA5L:5073:1:0:1:0', # potential evaporation
    'etc': 'EVATC-M:ERA5L:5073:1:0:0', # evaporation from the top of canopy
    'evt': 'EVAVT-M:ERA5L:5073:1:0:0', # evaporation from vegetation transpiration
    'lsf': 'LSHF:ERA5L:5073:1:0:1:0', # lake shape factor
    'st': 'SKT-K:ERA5L:5073:1:0:1', # skin temperature
    'sm': 'SMLT-M:ERA5L:5073:1:0:1:0', # snowmelt
    'sfa': 'SNACC-KGM2:ERA5L:5073:1:0:1:0', # snowfall accumulation
    'sro': 'SRO-M:ERA5L:5078:1:0:1:0', # surface runoff
    'st2': 'STL2-K:ERA5L:5073:9:1820:1', # soil temperature level 2 in kelvins
    'st3': 'STL3-K:ERA5L:5073:9:7268:1', # soil temperature level 3 in kelvins
    'st4': 'STL4-K:ERA5L:5073:9:25600:1', # soil temperature level 4 in kelvins
    'src': 'SRC-M:ERA5L:5073:1:0:1:0' # skin reservoir content
}

# --- ERA5LD 24h aggregated features (daily at hour 00) --- #
# remember to use origintime=20250101T000000Z for era5ld features in ts queries
# data on smartmet duplicate tmax, tmin needs to be fixed
era5ld_features = {
    #'tmax':'TMAX-24-K:ERA5LD:5022:1:0:1', # maximum temperature
    #'tmin':'TMIN-24-K:ERA5LD:5022:1:0:1', # minimum temperature
}

# --- Timeseries query for INSTANT features --- #
hours_list = [f"{i:02d}" for i in range(24)] # all hours of day
hours=",".join(hours_list)

start='20250101T000000'
end='20251101T000000' 

# Time series query for instant features
for pair in era5l_features.items():
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
        output_file = os.path.join(era5l_dir, f'era5l_{feat}_2025_instant_{latlon_id}.csv')
        df_group.to_csv(output_file, index=False)

# Time series query for 24h features
for pair in era5l_24h_features.items():
    feat,fmikey=pair
    print(feat)
    q1 = (
        "http://smartmet.xyz:8080/timeseries"
        f"?latlons={latlons_param}"
        f"&param=time,latitude,longitude,{fmikey}"
        f"&starttime={start}Z&endtime={end}Z&hour=00"
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
        output_file = os.path.join(era5l_dir, f'era5l_{feat}_2025_24hagg_{latlon_id}.csv')
        df_group.to_csv(output_file, index=False)
