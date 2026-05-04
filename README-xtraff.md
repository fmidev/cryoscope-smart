# Training a model to forecas soil wetness classes for trafficability with eXtreme gradient boosting (XGBoost)

This code reproduces the data and model training and prediction workflows used in `Kröger et al.: Water in Your Boots: Community-Based App for Arctic Wildfire Preparedness and Terrain Trafficability Conditions`

## System requirements

Python version 3.11.5 in the UNIX/Linux environment was used in this project.

The time it takes to run a XGBoost model training dependes f.ex. on the number of locations, number of predictors, selected hyperparameters, etc. For 1,348 observations, 66 predictors and hyperparameters described in the article, it took approximately 20 minutes to train the model with Optuna hyperparameter tuning, with 32 CPU cores and 251G memory. With the best fitted model from Optuna tuning, predicting soil wetness from 15-day ensemble forecast data takes around 5 hours with 63 CPU cores and 125G memory. Most time consuming is fetching latest EC-ENS 15-day ensemble forecasts from ECMWF Mars archive. Training the model and predicting with it was carried out on different servers. 

## Dependencies

To create xgb environment used in this project, check out the [environment-xtraff.yml](environment-xtraff.yml) file.

To download the seasonal forecast data etc from the Climate Data Store, the CDS API client needs to be installed https://cds.climate.copernicus.eu/api-how-to. You will need to register for an ECMWF account to download data from CDS. To download the seasonal forecast data etc from the Climate Data Store, the CDS API client needs to be installed https://cds.climate.copernicus.eu/api-how-to. You will need to register for an ECMWF account to download data from CDS.

Instructions for Optuna and Optuna Dashboard at https://optuna.org.

For each step it is adviced to use the Linux screen, downloading the data and running the model training/prediction takes time.

The Climate Data Operator (CDO) software is used in predicting the SWI2 for handling the input/output grib files https://code.mpimet.mpg.de/projects/cdo/embedded/index.html#x1-30001.1.

We use the GNU parallel: Tange, O., 2018. GNU Parallel 2018. Available at: https://doi.org/10.5281/zenodo.1146014

## Target variable 

## Downloading the features used in model training

## Training the model 

## Predicting soil wetness classes

## End-user service trafficability.xyz 