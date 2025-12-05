## ECSF, ECBSF, ECB2SF

[ECSF Seasonal forecasts (SF)](https://sm.cryo-scope.eu/grid-gui?session=bg=light;bl=1;cl=Grey;cm=None;f=;fn=;ft=;g=;gm=;hu=128;is=DarkGrey;iv=Generated;k=;l=;lb=Default;lm=LightGrey;lo=None;lt=;m=0;max=16;mi=Default;min=6;p=;pg=main;pi=;pn=;pre=Image;pro=;sa=60;sm=LightCyan;st=10;sy=None;t=;tg=;tgt=Month;u=;xx=;yy=;&pi=14) are forecasts for 215 days forward updated monthly, with 51 ensemble members (1 control and 50 perturbed members). Each month a new updated SF is added to SmartMet server. 

Horizontal resolution 1° x 1°. Coverage India-Himalayas region. Daily data for single (sl) and pressure (pl) levels (925 hPa, 850 hPa, 700 hPa, and 500 hPa).  

From Climate Data Store (CDS): 

- [Seasonal forecast daily and subdaily data on single levels](https://cds.climate.copernicus.eu/datasets/seasonal-original-single-levels?tab=overview)
- [Seasonal forecast subdaily data on pressure levels](https://cds.climate.copernicus.eu/datasets/seasonal-original-pressure-levels?tab=overview)

See Table below for available variables for ECSF. `x` marks if variable is also available as ECBSF or ECB2SF version.

|SmartMet server name| Description | units | ECBSF | ECB2SF|Parameter shortname|Frequency|sl or pl|
|:-|:-|:-|:-|:-|:-|:-|:-|
|DD-D|Wind direction|deg|||wdir||pl|
|EVAP-M|Evaporation|m of water equivalent|||e||sl|
|EWSS-NM2S|Eastward turbulent surface stress|N m-2 s|||ewss||sl|
|FF-MS|10m Wind speed (derived)|m s-1|||ws||pl|
|FFG-MS|10m wind gust since previous post-processing|m s-1|||10fg||sl|
|FLLAT-JM2|Surface latent heat flux|J m-2|||slhf||sl|
|FLSEN-JM2|Surface sensible heat flux||J m-2||sshf||sl|
|HSNOW-M|Snow thickness (derived)|m|||sde||sl|
|IC-0TO1|Sea-ice cover|0-1|||ci||sl|
|KX|K index (derived)|K|||kx||pl|
|N-0TO1|Total cloud cover|0-1|||tcc||sl|
|NSSS-NM2S|Northward turbulent surface stress|N m-2 s|||nsss||sl|
|PSEA-HPA|Mean sea level pressure|Pa|||msl||sl|
|Q-KGKG|Specific humidity|kg kg-1|||qv||pl|
|RADGLOA-JM2|Surface short-wave (solar) radiation downwards|J m-2|||ssrd|24h aggregation since beginning of forecast|sl|
|RADLWA-JM2|Surface long-wave (thermal) radiation downwards|J m-2|||strd|24h aggregation since beginning of forecast|sl|
|RNETLWA-JM2|Surface net long-wave (thermal) radiation|J m-2|||str|24h aggregation since beginning of forecast|sl|
|RNETSWA-JM2|Surface net short-wave (solar) radiation|J m-2|||ssr|24h aggregation since beginning of forecast|sl|
|RO-M|Runoff|m|||ro||sl|
|RR-M|Total precipitation|m|||tp|24h aggregation since beginning of forecast|sl|
|RTOPLWA-JM2|Top net long-wave (thermal) radiation|J m-2|||ttr|	24h aggregation since beginning of forecast|sl|
|SD-M|Snow depth|m of water equivalent|||sd||sl|
|SNACC-KGM2|Snowfall|m of water equivalent|||sf|24h aggregation since beginning of forecast|sl|
|SND-KGM3|Snow density|kg m-3|||rsn||sl|
|STL1-K|Soil temperature level 1|K|||stl1||sl|
|T-K|Temperature|K|||t||pl|
|T2-K|2m temperature|K|||2t||sl|
|TCLW-KGM2|Total column cloud liquid water|kg m-2|||tclw||sl|
|TD-K|Dewpoint temperature|K|||dpt||pl|
|TD2-K|2m dewpoint temperature|K|||2d||sl|
|TMAX-24-K|Maximum 2m temperature in the last 24 hours|K|||mx2t24|||
|TMIN-24-K|Minimum 2m temperature in the last 24 hours|K|||mn2t24|||
|TOTCWV-KGM2|Total column water vapour|kg m-2|||tcwv||sl|
|TSEA-K||K|||sst||sl|
|TSR-J|||||tsr||sl|
|U-MS|||||u||pl|
|U10-MS|||||10u||sl|
|V-MS|||||v||pl|
|V10-MS|||||10v||sl|
|VP-M2S|Velocity potential (derived)|m2 s-1|||vp||pl|
|VSW-M3M3|Volumetric soil moisture (needs to be fixed)|m3 m-3|||vsw||sl|
|Z-M2S2|Geopotential|m2 s-2|||z||pl|







## ERA5

## ERA5L

## MODIS



