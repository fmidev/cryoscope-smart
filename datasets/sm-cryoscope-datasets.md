# TABLES OF DATASETS AND VARIABLES ON sm.cryo-scope.eu

  - [ECSF, ECBSF, ECB2SF](#ecsf-ecbsf-ecb2sf)
  - [ERA5](#era5)
  - [ERA5-Land](#era5-land)
  - [ERA5-Land derived daily statistics](#era5-land-derived-daily-statistics)
  - [ERA5-Land derived climatologies](#era5-land-derived-climatologies)
  - [MODIS](#modis)
  - [CLMS](#clms)
  - [SNOWCAP climatologies for snowdepth and SWE](#snowcap-climatologies-for-snowdepth-and-swe)
  - [RGI2000](#rgi2000)

## ECSF, ECBSF, ECB2SF

[ECSF Seasonal forecasts (SF)](https://sm.cryo-scope.eu/grid-gui?session=bg=light;bl=1;cl=Grey;cm=None;f=;fn=;ft=;g=;gm=;hu=128;is=DarkGrey;iv=Generated;k=;l=;lb=Default;lm=LightGrey;lo=None;lt=;m=0;max=16;mi=Default;min=6;p=;pg=main;pi=;pn=;pre=Image;pro=;sa=60;sm=LightCyan;st=10;sy=None;t=;tg=;tgt=Month;u=;xx=;yy=;&pi=14) are forecasts for 215 days forward updated monthly, with 51 ensemble members (1 control and 50 perturbed members). Each month a new updated SF is added to SmartMet server. 

Horizontal resolution 1° x 1°. Coverage India-Himalayas region. Daily data for single and pressure levels (925 hPa, 850 hPa, 700 hPa, and 500 hPa).  

From Climate Data Store (CDS): 

- [Seasonal forecast daily and subdaily data on single levels](https://cds.climate.copernicus.eu/datasets/seasonal-original-single-levels?tab=overview)
- [Seasonal forecast subdaily data on pressure levels](https://cds.climate.copernicus.eu/datasets/seasonal-original-pressure-levels?tab=overview)

See Tables below for available variables for ECSF. `x` marks if variable is also available as ECBSF or ECB2SF version (statistically bias-adjusted with either ERA5L or ERA5).

### Temperature and pressure

|SmartMet server name| Description | units | ECBSF | ECB2SF|Parameter shortname|Frequency|
|:-|:-|:-|:-|:-|:-|:-|
|PSEA-HPA|Mean sea level pressure|Pa|||msl|instantaneous|
|T2-K|2m temperature|K|x|x|2t|instantaneous|
|STL1-K|Soil temperature level 1|K|x|x|stl1|instantaneous|
|TD2-K|2m dewpoint temperature|K|x|x|2d|instantaneous|
|TMAX-24-K|Maximum 2m temperature in the last 24 hours|K|||mx2t24|24h aggregation|
|TMIN-24-K|Minimum 2m temperature in the last 24 hours|K|||mn2t24|24h aggregation|
|TSEA-K|Sea surface temperature|K|||sst|instantaneous|

### Wind
|SmartMet server name| Description | units | ECBSF | ECB2SF|Parameter shortname|Frequency|
|:-|:-|:-|:-|:-|:-|:-|
|FFG-MS|10m wind gust since previous post-processing|m s-1|||10fg|24h aggregation|
|U10-MS|10 metre U wind component|m s-1|x|x|10u|instantaneous|
|V10-MS|10 metre V wind component|m s-1|x|x|10v|instantaneous|

*Note: ECBSF and ECB2SF both have Wind speed (FF-MS) variable derived from 10u and 10v which ECSF does not have for single level data on SmartMet server, different therefore from the pressure level winds derived variable FF-MS.*

### Radiation and heat

|SmartMet server name| Description | units | ECBSF | ECB2SF|Parameter shortname|Frequency|
|:-|:-|:-|:-|:-|:-|:-|
|FLLAT-JM2|Surface latent heat flux|J m-2|||slhf|24h aggregation since beginning of forecast|
|FLSEN-JM2|Surface sensible heat flux|J m-2|||sshf|24h aggregation since beginning of forecast|
|RADGLOA-JM2|Surface short-wave (solar) radiation downwards|J m-2|||ssrd|24h aggregation since beginning of forecast|
|RADLWA-JM2|Surface long-wave (thermal) radiation downwards|J m-2|||strd|24h aggregation since beginning of forecast|
|RNETLWA-JM2|Surface net long-wave (thermal) radiation|J m-2|||str|24h aggregation since beginning of forecast|
|RNETSWA-JM2|Surface net short-wave (solar) radiation|J m-2|||ssr|24h aggregation since beginning of forecast|
|TSR-J|Top net short-wave (solar) radiation|J m-2|||tsr|24h aggregation since beginning of forecast|
|RTOPLWA-JM2|Top net long-wave (thermal) radiation|J m-2|||ttr|	24h aggregation since beginning of forecast|

### Clouds, evaporation, runoff and precipitation
|SmartMet server name| Description | units | ECBSF | ECB2SF|Parameter shortname|Frequency|
|:-|:-|:-|:-|:-|:-|:-|
|EVAP-M|Evaporation|m of water equivalent|||e||
|RO-M|Runoff|m|||ro||
|RR-M|Total precipitation|m|||tp|24h aggregation since beginning of forecast|
|N-0TO1|Total cloud cover|0-1|||tcc||

### Snow and ice

|SmartMet server name| Description | units | ECBSF | ECB2SF|Parameter shortname|Frequency|
|:-|:-|:-|:-|:-|:-|:-|
|HSNOW-M|Snow thickness (derived)|m|||sde||
|IC-0TO1|Sea-ice cover|0-1|||ci||
|SD-M|Snow depth|m of water equivalent|||sd||
|SNACC-KGM2|Snowfall|m of water equivalent|||sf|24h aggregation since beginning of forecast|
|SND-KGM3|Snow density|kg m-3|||rsn||

### Soil

|SmartMet server name| Description | units | ECBSF | ECB2SF|Parameter shortname|Frequency|
|:-|:-|:-|:-|:-|:-|:-|
|VSW-M3M3|Volumetric soil moisture (needs to be fixed)|m3 m-3|||vsw||

### Pressure level data

|SmartMet server name| Description | units | ECBSF | ECB2SF|Parameter shortname|Frequency|
|:-|:-|:-|:-|:-|:-|:-|
|DD-D|Wind direction (derived)|deg|||wdir||
|FF-MS|10m Wind speed (derived)|m s-1|||ws||
|KX|K index (derived)|K|||kx||
|Q-KGKG|Specific humidity|kg kg-1|||qv||
|Z-M2S2|Geopotential|m2 s-2|||z|
|VP-M2S|Velocity potential (derived)|m2 s-1|||vp|
|U-MS|||||u||
|V-MS|||||v||
|TD-K|Dewpoint temperature|K|||dpt||
|T-K|Temperature|K|||t||

### Other 
|SmartMet server name| Description | units | ECBSF | ECB2SF|Parameter shortname|Frequency|
|:-|:-|:-|:-|:-|:-|:-|
|EWSS-NM2S|Eastward turbulent surface stress|N m-2 s|||ewss||
|NSSS-NM2S|Northward turbulent surface stress|N m-2 s|||nsss||
|TCLW-KGM2|Total column cloud liquid water|kg m-2|||tclw||
|TOTCWV-KGM2|Total column water vapour|kg m-2|||tcwv||

## ERA5

ERA5 Reanalysis data from Climate Data Store:

- [ERA5 hourly data on single levels from 1940 to present](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview)
- [ERA5 hourly data on pressure levels from 1940 to present](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels?tab=overview)
- [ERA5 post-processed daily statistics on single levels from 1940 to present](https://cds.climate.copernicus.eu/datasets/derived-era5-single-levels-daily-statistics?tab=overview)
- [ERA5 post-processed daily statistics on pressure levels from 1940 to present](https://cds.climate.copernicus.eu/datasets/derived-era5-pressure-levels-daily-statistics?tab=overview)


## ERA5-Land

ERA5-Land Reanalysis (ERA5L) data from Climate Data Store:

- [ERA5-Land hourly data from 1950 to present](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land?tab=overview)

## ERA5-Land derived daily statistics


## ERA5-Land derived climatologies

## MODIS

https://doi.org/10.23729/fd-1bad8a16-9edf-38d9-9628-2bd025d8d9ce

## CLMS

## SNOWCAP climatologies for snowdepth and SWE

Data under the SNOWCAP producer contains climatologies (2015-2023) for snow depth and SWE from SNOWCAP, in approximately 1 km grid. Data is organized in multiple *Generations* on SmartMet server to avoid overlapping, see table below. 

Although the timestamps are set to 1 January 2020 – 31 December 2020, the values are climatological statistics calculated over the period 2015–2023. For daily statistics, each calendar day in 2020 represents the multi-year mean/maximum/minimum for that specific day-of-year over 2015–2023. For monthly statistics, each monthly value in 2020 represents the multi-year mean/maximum/minimum for that calendar month over 2015–2023.

SmartMet server parameters **SDE-CM is snowdepth** data (m) and **SD-M is SWE** data (m of water equivalent). 

|Generation | Climatology | Description |
|:-|:-|:-|
|20200101T000000|ydaymean|Multi-year daily mean|
|20200201T000000|ydaymax|Multi-year daily maximum|
|20200301T000000|ydaymin|Multi-year daily minimum|
|20230101T000000|ymonmean|Multi-year montly mean|
|20230201T000000|ymonmax|Multi-year montly maximum|
|20230301T000000|ymonmin|Multi-year monthly minimum|



## RGI2000