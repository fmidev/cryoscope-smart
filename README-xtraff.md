# Training a model to forecas soil wetness classes for trafficability with eXtreme gradient boosting (XGBoost)

This code reproduces the data and model training and prediction workflows used in `Kröger et al.: Water in Your Boots: Community-Based App for Arctic Wildfire Preparedness and Terrain Trafficability Conditions`


## Table of contents

- [System requirements](#system-requirements)
- [Dependencies](#dependencies)
- [Target variable](#target-variable)
- [Downloading the features used in model training](#downloading-the-features-used-in-model-training)
- [Training the model](#training-the-model)
- [Predicting soil wetness classes](#predicting-soil-wetness-classes)
- [End-user service trafficability.xyz](#end-user-service-trafficabilityxyz)
- [Contact](#contact)
- [References](#references)


## System requirements

Python version 3.11.5 in the UNIX/Linux environment was used in this project.

The time it takes to run a XGBoost model training dependes f.ex. on the number of locations, number of predictors, selected hyperparameters, etc. For 1,348 observations, 66 predictors and hyperparameters described in the article, it took approximately 20 minutes to train the model with Optuna hyperparameter tuning (100 trials), with 32 CPU cores and 251G memory. With the best fitted model from Optuna tuning, predicting soil wetness from 15-day ensemble forecast data takes around 5 hours with 63 CPU cores and 125G memory. Most time consuming is fetching latest EC-ENS 15-day ensemble forecasts from ECMWF Mars archive. Training the model and predicting with it was carried out on different servers. 

## Dependencies

To create xgb2 environment used in this project, check out the [environment-xtraff.yml](environment-xtraff.yml) file.

15-day ensemble forecasts are downloaded from ECMWF Mars archive. 

Instructions for Optuna and Optuna Dashboard at https://optuna.org.

For each step it is adviced to use the GNU Screen, downloading the data and running the model training/prediction takes time.

The Climate Data Operator (CDO) software is used in predicting the soil wetness for handling the input/output grib files https://code.mpimet.mpg.de/projects/cdo/embedded/index.html#x1-30001.1.

We use the GNU parallel: Tange, O., 2018. GNU Parallel 2018. Available at: https://doi.org/10.5281/zenodo.1146014

## Target variable 

Target variable for the XGBoost classification model is 1,348 in-situ observations collected via the *Water in Your Boots?* (currently: https://trafficability.xyz/) web application during summer 2025 observation campaign. Includes location information and datetime, among other. More information from the publication. 

| Target Variable | Sources | Spatial resolution | Temporal resolution |
|:-|:-|:-|:-|
| Soil wetness class<br>Very dry – 0<br>Dry – 1<br>Moist – 2<br>Wet – 3<br>Extremely wet – 4 | In-situ observations from *Water in Your Boots?* 2025 observation campaign | 1,348 observations used as ML training target from Finland, Sweden, Norway (1,716 in total) | March 2025 – October 2025 |

## Downloading the features used in model training

For training the XGBoost model, you will need a table of all features (predictors) and target (predictand) in all observation locations for the whole time period as input. The raw in-situ observations are not yet public. 

We have several time series scripts in Python that use the request module to make http-requests to our SmartMet server (https://smartmet.xyz/grid-gui) Time Series API (https://github.com/fmidev/smartmet-plugin-timeseries).

To fetch ERA5-Land data from SmartMet server, run the [ts-era5l-xtraff.py](ts-era5l-xtraff.py) script. It makes Timeseries queries to SmartMet server for each variable separately, for all locations. Time period and step depends on the variable. Output is a csv file for each variable and location, defined with unique location IDs from latitude, longitude (user corrected latitude and longitude is used if available).  

To fetch ERA5 data from SmartMet server, run the [ts-era5-xtraff.py](ts-era5-xtraff.py) script. 

To fetch SWI data from SmartMet server, run the [ts-swi-xtraff.py](ts-swi-xtraff.py) script. 

To fetch the static ECC features, run the [ts-ecc-xtraff.py](ts-ecc-xtraff.py) script. 

The other static features, such as TWI, were acquired from copernicus.data.lit.fmi.fi (HTML index not up-to-date) with `gdallocationinfo`. Example query: `(echo "lat,lon,clay_5-15cm"; paste iba_lonlat.txt <(gdallocationinfo -wgs84 -valonly /vsicurl/https://copernicus.data.lit.fmi.fi/soilgrids/clay/202005_clay_5-15cm_mean_250.tif < iba_lonlat.txt) | awk '{print $2","$1","$3}') > soilgrids/iba-clay_5-15cm.txt` where you need text file which lists one point per row, with longitude in the first column and latitude in the second. 

All features used in training are described in [Appendix A1](linkhere). 

## Training the model 

You´ll need to combine all the features and target as one input csv for the XGBoost training scripts (all chosen locations, full time series) with Linux standard cut and paste commands, or by other means (python scripts). Note that static predictors need to be repeated daily to match timeseries data. The first row of the input table should be column names, all parameters from training csv file (not all were used in the final trained model):

`time,latitude,longitude,latlon_id,class_target,date,closest_hour,user_latitude,user_longitude,accuracy,certainty,answer,accuracy_own,laihv,lailv,rsn,sd,sp,stl1,swvl1,swvl2,swvl3,swvl4,t2,td2,u10,v10,q500,q700,q850,q925,t500,t700,t850,t925,u500,u700,u850,u925,v500,v700,v850,v925,z500,z700,z850,z925,e,ro,sf,slhf,sro,sshf,ssr,ssrd,ssro,str,strd,tp,swi2,date_reform,VH,VV,VH/VV,pm_VH,pm_VV,pm_VH/VV,ndmi_1,ndmi_2,swi1,twi300m,twi,dtmaspect,dtmslope,dtmheight,cvh,lake_cover,land_cover,tvh,urban_cover,cvl,lake_depth,soiltype,tvl,clay_0-5cm,clay_5-15cm,clay_15-30cm,sand_0-5cm,sand_5-15cm,sand_15-30cm,silt_0-5cm,silt_5-15cm,silt_15-30cm,soc_0-5cm,soc_5-15cm,soc_15-30cm,tri,swi1_twi_corrected,swi2_twi_corrected`

To perform the Optuna hyperparameter tuning (https://optuna.org/), run [xgb-fit-optuna-xtraff.py](xgb-fit-optuna-xtraff.py) and give studynumber as cmd (example: `python xgb-fit-optuna-xtraff.py 001`). This script will produce several results (SHAP figures, confusion matrix, classification report, Optuna optimization history plot, model trained with best hyperparameters, etc). 

## Predicting soil wetness classes

Soil wetness classes are predicted for 1-day lead time. This requires first downloading the (latest) 15-day ensemble forecast data from ECMWF Mars archive and pre-processing, as all input data must be re-gridded to 330m spatial resolution. Script for this is [get-ec-ens.sh](get-ec-ens.sh). Preprocessing uses the GNU parallel and CDO. 

XGBoost prediction is done with [xgb-predict-xtraff-present.py](xgb-predict-xtraff-present.py). This Python script uses Xarray to join different input grids into one data frame that includes all time steps for each input in the target grid. Then prediction for soil wetness (classes turned to numerical values) is made with XGBoost predict with the previously trained model. Ready file is then returned to the bash script so that the resulting grib file is fixed and the end product is set up to our SmartMet server. Example end-product [here](https://smartmet.xyz/grid-gui?session=bl=1;cl=Grey;cm=None;f=;fn=-1;ft=0;g=882;gm=5059;hu=128;k=;l=0;lb=DarkSlateGrey;lcp=1;lm=LightGrey;lsl=128;lsp=2;lss=384;lt=1;m=0;max=64;mi=Default;min=2;op=255;p=SWI1;pg=main;pi=32;pl=;pn=SWI;pre=Image;pro=5059;sa=60;sc=DarkSlateGrey;scp=1;sm=LightCyan;ssl=128;ssp=2;sss=384;st=14;t=;tg=;tgt=All;u=;xx=;yy=;&pi=52). 

## End-user service trafficability.xyz 



## Contact

Anni Kröger Finnish Meteorological Institute anni.kroger@fmi.fi for more information. 

## References 

OPTUNA 
Takuya Akiba, Shotaro Sano, Toshihiko Yanase, Takeru Ohta, and Masanori Koyama. 2019.
	Optuna: A Next-generation Hyperparameter Optimization Framework. In KDD.

GNU Parallel
Tange O. (2018). GNU parallel. Zenodo. 10.5281/zenodo.1146014    

Climate Data store (CDS)
https://cds.climate.copernicus.eu/ 

