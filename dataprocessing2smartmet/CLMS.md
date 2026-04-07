# CLMS processing

## SWE 5km

```bash
#!/bin/bash
# CLMS SWE Globland SWE 5km NH data to SmartMet server 

year=$1
# first mergetime all daily nc files to yearly nc files
cdo --eccodes mergetime c_gls_SWE5K_${year}*_NHEMI_SSMIS_V1.0.2.nc c_gls_SWE5K_${year}_NHEMI_SSMIS_V1.0.2.nc

# then grib2 conversions
cdo --eccodes -s -O -b P12 -f grb2 copy -setparam,60.1.0 -selname,swe c_gls_SWE5K_${year}_NHEMI_SSMIS_V1.0.2.nc CLMS_20000101T000000_${year}_swe.grib 
grib_set -s centre=86,discipline=0,parameterCategory=1,parameterNumber=60,shortName=sd CLMS_20000101T000000_${year}_swe.grib CLMS_20000101T000000_${year}_Globland_SWE5km_NH.grib 
```