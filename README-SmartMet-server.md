# SmartMet server configuration instructions

## Parameter mapping 

### Inspecting GRIB files 

Check out the contents of grib files with two below commands: 

`cdo --eccodes sinfon name_of_file.grib`  # parameter names

`cdo --eccodes sinfo name_of_file.grib` # parameter IDs

Figure 1 shows example output. We see parameter shortnames, grid coordinates, vertical coordinates and time coordinates, among other information. For parameter mappings, we are interested in Parameter name. Replacing `sinfon` with `sinfo` would produce otherwise similar output, but instead with Parameter IDs:

- rsn : 33.128
- sde : 11.1.0
- sd : 141.128
- sf : 144.128

From this we see that sde is GRIB2, and others are GRIB1 (3 identifiers vs 2). From the ECMWF Parameter database https://codes.ecmwf.int/grib/param-db/ you'll find more information on these variables by searching the shortname. For example, rsn is Snow density [kg m-3] with ID 33: https://codes.ecmwf.int/grib/param-db/?search=rsn. The GRIB encoding for GRIB1 and GRIB2 can also be checked from Parameter database. 

We will need this information for parameter mappings. If not all parameters from grib file are visible at SmartMet server's grid-gui, you need to define new mappings.

![figure 1](sinfoprint.png)
Figure 1. 

### FMI parameter definitions 

Good job, you have found a variable not yet configured to SmartMet server!

We start with FMI parameter definitions. All configuration files for parameter mappings are in path `~/config/libraries/grid-files/`. Files for new configurations are in `~/config/libraries/grid-files/ext/` - it is super important to define new mappings under `ext/` directory so that they will not be overridden!! 

The file we are interested in is `fmi_parameters.csv` - identical filename in both working directories. First check if `~/config/libraries/grid-files/fmi_parameters.csv` already has definition for the new parameter (search by name, not shortname). For example, rsn is already mapped there and you should find a row: 

`1035;SND-KGM3;kg m-2;Snow density in kg/m3;1;1;1;;`

In case you can't find your variable, define a new row in `~/config/libraries/grid-files/ext/fmi_parameters.csv`. Here example for 10m U-component of wind:

`# FIELDS:`

`# 1) FmiParameterId`

`# 2) FmiParameterName`

`# 3) FmiParameterUnits`

`# 4) FmiParameterDescription`

`# 5) AreaInterpolationMethod`

`# 6) TimeInterpolationMethod`

`# 7) LevelInterpolationMethod`

`# 8) DefaultPrecision`

`10000165;U10-MS;m/s;10 metre U wind component;1;1;1;2;`

Here, FmiParameterId is given as 10000000 + parameter ID from https://codes.ecmwf.int/grib/param-db/. For example for 10m U-wind component parameterID is 165 (https://codes.ecmwf.int/grib/param-db/?id=165). FmiParameterName is fmi-name with units, for new parameters you can decide the name (here U10-MS). In theory you could name it to RAINBOW-PONY, but common rule to follow is SHORTNAME-UNITS and using descriptive names. You can copy an existing row in the file, and just change the 4 first fields. So, to recap, fill in this information: 

1) FMI-ID (10000000 + parameter ID)
2) FMI-name (shortname-units)
3) Units
4) Full name of variable

### GRIB parameter definitions

From path `~/config/libraries/grid-files` and `~/config/libraries/grid-files/ext` you will find grib1 parameters.csv and and grib2 parameters.csv, for GRIB1 and GRIB2 parameter definitions, respectively. 

Usually GRIB definitions already exist, but there are exeptions. Similar to before, if there isn’t a definition for parameter, create a new one in `ext/grib1 parameters.csv` or `ext/grib2 parameters.csv`. Below are examples for GRIB1 and GRIB2:

`# GRIB1`

`# Soil wetness level 2`

`171;table2Version=128,indicatorOfParameter=171;`

All the info can be found in https://codes.ecmwf.int/grib/param-db/ OR in the grib file with `sinfo` and `sinfon`. First field is parameter-id (here grib-id), for grib1 you need to give table2version and indicatorOfParameter. F.ex. for soil wetness level 2 check out https://codes.ecmwf.int/grib/param-db/?id=171 GRIB1 edition for these.

`# GRIB2`

`# Soil type`

`43;discipline=2,parameterCategory=3,parameterNumber=0;`

Here https://codes.ecmwf.int/grib/param-db/?id=43 and GRIB2 edition for discipline, parameterCategory and parameterNumber information for soil type.

### FMI to GRIB definitions

Next comes the "mapping" - we need to map GRIB identifiers to FMI identifiers. Paths are same, files are named `fmi parameterID grib.csv`. Below is an example: 

`# FIELDS:`

`# 1) FmiParameterId/FmiParameterName`

`# 2) GribParameterId`

`# 3) ConversionFunction`

`# 4) ReverseConversionFunction`

`# 165:10 metre U wind component (m s-1)`

`U10-MS;165;;;`

First field is fmi-name defined in fmi parameters.csv, second field is grib-id from grib* parameters.csv. It is that simple.

### Reading in new mappings

When all three mapping definitions are ready, you need to run **filesys2smartmet** to generate automatic mappings and read data to server. 

`sudo docker exec smartmet-server /bin/fmi/filesys2smartmet /etc/smartmet/libraries/tools-grid/filesys-to-smartmet.cfg 0`

Sometimes tmp files need to be removed first, otherwise new mappings are not visible. Instructions for that are in the next section. The working order is. 

1) Remove tmp files (see next section)
2) Move GRIB file from grib/ directory to /data directory 
3) Run **filesys2smartmet** 
4) Move GRIB file back to grib/ directory
5) Run **filesys2smartmet** again

From path `~/config/engines/grid-engine` you find `mapping fmi.csv` and `mapping fmi auto.csv` with all mappings for parameters. Mappings are automatically generated to `mapping fmi auto.csv` and they should be moved to the permanent mapping file `mapping fmi.csv` which is not automatically overriden. Below two examples. First is automatically generated mapping for parameter, second is user-defined (afterwards manually added) unit change. Here T2-K and T2-C are 2m temperatures in Kelvins and Celsius. Only T2-K is visible at grid-gui but f.ex. Timeseries queries or WMS layers can be made for T2-C too. There are several functions for these, f.ex. MUL for multiplication. More information can be seen in the mapping files.

`ERA5L;T2-K;2;T2-K;5022;;1;00000;;;;0;E;;;;`

`ERA5L;T2-C;2;T2-K;5022;;1;00000;;;;0;E;SUM{$,-273.15};SUM{$,273.15};;`

Now, new parameter should become visible at grid-gui. If not, check for typos in definition files. You can also check with grid dump if mappings are correct at server: `sudo docker exec smartmet-server /bin/files/grid_dump /srv/data/grib/name_of_file.grib | less`. Sometimes there might be duplicate mappings (ids or names) which mess up the system, check for those too. Now, if you see something like FMI-0 in the `mapping fmi auto.csv`, something went wrong in the mappings definitions. 

### Removing tmp files 

