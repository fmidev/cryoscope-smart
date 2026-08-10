| CARRA2 variable|CARRA2 unit | CARRA2 level |CARRA2 temporal resolution|ECSF variable|ECSF units| ECSF level |ECSF temporal resolution|
|:-|:-|:-|:-|:-|:-|:-|:-|
|10m u component of wind||single||10m u component of wind||single||
|10m v component of wind||single||10m v component of wind||single||
|10m wind direction||single||||||
|10m wind speed||single||||||
|2m relative humidity||single||||||
|2m specific humidity||single||||||
|2m temperature||single||2m temperature||single||
|cloud base||single||||||
|cloud top||single||||||
|direct solar radiation||single||||||
|evaporation||single||evaporation||single||
|fog||single||||||
|high cloud cover||single||||||
|instantaneous 10m wind gust||single||||||
|land sea mask||single||land-sea mask||single||
|low cloud cover||single||||||
|maximum 2m temperature since previous post-processing||single||maximum 2m temperature in the last 24h||single||
|minimum 2m temperature since previous post-processing||single||minimum 2m temperature in the last 24h||single||
|mean sea level pressure||single||mean sea level pressure||single||
|medium cloud cover||single||||||
|orography||single||orography||single||
|percolation||single||||||
|sea ice area fraction||single||sea ice cover||||
|sea ice surface temperature||single||||||
|sea ice thickness||single||||||
|sea surface temperature||single||sea surface temperature||single||
|skin temperature||single||||||
|snow cover||single||snow cover||single||
|snow depth||single||snow depth|| single||
|snow depth water equivalent||single||||||
|snow on ice total depth||single||||||
|surface net solar radiation||single||surface net solar radiation||single||
|surface net solar radiation, clear sky||single||||||
|surface net thermal radiation||single||surface net thermal radiation||single||
|surface net thermal radiation, clear sky||single||||||
|suface pressure||single||||||
|surface roughness||single||||||
|surface roughness length for heat||single||||||
|surface runoff||single||surface runoff||single||
|surface sensible heat flux||single||surface sensible heat flux||single||
|surface solar radiation downwards||single||surface solar radiation downwards||single||
|thermal surface radiation downwards||single||Surface thermal radiation downwards||single||
|top net solar radiation||single||top net solar radiation||single||
|top net thermal radiation||single||top net thermal radiation||single||
|total cloud cover||single||total cloud cover||single||
|total column cloud ice water||single||total column cloud ice water||single||
|total column cloud liquid water||single||total column cloud liquid water||single||
|total column graupel||single||||||
|total column integrated water vapour||single||total column water vapour||single||
|total precipitation||single||total precipitation||single||
|cloud cover||pressure||||||
|geometrical vertical velocity||pressure||||||
|geopotential||pressure||geopotential||pressure||
|graupel||pressure||||||
|potential vorticity||pressure||||||
|pseudo-adiabatic potential temperature||pressure||||||
|relative humidity||pressure||||||
|temperature||pressure||temperature||pressure||
|wind speed||pressure||||||
|wind direction||pressure||||||


Derived variables. Calculate dpt from datasets and then fetch data, calculate these in dataframe (no need to create new variables to smartmet)

|derived variable|equation|ECSF variables| ECSF levels |ECSF temporal resolution| CARRA2 variables| CARRA2 levels |CARRA2 temporal resolution|
|:-|:-|:-|:-|:-|:-|:-|:-|
|dewpoint temperature on pressure levels||||||||
|K index|	(T850−T500) + Td850 − (T700−Td700)|||||||
|vertical totals|T850 − T500|||||||
|cross totals|	Td850 − T500|||||||
|totals totals|	T850 + Td850 − 2·T500|||||||
|dewpoint depression|T850 − Td850|||||||
|mid-level lapse rate|(T850−T500) / ((Z500−Z850)/g)|||||||
|thickness|1000–500	(Z500 − Z1000)/g|||||||
|pressure change from previous day|
