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
