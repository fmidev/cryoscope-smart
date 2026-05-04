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

Target variable for the XGBoost classification model is 1,348 collected in-situ observations via the *Water in Your Boots?* web application form during summer 2025 observation campaign. Includes location information and datetime, among other. 

| Target Variable | Sources | Spatial resolution | Temporal resolution |
|---|---|---|---|
| Soil wetness class<br>Very dry – 0<br>Dry – 1<br>Moist – 2<br>Wet – 3<br>Extremely wet – 4 | In-situ observations from *Water in Your Boots?* 2025 observation campaign | 1,348 observations used as ML training target from Finland, Sweden, Norway (1,716 in total) | March 2025 – October 2025 |

## Downloading the features used in model training

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

