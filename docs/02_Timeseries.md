# Timeseries API

The Timeseries plugin can be used to fetch time series information for observation and forecast data, with specific time or time interval chosen by the user. The datasets can be downloaded with an HTTP request which contains the parameters needed to obtain the information, processing the results and formatting the output. (Note: Examples of Python scripts for the Timeseries API with output in CSV can be found in [Examples](05_Examples.md)).

For more detailed information, see "the official" [Timeseries API documentation](https://github.com/fmidev/smartmet-plugin-timeseries/tree/master).

A simple example of an HTTP request: 

https://sm.cryo-scope.eu/timeseries?latlon=31.3,77.3&param=utctime,latitude,longitude,T2-K:ERA5:5080:1:0:1:0,SUM{T2-K:ERA5:5080:1:0:1:0;-273.5},MUL{RR-M:ERA5:5080:1:0:1:0;1000}&starttime=20250815T000000Z&endtime=20250820T000000Z&hour=12&format=debug&precision=full&tz=utc&timeformat=sql&origintime=20000101T000000Z

![figure 1](../timeseries-http.png)

*Figure 1. Output for the example http request.*

Let's break it down: 
- The service location (source) that starts the Timeseries HTTP request query is `sm.cryo-scope.eu`, and the parameters following it are given as name-value pairs separated by the ampersand (&) character. (For European data, use `desm.harvesterseasons.com`)
- The data is for a point location with latitude 31.3 and longitude 77.3. 
- Parameters requested are utctime, latitude, longitude, 2m temperature in Kelvins, 2m temperature in Celsius, and total precipitation in mm from ERA5 reanalysis dataset. The FMI key for parameters can be copied from https://sm.cryo-scope.eu/grid-gui (or https://desm.harvesterseasons.com/grid-gui) (Figure 2). 
- This request uses the Timeseries API’s built-in functions, SUM for summation and MUL for multiplication, to process the data on-the-fly. 
- Data is requested for 5 days 15.8.-20.8.2025 for 12 UTC daily. 
- Output format is debug (Figure 1).

![figure 2](../fmi-key.png)

*Figure 2. FMI Key can be copied from grid-gui to Timeseries request.*



functions

bbox, area, point, etc

formats

time

Key features:

Location-based queries: request data for coordinates, place names, administrative areas, or polygons.

Time range selection: flexible definition of start and end times, temporal resolution, and step length.

Variable selection: access to a wide range of forecast, observation, and reanalysis parameters.

Multiple formats: results available in JSON, XML, or CSV for easy integration with applications and workflows.

Aggregation & statistics: compute averages, sums, maxima/minima, or other statistics over defined periods.

Integration: well-suited for modeling, visualization dashboards, or application backends that need on-demand timeseries data.

Example use cases:

Extracting temperature and precipitation forecasts for wildfire risk modeling.

Providing soil moisture time series to support trafficability assessments.

Supplying climate indicators for user-facing services and decision support systems.