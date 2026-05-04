# Training a model to forecas soil wetness classes for trafficability with eXtreme gradient boosting (XGBoost)

This code reproduces the data and model training and prediction workflows used in `Kröger et al.: Water in Your Boots: Community-Based App for Arctic Wildfire Preparedness and Terrain Trafficability Conditions`

## System requirements

Python version 3.11.5 in the UNIX/Linux environment was used in this project.

The time it takes to run a XGBoost model training dependes f.ex. on the number of locations, number of predictors, selected hyperparameters, etc. For 1,348 observations, 66 predictors and hyperparameters described in the article, it took approximately 20 minutes to train the model with Optuna hyperparameter tuning (100 trials), with 32 CPU cores and 251G memory. With the best fitted model from Optuna tuning, predicting soil wetness from 15-day ensemble forecast data takes around 5 hours with 63 CPU cores and 125G memory. Most time consuming is fetching latest EC-ENS 15-day ensemble forecasts from ECMWF Mars archive. Training the model and predicting with it was carried out on different servers. 

## Dependencies

To create xgb environment used in this project, check out the [environment-xtraff.yml](environment-xtraff.yml) file.

How to access Mars archive...?

Instructions for Optuna and Optuna Dashboard at https://optuna.org.

For each step it is adviced to use the GNU Screen, downloading the data and running the model training/prediction takes time.

The Climate Data Operator (CDO) software is used in predicting the soil wetness for handling the input/output grib files https://code.mpimet.mpg.de/projects/cdo/embedded/index.html#x1-30001.1.

We use the GNU parallel: Tange, O., 2018. GNU Parallel 2018. Available at: https://doi.org/10.5281/zenodo.1146014

## Target variable 

Target variable for the XGBoost classification model is 1,348 collected in-situ observations via the *Water in Your Boots?* web application form during summer 2025 observation campaign. Includes location information and datetime, among other. More information from the publication. 

| Target Variable | Sources | Spatial resolution | Temporal resolution |
|:-|:-|:-|:-|
| Soil wetness class<br>Very dry – 0<br>Dry – 1<br>Moist – 2<br>Wet – 3<br>Extremely wet – 4 | In-situ observations from *Water in Your Boots?* 2025 observation campaign | 1,348 observations used as ML training target from Finland, Sweden, Norway (1,716 in total) | March 2025 – October 2025 |

## Downloading the features used in model training

For training the XGBoost model, you will need a table of all features (predictors) and target (predictand) in all observation locations for the whole time period as input. 

We have several time series scripts in Python that use the request module to make http-requests to our SmartMet server (https://smartmet.xyz/grid-gui) Time Series API (https://github.com/fmidev/smartmet-plugin-timeseries). 

To fetch ERA5-Land data from SmartMet server, run the 

In addition, static variables, such as different land covers or inland water fractions, must be prepared as time series data. To run the time series (ts) scripts, you will need the csv file with LUCAS point-ids, and corresponding latitudes and longitudes. All the ts scripts need functions.py with functions for the time series queries etc. You can fetch data for up to 5000 points per query. Output is a csv file for each location. Check the directory structures defined in the scripts.

To download the predictand SWI2 data, run the get-swi-ts-all-FIN.py. The time series query for SWI target parameters also replaces some of the missing values with linearly interpolated values using the two nearest values within a 4-day time interval with interpolate_t. The resulting time series per location are saved as csv files.

To download the ERA5-Land predictor data, run the get-era5l-ts-all-FIN.py. It fetches the 24h accumulated, 00 and 12 UTC hourly, and 5-/15-/60-/100-day rolling cumulative daily sums time series data and saves them per location and predictor as csv files.

To download SWI2 climatology predictor data, run get-swi-clim-ts-FIN.py.

To download static predictors such as soil type, run get-ECC-static.py.

To plot the LUCAS locations on map (whole set or subset), run plot-LUCAS-locations.py. You will need a NUTS_RG_20M_2021_4326.json file for the background map.

List of all 10 000 Lucas locations (POINTIDs) used in this study can be found in 10000pointIDs-2.txt file.

Note that LUCAS_2018_Copernicus_attr+additions_AT-UK_soils.csv file has soilgrids information etc used in this study.

## Training the model 

## Predicting soil wetness classes

## End-user service trafficability.xyz 

## References 

OPTUNA 
Takuya Akiba, Shotaro Sano, Toshihiko Yanase, Takeru Ohta, and Masanori Koyama. 2019.
	Optuna: A Next-generation Hyperparameter Optimization Framework. In KDD.

GNU Parallel
Tange O. (2018). GNU parallel. Zenodo. 10.5281/zenodo.1146014    

Climate Data store (CDS)
https://cds.climate.copernicus.eu/ 

