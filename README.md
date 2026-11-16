# SmartMet for CryoSCOPE

SmartMet server is a data and product server that provides access to observational, forecast, and model data. It is used for data services and product generation. The server can host datasets and products from several producers, e.g. the new datasets and products produced in the CryoSCOPE project. Both project’s internal and external users can access and explore the CryoSCOPE datasets via SmartMet server APIs and the general data browser (grid-gui). The main point within the CryoSCOPE project is that SmartMet server can be used for end-user services with Smartmet as the backend data server: simple & efficient.


This repo contains information on the SmartMet server for CryoSCOPE: documentation, links, examples. It is intended for users who need to query, visualize, or contribute data via the server.

See https://github.com/fmidev/cryoscope-smartmet for server configuration and workflows.

See [the official SmartMet server documentation](https://github.com/fmidev/smartmet-server) for more details. 

## Documentation

- [SmartMet Server Overview](docs/00_Overview.md)
- [Data Contribution Guide](docs/01_Data_Contribution.md)
- [Timeseries API](docs/02_Timeseries.md)
- [WMS API](docs/03_WMS.md)
- [EDR API](docs/04_EDR.md)
- [Script Examples (Python)](docs/05_Examples.md)
- [Datasets available](docs/06_Datasets.md)
- [Example end-user service: HarvesterSeasons](docs/07_HarvesterSeasons.md)
- [FAQ](docs/08_FAQ.md)

## Contact Us

Questions, feedback, or need support, feel free to reach out:

👩‍💻 Maintainer: Anni Kröger, Finnish Meteorological Institute

📧 Email: anni.kroger@fmi.fi

🌐 About the CryoSCOPE project: https://cryoscope-project.eu

# Cryoscope Arctic observing analysis

Smart climate monitoring and Arctic cryosphere observation platform are used as context for an AI led analysis of how Arctic Observig is doing based on Claude Sonnet 5 agent work guided by Mikko Strahlendorff. The key data set was fetched from WMO Oscar surface at https://oscar.wmo.int/surface/#/search. The empty search was changed by matching ANY criteria and defining the bounding box as 60..90N and -180..180E.

## 📊 Analysis & Data

### WMO OSCAR Arctic Weather Stations Analysis

Comprehensive analysis of **1,127 Arctic meteorological stations** (60°N-84.5°N) from the WMO OSCAR Surface Database.

**Location:** [`analysis/wmo-oscar-arctic-stations/`](analysis/wmo-oscar-arctic-stations/)

**Quick Start:** See [analysis/wmo-oscar-arctic-stations/START_HERE.md](analysis/wmo-oscar-arctic-stations/START_HERE.md)

**Contents:**
- 📄 Comprehensive technical reports and analysis
- 📊 Publication-quality visualizations (300 DPI)
- 📍 Complete Arctic station dataset (1,127 stations, 29 columns)
- 🛠️ Implementation guide for Cryoscope platform integration
- 🗺️ Geographic distribution analysis and coverage assessment

**Key Findings:**
- ✅ Excellent sub-Arctic coverage (987 stations below 70°N)
- ⚠️ Critical High Arctic gap (only 144 stations above 70°N)
- 📈 Data-driven recommendations for network expansion

For more details, start with [`analysis/wmo-oscar-arctic-stations/README.md`](analysis/wmo-oscar-arctic-stations/README.md)
