#!/usr/bin/env bash
# This script fetches single and pressure level 15-days EC-ENS data from MARS archive,
# adds sde from snow variables, and performs XGBoost downscaling to get soil moisture class forecasts
# for Nordic domain (72/3/52/33). 
# Result is transformed from class to percentage for parameter mapping convenience (SWI1 product).
# Default date is yesterday, give year month day as cmd for other dates.
# Default grid is ERA5-Land, give era5 as 4th cmd for ERA5 grid.
# (AK 2025)
eval "$(/home/users/smartmet/mambaforge/bin/conda shell.bash hook)"
conda activate xgb2

if [ $# -ne 0 ]
then
    year=$1
    month=$2
    day=$3
    if [[ $4 == 'era5' ]] 
        then bsf='B2SF'; era='era5'; GRID=0.25/0.25;
        else bsf='BSF'; era='era5l'; GRID=0.1/0.1;
    fi
else
    year=$(date +%Y)
    month=$(date +%m)
    day=$(date +%d)
    bsf='BSF'; era='era5l'; GRID=0.1/0.1;
fi

DATE="${year}-${month}-${day}"

echo $DATE $GRID $bsf $era

# MARS parameters for surface and pressure levels
MARS_DIR="/home/users/smartmet/firedanger-smartmet/mars"

# MARS requests
process_param() {
    DATE=$1
    MARS_DIR=$2
    GRID=$3
    era=$4
    LEVEL=$5

    REQ_TEMP_0="ec-ens_${LEVEL}_req_temp_0.mars"
    REQ_TEMP_1TO50="ec-ens_${LEVEL}_req_temp_1to50.mars"
    
    TARGET_0="ec-ens_${DATE}_${era}_${LEVEL}-nd-0.grib"
    TARGET_1TO50="ec-ens_${DATE}_${era}_${LEVEL}-nd-1to50.grib"

    REQUEST_FILE_0="${MARS_DIR}/ec-ens_req_${LEVEL}_${DATE}_0.mars"
    REQUEST_FILE_1TO50="${MARS_DIR}/ec-ens_req_${LEVEL}_${DATE}_1to50.mars"
    
    # request control 0
    sed -e "s#DATE_CMD#$DATE#g" \
        -e "s#GRID_CMD#$GRID#g" \
        -e "s#TARGET_CMD#$TARGET_0#g" \
        "${MARS_DIR}/${REQ_TEMP_0}" > "$REQUEST_FILE_0"

    # request members 1 to 50    
    sed -e "s#DATE_CMD#$DATE#g" \
        -e "s#GRID_CMD#$GRID#g" \
        -e "s#TARGET_CMD#$TARGET_1TO50#g" \
        "${MARS_DIR}/${REQ_TEMP_1TO50}" > "$REQUEST_FILE_1TO50"

    # download control 0
    [ -s ec-ens/${TARGET_0} ] && echo "EC-ENS control file already downloaded" || cat $REQUEST_FILE_0 | /home/users/smartmet/firedanger-smartmet/bin/mars
    
    # download members 1 to 50
    [ -s ec-ens/${TARGET_1TO50} ] && echo "EC-ENS members 1 to 50 file already downloaded" || cat $REQUEST_FILE_1TO50 | /home/users/smartmet/firedanger-smartmet/bin/mars

    [ -s ec-ens/${TARGET_0} ] && [ -s ec-ens/${TARGET_1TO50} ] && echo "EC-ENS ready" || mv $TARGET_0 $TARGET_1TO50 ec-ens/

    rm $REQUEST_FILE_0 $REQUEST_FILE_1TO50
}

export -f process_param

cd /home/users/smartmet/data

# SINGLE LEVEL DATA
lev='sfc'
# Fetch single level (sfc) data from MARS
[ ! -s ec-ens/ec-ens_${DATE}_${era}_sfc-nd-0.grib ] && [ ! -s ec-ens/ec-ens_${DATE}_${era}_sfc-nd-1to50.grib ] && \
    echo "Downloading EC-ENS sfc data for ${DATE}..." && \
    process_param $DATE $MARS_DIR $GRID $era $lev || echo "EC-ENS sfc data already downloaded for ${DATE}"

conda activate cdo
# sfc to ensemble members 1-50 and copy control 0 to ensmems/ too
[ ! -s ec-ens/ensmems/ec-ens_${DATE}_${era}_sfc-nd-50.grib ] && grib_copy ec-ens/ec-ens_${DATE}_${era}_sfc-nd-1to50.grib ec-ens/ensmems/ec-ens_${DATE}_${era}_sfc-nd-[number].grib || echo "Already sfc to members"
[ ! -s ec-ens/ensmems/ec-ens_${DATE}_${era}_sfc-nd-0.grib ] && cp ec-ens/ec-ens_${DATE}_${era}_sfc-nd-0.grib ec-ens/ensmems/ec-ens_${DATE}_${era}_sfc-nd-0.grib || echo "Already sfc control to members"

## create disaccumulated variables
[ -s ec-ens/ensmems/ec-ens_${DATE}_${era}_sfc-nd-50.grib ] && ! [ -s ec-ens/ensmems/ec-ens_${DATE}_${era}_sfc-disacc-nd-50.grib ] && \
 seq 0 50 | parallel "cdo -s --eccodes -O mergetime -seltimestep,1 -selname,e,pev,tp,slhf,sshf,ro,sro,ssro,str,strd,ssr,ssrd,sf ec-ens/ensmems/ec-ens_${DATE}_${era}_sfc-nd-{}.grib \
     -deltat -selname,e,pev,tp,slhf,sshf,ro,sro,ssro,str,strd,ssr,ssrd,sf ec-ens/ensmems/ec-ens_${DATE}_${era}_sfc-nd-{}.grib ec-ens/ensmems/ec-ens_${DATE}_${era}_sfc-disacc-nd-{}.grib"

# add snow depth to ec-ens
[ -s ec-ens/ensmems/ec-ens_${DATE}_${era}_sfc-nd-50.grib ] && [ ! -s ec-ens/ensmems/ec-ens_${DATE}_${era}_sfc+sde-nd-50.grib ] && \
    seq 0 50 | parallel cdo -s --eccodes -O aexprf,ec-sde.instr ec-ens/ensmems/ec-ens_${DATE}_${era}_sfc-nd-{}.grib ec-ens/ensmems/ec-ens_${DATE}_${era}_sfc+sde-nd-{}.grib || \
    echo "NOT adding snow - no input or already produced"

# fix grib attributes for ECENS sfc
[ -s ec-ens/ensmems/ec-ens_${DATE}_${era}_sfc+sde-nd-50.grib ] && [ ! -s ec-ens/ensmems/ECENS_${year}${month}${day}T000000_${era}_sfc+sde-nd-50.grib ] && \
 seq 0 50 | parallel grib_set -r -s centre=98,setLocalDefinition=1,localDefinitionNumber=15,totalNumber=51,number={} ec-ens/ensmems/ec-ens_${DATE}_${era}_sfc+sde-nd-{}.grib \
    ec-ens/ensmems/ECENS_${year}${month}${day}T000000_${era}_sfc+sde-nd-{}.grib || echo "NOT fixing ECENS all+sde gribs attributes - no input or already produced"
# join ensemble members and move to grib folder 
[ -s ec-ens/ensmems/ECENS_${year}${month}${day}T000000_${era}_sfc+sde-nd-50.grib ] && [ ! -s grib/ECENS_${year}${month}${day}T000000_${era}_sfc+sde-nd.grib ] && \
grib_copy ec-ens/ensmems/ECENS_${year}${month}${day}T000000_${era}_sfc+sde-nd-*.grib grib/ECENS_${year}${month}${day}T000000_${era}_sfc+sde-nd.grib || echo "NOT joining all+sde ensemble members ECENS - no input or already produced"

# PRESSURE LEVEL DATA
lev='pl'

conda activate xgb2
# Fetch pressure level (pl) data from MARS
[ ! -s ec-ens/ec-ens_${DATE}_${era}_pl-nd-0.grib ] && [ ! -s ec-ens/ec-ens_${DATE}_${era}_pl-nd-1to50.grib ] && \
    echo "Downloading EC-ENS pressure level data for ${DATE}..." && \
    process_param $DATE $MARS_DIR $GRID $era $lev || echo "EC-ENS pl data already downloaded for ${DATE}"
conda activate cdo
# pl to ensemble members (for xgboost) 1-50 and copy control 0 to ensmems/ too
[ ! -s ec-ens/ensmems/ec-ens_${DATE}_${era}_pl-nd-50.grib ] && grib_copy ec-ens/ec-ens_${DATE}_${era}_pl-nd-1to50.grib ec-ens/ensmems/ec-ens_${DATE}_${era}_pl-nd-[number].grib || echo "Already pl to members"
[ ! -s ec-ens/ensmems/ec-ens_${DATE}_${era}_pl-nd-0.grib ] && cp ec-ens/ec-ens_${DATE}_${era}_pl-nd-0.grib ec-ens/ensmems/ec-ens_${DATE}_${era}_pl-nd-0.grib || echo "Already pl control to members"
# fix grib attributes for ECENS
[ -s ec-ens/ensmems/ec-ens_${DATE}_${era}_pl-nd-50.grib ] && [ ! -s ec-ens/ensmems/ECENS_${year}${month}${day}T000000_${era}_pl-nd-50.grib ] && \
 seq 0 50 | parallel grib_set -r -s centre=98,setLocalDefinition=1,localDefinitionNumber=15,totalNumber=51,number={} ec-ens/ensmems/ec-ens_${DATE}_${era}_pl-nd-{}.grib \
    ec-ens/ensmems/ECENS_${year}${month}${day}T000000_${era}_pl-nd-{}.grib || echo "NOT fixing ECENS pl gribs attributes - no input or already produced"
# join ensemble members and move to grib folder 
[ -s ec-ens/ensmems/ECENS_${year}${month}${day}T000000_${era}_pl-nd-50.grib ] && [ ! -s grib/ECENS_${year}${month}${day}T000000_${era}_pl-nd.grib ] && \
grib_copy ec-ens/ensmems/ECENS_${year}${month}${day}T000000_${era}_pl-nd-*.grib grib/ECENS_${year}${month}${day}T000000_${era}_pl-nd.grib || echo "NOT joining pl ensemble members ECENS - no input or already produced"

DATE=${year}-${month}-${day}
EDATE=$(date -d "$DATE +14 days" +%Y-%m-%d)
echo $DATE $EDATE
# laihv lailv swi2clim
echo 'shift laihv lailv swi2clim dates'
! [ -s ec-ens/ECC_${year}${month}${day}T000000_laihv-nd-day.grib ] && ! [ -s ec-ens/ECC_${year}${month}${day}T000000_lailv-nd-day.grib ] && ! [ -s ec-ens/SWIC_${year}${month}${day}T000000_2020_2015-2022_swis-ydaymean-nd-9km-fixed.grib ] && \
    diff=$(($year - 2020)) && \
    cdo -s seldate,$DATE,$EDATE -shifttime,${diff}years ECC_20000101T000000_laihv-nd-day-fix-merged.grib ec-ens/ECC_${year}${month}${day}T000000_laihv-nd-day.grib && \
    cdo -s seldate,$DATE,$EDATE -shifttime,${diff}years ECC_20000101T000000_lailv-nd-day-fix-merged.grib ec-ens/ECC_${year}${month}${day}T000000_lailv-nd-day.grib && \
    cdo -s seldate,$DATE,$EDATE -shifttime,${diff}years SWIC_20000101T000000_2020_2015-2022_swis-ydaymean-nd-9km-fixed-fix-merged.grib ec-ens/SWIC_${year}${month}${day}T000000_2020_2015-2022_swis-ydaymean-nd-9km-fixed.grib || echo 'not shifting'
#seldate,$DATE,$EDATE

# EC-ENS sfc+sde 2t,2d,rsn,sd,stl1,stl2,swvl1-4,sde,sp,u10,v10,src,skt
sfc_input=ec-ens/ensmems/ECENS_${year}${month}${day}T000000_${era}_sfc+sde-nd-{}.grib
# disaccumulated variables e,pev,tp,slhf,sshf,ro,sro,ssro,str,strd,ssr,ssrd,sf
disacc_input=ec-ens/ensmems/ec-ens_${DATE}_${era}_sfc-disacc-nd-{}.grib
# pressure level variables t u q v z at 500,700,850,925 hPa
pl_input=ec-ens/ensmems/ECENS_${year}${month}${day}T000000_${era}_pl-nd-{}.grib

# laihv, lailv from ECC
laihv_input=ec-ens/ECC_${year}${month}${day}T000000_laihv-nd-day.grib
lailv_input=ec-ens/ECC_${year}${month}${day}T000000_lailv-nd-day.grib
# for now use swi2clim instead of swi2, later maybe swi2 forecast produced at desm? tårta på tårta?
swi2clim_input=ec-ens/SWIC_${year}${month}${day}T000000_2020_2015-2022_swis-ydaymean-nd-9km-fixed.grib
output=ec-ens/ensmems/ECXENS_${year}${month}${day}_swi1_${era}_nd-{}.nc

# run XGBoost model to produce swi1 forecasts
#conda activate xgb2
#! [ -s grib/ECXENS_$year${month}${day}T000000_swi1-${era}-nd.grib ] && echo 'start XGBoost predict for SWI1' && seq 0 50 | parallel -j25 python /home/users/smartmet/firedanger-smartmet/bin/xgb-predict-iba.py $sfc_input $disacc_input $pl_input $laihv_input $lailv_input $swi2clim_input $output  || echo 'NOT XGBoost predict for SWI1 - no input or already produced'

#conda activate cdo
# netcdf to grib
#echo 'netcdf to grib'
#[ -s  ] && ! [ -s  ] && \
#seq 0 50 | parallel cdo -s -b P8 -f grb2 copy -setparam,40.228.192 -setmissval,-9.e38 $output ec-ens/ensmems/ECXENS_${year}${month}${day}_swi1_${era}_nd-{}.grib || echo "NO input or already netcdf to grib"

# fix grib attributes
#echo 'fix grib attributes'
#[ -s  ] && ! [ -s  ] && \
#seq 0 50 | parallel grib_set -r -s edition=1,setLocalDefinition=1,localDefinitionNumber=15,centre=98,totalNumber=51,number={} ec-ens/ensmems/ECXENS_${year}${month}${day}_swi1_${era}_nd-{}.grib ec-ens/ensmems/ECXENS_${year}${month}${day}_swi1_${era}_nd-{}-fixed.grib || echo "NOT fixing swi1 grib attributes - no input or already produced"

# join ensemble members and move to grib folder
#echo 'join ensemble members and move to grib folder'
#[ -s  ] && ! [ -s  ] && \
# grib_copy ec-ens/ensmems/ECXENS_${year}${month}${day}_swi1_${era}_nd-*-fixed.grib grib/ECXENS_${year}${month}${day}T000000_swi1-${era}-nd.grib \
# || echo "NOT joining ens members - no input or already done"

# PRESENT MODEL
# select only second timestep for the present model 
conda activate cdo
DATE=${year}-${month}-${day}
ONEDATE=$(date -d "$DATE +1 days" +%Y-%m-%d)
yday=$(date -d "$DATE -1 days" +%Y%m%d)
echo 'EC-ENS start from' $DATE 'Present model prediction for:' $ONEDATE

sfc_input_2=ec-ens/ensmems/ec-ens_${ONEDATE}_sfc+sde-300m-nd-{}.grib
disacc_input_2=ec-ens/ensmems/ec-ens_${ONEDATE}_sfc-disacc-300m-nd-{}.grib
pl_input_2=ec-ens/ensmems/ec-ens_${ONEDATE}_pl-300m-nd-{}.grib
laihv_input_2=ec-ens/ECC_${ONEDATE}_laihv-300m-nd-day.grib
lailv_input_2=ec-ens/ECC_${ONEDATE}_lailv-300m-nd-day.grib
swi2clim_input_2=ec-ens/SWIC_${ONEDATE}_2020_2015-2023_swis-ydaymean-300m-nd.grib
output2=ec-ens/ensmems/ECXENS_${year}${month}${day}_swi1-present_300m-nd-{}.nc

# process laihv, lailv and swi2clim data
# for now, input files are remapped to 330m grid until Mikko has finalized the actual file versions
laihv_in=ECC_20000101T000000_laihv-eu-edte-day0012.grib
lailv_in=ECC_20000101T000000_lailv-eu-edte-day0012.grib
#swi2clim_in=SWIC_20000101T000000_2020_2015-2023_swis-ydaymean-eu-edte0012.grib
diff=$(($year - 2020))
echo 'ecc swic seldate'
! [ -s ec-ens/ECC_${ONEDATE}_laihv-eu-edte-day.grib ] && cdo -s selhour,0 -seldate,$ONEDATE -shifttime,${diff}years $laihv_in ec-ens/ECC_${ONEDATE}_laihv-eu-edte-day.grib || echo 'not shifting laihv dates already done or missing input'
! [ -s ec-ens/ECC_${ONEDATE}_lailv-eu-edte-day.grib ] && cdo -s selhour,0 -seldate,$ONEDATE -shifttime,${diff}years $lailv_in ec-ens/ECC_${ONEDATE}_lailv-eu-edte-day.grib || echo 'not shifting lailv dates already done or missing input'
#! [ -s ec-ens/SWIC_${ONEDATE}_2020_2015-2023_swis-ydaymean-eu-edte.grib ] && cdo -s selhour,0 -seldate,$ONEDATE -shifttime,${diff}years $swi2clim_in ec-ens/SWIC_${ONEDATE}_2020_2015-2023_swis-ydaymean-eu-edte.grib || echo 'not shifting swic dates already done or missing input'
echo 'ecc swic remap'
! [ -s $laihv_input_2 ] && cdo -s -b P8 -O --eccodes remap,003-nordic-grid,ecc-edte-003-nd-weights.nc ec-ens/ECC_${ONEDATE}_laihv-eu-edte-day.grib $laihv_input_2 || echo 'already remapped laihv'
! [ -s $lailv_input_2 ] && cdo -s -b P8 -O --eccodes remap,003-nordic-grid,ecc-edte-003-nd-weights.nc ec-ens/ECC_${ONEDATE}_lailv-eu-edte-day.grib $lailv_input_2 || echo 'already remapped lailv'
#! [ -s $swi2clim_input_2 ] && cdo -s -b P8 -O --eccodes remap,003-nordic-grid,swic-edte-003-nd-weights.nc ec-ens/SWIC_${ONEDATE}_2020_2015-2023_swis-ydaymean-eu-edte.grib $swi2clim_input_2 || echo 'already remapped swic'

# the "latest" (two days ago latest available compared to ONEDATE) swi2 satellite observations remapped to 330m grid 
swi2_raw=grib/SWI_20000101T000000_${yday}T120000_swis.grib
! [ -s $swi2_raw ] && cd /home/users/smartmet/firedanger-smartmet/bin && ./get-swi-daily.sh ${yday} 2.1.1
cd /home/users/smartmet/data
swi2_input_2=ec-ens/SWI_${ONEDATE}_swi2-present_300m-nd.grib
! [ -s $swi2_input_2 ] && cdo -s -b P8 -O --eccodes remap,003-nordic-grid,swis-003-nd-weights.nc -setdate,${ONEDATE} -settime,00:00:00 $swi2_raw $swi2_input_2 || echo 'already remapped swi2 present'

echo 'process ec-ens data'
seq 0 50 | parallel cdo -s selhour,0 -seldate,$ONEDATE $sfc_input ec-ens/ensmems/ec-ens_${ONEDATE}_sfc+sde-nd-{}-fix.grib
seq 0 50 | parallel cdo -s selhour,0 -seldate,$ONEDATE $pl_input ec-ens/ensmems/ec-ens_${ONEDATE}_pl-nd-{}-fix.grib
seq 0 50 | parallel cdo -s selhour,0 -seldate,$ONEDATE $disacc_input ec-ens/ensmems/ec-ens_${ONEDATE}_sfc-disacc-nd-{}-fix.grib
echo 'ec-ens remap to 330m'
! [ -s ec-ens/ensmems/ec-ens_${ONEDATE}_sfc+sde-300m-nd-50.grib ] && seq 0 50 | parallel -j10 cdo -s -b P8 -O --eccodes -remap,003-nordic-grid,ec-ens-003-nd-weights.nc ec-ens/ensmems/ec-ens_${ONEDATE}_sfc+sde-nd-{}-fix.grib $sfc_input_2 || echo 'already sfc remapped to 300m'
! [ -s ec-ens/ensmems/ec-ens_${ONEDATE}_pl-300m-nd-50.grib ] && seq 0 50 | parallel -j10 cdo -s -b P8 -O --eccodes -remap,003-nordic-grid,ec-ens-003-nd-weights.nc ec-ens/ensmems/ec-ens_${ONEDATE}_pl-nd-{}-fix.grib $pl_input_2 || echo 'already pl remapped to 300m'
! [ -s ec-ens/ensmems/ec-ens_${ONEDATE}_sfc-disacc-300m-nd-50.grib ] && seq 0 50 | parallel -j10 cdo -s -b P8 -O --eccodes -remap,003-nordic-grid,ec-ens-003-nd-weights.nc ec-ens/ensmems/ec-ens_${ONEDATE}_sfc-disacc-nd-{}-fix.grib $disacc_input_2 || echo 'already sfc-disacc remapped to 300m'
echo 'ec-ens remapping done'

# shift also dates for SG etc
sg_input=ec-ens/SG_${ONEDATE}_soilgrids-0-200cm-nd-300.grib
! [ -s $sg_input ] && cdo --eccodes setdate,${ONEDATE} -selhour,0 SG_20200501T000000_soilgrids-0-200cm-nd-300-fixfix.grib $sg_input || echo 'already setdate for soilgrids'
# and ecc data
ecc_input=ec-ens/ECC_${ONEDATE}_all-300m-nd0012.grib
! [ -s $ecc_input ] && cdo --eccodes setdate,${ONEDATE} -selhour,0 ECC_20000101T000000_all-300m-nd0012.grib $ecc_input || echo 'not ecc setdate already done or else'
# and twi data
twi_input=ec-ens/COPERNICUS_${ONEDATE}_twi-dtm_nd-300.grib 
! [ -s $twi_input ] && cdo -s -b P8 --eccodes setdate,${ONEDATE} COPERNICUS_20000101T000000_20110701T000000_twi-dtm_nd-300.grib $twi_input || echo 'not twi setdate already done or else'
# and tri data
tri_input=ec-ens/COPERNICUS_${ONEDATE}_tri-dtm_nd-300.grib
! [ -s $tri_input ] && cdo -s -b P8 --eccodes setdate,${ONEDATE} COPERNICUS_20000101T000000_20110701T000000_sdordiff-dtm-tri_nd-300.grib $tri_input || echo 'not tri setdate already done or else'

# DTM inputs (height, slope, aspect)
dtm_height_input=grib/COPERNICUS_20000101T000000_20110701T000000_h-dtm_nd-300-fix.grib
dtm_slope_input=grib/COPERNICUS_20000101T000000_20110701T000000_slor-dtm_nd-300-fix.grib
dtm_aspect_input=grib/COPERNICUS_20000101T000000_20110701T000000_anor-dtm_nd-300-fix.grib
height_in=ec-ens/DTM_${ONEDATE}_height-dtm_nd-300.grib
aspect_in=ec-ens/DTM_${ONEDATE}_aspect-dtm_nd-300.grib
slope_in=ec-ens/DTM_${ONEDATE}_slope-dtm_nd-300.grib
cdo --eccodes setdate,${ONEDATE} -selhour,0 $dtm_height_input $height_in
cdo --eccodes setdate,${ONEDATE} -selhour,0 $dtm_slope_input $slope_in
cdo --eccodes setdate,${ONEDATE} -selhour,0 $dtm_aspect_input $aspect_in

# set date for oceanmask
oceanmask=ec-ens/ERA5L_oceanmask_${ONEDATE}.grib
! [ -s $oceanmask ] && cdo --eccodes setdate,${ONEDATE} -selhour,0 ERA5L_oceanmask.grib $oceanmask || echo 'already setdate for oceanmask'

echo 'start xgboost predict for SWI1 present model'
conda activate xgb2
#! [ -s ec-ens/ensmems/ECXENS_${year}${month}${day}_swi1-present_300m-nd-50.nc ] && 
seq 0 50 | parallel --ungroup -j1 python /home/users/smartmet/firedanger-smartmet/bin/xgb-predict-xtraff-present.py $sfc_input_2 $disacc_input_2 $pl_input_2 $laihv_input_2 $lailv_input_2 $swi2_input_2 $sg_input $ecc_input $twi_input $oceanmask $height_in $aspect_in $slope_in $tri_input $output2 {} || echo 'NOT XGBoost predict for SWI1 - no input or already produced'

conda activate cdo
# netcdf to grib
echo 'netcdf to grib'
#[ -s  ] && ! [ -s  ] && \
seq 0 50 | parallel cdo -s -b P8 -f grb2 copy -setparam,40.228.192 -setmissval,-9.e38 $output2 ec-ens/ensmems/ECXENS_${year}${month}${day}_swi1-present_nd-{}.grib || echo "NO input or already netcdf to grib"

# fix grib attributes
echo 'fix grib attributes'
#[ -s  ] && ! [ -s  ] && \
seq 0 50 | parallel grib_set -r -s edition=1,setLocalDefinition=1,localDefinitionNumber=15,centre=98,totalNumber=51,number={} ec-ens/ensmems/ECXENS_${year}${month}${day}_swi1-present_nd-{}.grib ec-ens/ensmems/ECXENS_${year}${month}${day}_swi1-present_nd-{}-fixed.grib || echo "NOT fixing swi1 grib attributes - no input or already produced"

# join ensemble members and move to grib folder
echo 'join ensemble members and move to grib folder'
generation="${ONEDATE//-/}"
#! [ -s grib/ECXENS_${year}${month}${day}T120000_${ONEDATE}_swi1-present-300m-nd.grib ] && 
grib_copy ec-ens/ensmems/ECXENS_${year}${month}${day}_swi1-present_nd-*-fixed.grib grib/XTRAFF_20250101T000000_${generation}T000000_waterinyourboots-300m-nd-XTRAFF-FIN.grib || echo "NOT joining ens members - no input or already done"

#sudo docker exec smartmet-server /bin/fmi/filesys2smartmet /home/smartmet/config/libraries/tools-grid/filesys-to-smartmet.cfg 0

#rm ec-ens/ensmems/*${ONEDATE}*
#rm ec-ens/*${ONEDATE}*
#rm ec-ens/ensmems/*${year}${month}${day}*
#rm ec-ens/*${year}${month}${day}*