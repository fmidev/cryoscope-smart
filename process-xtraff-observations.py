#!/usr/bin/env python3
import json
import os
import pandas as pd

iba_dir='/home/smartmet/copernicus/IBAML'
era5l_dir='/home/smartmet/copernicus/IBAML/era5l/'

# Open the JSON file
with open(os.path.join(iba_dir, "ibahavainnot.json"), "r", encoding="utf-8") as file:
    data = json.load(file)

# Create a DataFrame with only selected fields
df = pd.DataFrame([
    {
        "latitude": item["geoLocation"][1],
        "longitude": item["geoLocation"][0],
        "user_latitude": item["userGeoLocation"][1],
        "user_longitude": item["userGeoLocation"][0],
        "accuracy": item["geoLocationAccuracy"],
        "time": item["createdAt"],
        "certainty": item["certainty"],
        "answer": item["answer"]
    }
    for item in data
])

# make new columns LAT,LON that use user_latitude and user_longitude if they are not nan, otherwise use latitude and longitude
df['LAT'] = df.apply(lambda row: row['user_latitude'] if not pd.isna(row['user_latitude']) else row['latitude'], axis=1)
df['LON'] = df.apply(lambda row: row['user_longitude'] if not pd.isna(row['user_longitude']) else row['longitude'], axis=1)

print(df[['LAT','LON','latitude','longitude','user_latitude','user_longitude','time','answer']])

# ml area is 83N to 25S to -30W to 50E (ERA5L data available), drop latlon outside this area
df = df[(df['LAT'] <= 83) & (df['LAT'] >= -25) &
                (df['LON'] >= -30) & (df['LON'] <= 50)]
print(df)

# add unique id for each lat lon pair such as 000001 000002 etc and order by it and reset index
df['latlon_id'] = df.groupby(['LAT', 'LON']).ngroup().apply(lambda x: f"{x+1:06d}")
df.sort_values(['latlon_id'], inplace=True)
df.reset_index(drop=True, inplace=True)

# change values Erittäin märkä -> Extremely wet, Märkä -> Wet, Kostea -> Moist, Kuiva -> Dry, Erittäin kuiva -> Very dry
df['answer'] = df['answer'].replace({
    "Erittäin märkä": "Extremely wet",
    "Märkä": "Wet",
    "Kostea": "Moist",
    "Kuiva": "Dry",
    "Erittäin kuiva": "Very dry"
})

# Change values for certainty ['Varma' 'Certain' 'Fairly certain' 'Uncertain' 'Melko varma' 'Epävarma']
#print(df['certainty'].unique())
df['certainty'] = df['certainty'].replace({
    "Melko varma": "Fairly certain",
    "Epävarma": "Uncertain",
    "Varma": "Certain"
})

# from time column extract date and closest_hour
df['date'] = pd.to_datetime(df['time']).dt.date
#df_era5l['closest_hour'] = pd.to_datetime(df_era5l['time']).dt.hour

# create new datetime with only date and hours minutes in time 

df['datetime'] = pd.to_datetime(df['time']).dt.round('h')
df['closest_hour'] = pd.to_datetime(df['datetime']).dt.hour
df['closest_hour'] = df['closest_hour'].astype(int)
# drop datetime column
df.drop(columns=['datetime'], inplace=True)

# add a column 'accuracy_own' where if user_lat or user_lon is NOT nan, then accuracy is 1 else accuracy is accyracy column value for that row
df['accuracy_own'] = df.apply(lambda row: 1 if not pd.isna(row['user_latitude']) and not pd.isna(row['user_longitude']) else row['accuracy'], axis=1)
#df['accuracy_own'] = df.apply(lambda row: 1 if pd.isna(row['user_latitude']) or pd.isna(row['user_longitude']) else row['accuracy'], axis=1) # old version but I think I thought it wrong way first
# print smallest accuracy value
print("Smallest accuracy:", df['accuracy'].min())

drop_cols=['latitude', 'longitude', 'user_latitude', 'user_longitude','accuracy']
df.drop(columns=drop_cols, inplace=True)
rename_cols={'LAT': 'latitude', 'LON': 'longitude'}
df.rename(columns=rename_cols, inplace=True)

reorder_cols=['time',  'latitude', 'longitude', 'latlon_id','answer','certainty','date', 'closest_hour', 'accuracy_own']
df=df[reorder_cols]
# change latitude longitude to str
df['latitude'] = df['latitude'].astype(str)
df['longitude'] = df['longitude'].astype(str)
print(df)
print(df.columns)

# print unique closest_hour values
#print(df['closest_hour'].unique())


# Save the DataFrame to a CSV file
df.to_csv(f"{iba_dir}/iba_observations_2025_processed.csv", index=False, encoding="utf-8")
