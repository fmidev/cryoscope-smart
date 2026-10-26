# ML for Snow Water Equivalent from EO data: Combining Snowcap SWE as target with meteorological and satellite data to forecast SWE conditions with XGBoost​

This README describes the training data generation, model training, validation and prediction workflows for the snow water equivalent (SWE) model. The model is trained using SNOWCAP SWE as the target and ERA5 Land reanalysis, SNOWCAP climatology, terrain and forest statistics data as input features. Operational predictions are made from the ECMWF ensemble forecast for 15-day and 215-day inputs. This work is part of the CryoSCOPE project.

## System requirements
Python version Python 3.12.7 in the UNIX/Linux environment was used in this project.

The time it takes to run the model training dependes f.ex. on the number of locations, number of predictors, selected hyperparameters, etc. For 20 000 locations, 24 features and Optuna tuning, it took approximately 3 days to train the model used in this study, with 64 CPU cores and 228G memory. With the fitted model, predicting SWE from 15-day forecast data takes around XX hours, and predicting with seasonal forecast data takes around YY hours, with a similar setup.   

## Dependencies
To create xgb environment used in this project, check out the `swe-requirements.txt` file. (TODO: create)

To download the seasonal forecast data etc from the Climate Data Store, the CDS API client needs to be installed https://cds.climate.copernicus.eu/api-how-to. You will need to register for an ECMWF account to download data from CDS. 
To download the seasonal forecast data etc from the Climate Data Store, the CDS API client needs to be installed https://cds.climate.copernicus.eu/api-how-to. You will need to register for an ECMWF account to download data from CDS.

Instructions for Optuna and Optuna Dashboard at https://optuna.org.

For each step it is adviced to use the Linux screen, downloading the data and running the model training/prediction takes time.

The Climate Data Operator (CDO) software is used in predicting the SWE for handling the input/output grib files https://code.mpimet.mpg.de/projects/cdo/embedded/index.html#x1-30001.1.

We use the GNU parallel: Tange, O., 2018. GNU Parallel 2018. Available at: https://doi.org/10.5281/zenodo.1146014

## Downloading the target and input features data

For training the model you will need a table of all features and target in all chosen locations for the whole time period as input. We have several time series scripts in Python that use the request module to make http-requests to our SmartMet server (https://desm.harvesterseasons.com/grid-gui) Time Series API (https://github.com/fmidev/smartmet-plugin-timeseries). In addition, static variables must be prepared as time series data. Output is a csv file for each location.

### Matching static features to SNOWCAP grid points

### Selecting training and validation locations: Feature Space Coverage Sampling (FSCS)

### Fetching training time series from SmartMet server

## Training the model 

### Optuna tuning and XGBoost model training

### Validation with separate 20 000 locations

## Predicting SWE
