# Example End-User Service: A forestry climate service Harvester Seasons

With SmartMet Server as a backend, it is possible to build end-user services that visualize and demonstrate the data products developed within the CryoSCOPE project.

An example of such a service is [Harvester Seasons](harvesterseasons.com), developed for forestry use cases to support more sustainable forest operations. The service provides vizualisation of satellite data, reanalysis datasets, and forecasts for variables and indices identified together with end-users as most relevant for forestry operations (f.ex. trafficability, soil water index, soil temperature, snow height, etc). A lightweight, JavaScript-based web interface combines these data sources into an interactive visualization and analysis tool.

The entire system supporting the service is available in the [harvesterseasons-smartmet](https://github.com/fmidev/harvesterseasons-smartmet) GitHub repository.

The service has three main components: Trafficability index, WMS layers, and Time series graphs. 

![figure 1](../harvesterseasons.jpg)

Figure 1. View of the Harvester Seasons service. 

### Define own indices with LUA functions

![figure 2](../lua.jpg)

