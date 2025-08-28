# SmartMet server for CryoSCOPE - Overview

## SmartMet server - sources and links

- Main dissemination server: **sm.cryo-scope.eu** 
- Secondary server: firedanger.nsdc.fmi.fi (testing and development)
- General data browser (grid-gui): https://sm.cryo-scope.eu/grid-gui
- NOTE! Server to service data for Europe **desm.harvesterseasons.com** and https://desm.harvesterseasons.com/grid-gui (not to duplicate existing datasets from previous work)
- [The official SmartMet server documentation](https://github.com/fmidev/smartmet-server)

## What is SmartMet server? 
SmartMet server is a data and product server that provides access to observational, forecast, and model data. It is used for data services and product generation. The server can host datasets and products from several producers, e.g. the new datasets and products produced in the CryoSCOPE project. 

Both project’s internal and external users can access and explore the CryoSCOPE datasets via SmartMet server APIs (e.g. Timeseries, WMS, EDR) and the general data browser (grid-gui).

[Timeseries](02_Timeseries.md) to get time series data. 

[WMS](03_WMS.md) for web map layers. 

[EDR](04_EDR.md) for environmental data retrieval. 

## Why SmartMet for CryoSCOPE? 
- Centralized data access: 
- Standard APIs
- end-user services with data from smartmet

## Grid-GUI interface

The general data browsers (grid-gui) can be found from: 
- https://sm.cryo-scope.eu/grid-gui (Figure 1) or
- https://desm.harvesterseasons.com/grid-gui 

The latter one already has a lot of data for European domain. However, main dissemination server for CryoSCOPE will be **sm.cryo-scope.eu**. 


![figure 1](../smartmet-view.png)
*Figure 1. View of grid-gui interface for [sm.cryo-scope.eu/grid-gui](https://sm.cryo-scope.eu/grid-gui?session=bg=light;bl=1;cl=Grey;cm=None;f=1766;fn=0;ft=1;g=156;gm=5080;hu=128;is=DarkGrey;iv=Generated;k=T2-K:ERA5:5080:1:0:1:0;l=0;lb=Default;lm=LightGrey;lo=None;lt=1;m=3;max=16;mi=Default;min=6;p=T2-K;pg=main;pi=9;pn=ERA5;pre=Image;pro=5080;sa=60;sm=LightCyan;st=10;sy=None;t=20250704T000000;tg=202507;tgt=Month;u=;xx=;yy=;&cm=Temperature%20(240K..341K)).*

From the grid-gui interface user can browse available producers, products (data sets), parameters, and time periods. It is a useful tool for [Timeseries](02_Timeseries.md) requests and other APIs.  



screenshot(s) of grid-gui

fmi-key break down

ks timeseries official doc for source! (anni note)

geometry

etc kaikki muuttujat siinä vasemmalla