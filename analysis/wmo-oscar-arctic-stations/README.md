# WMO OSCAR Arctic Observing Network Analysis

This folder analyzes how the Arctic (60°N+) observing network — land weather
stations, drifting sea-ice buoys, ships, and Argo profiling floats — looks today
and how it has evolved over time, using the WMO OSCAR Surface Database and the
Argo program's own data authority (OceanOPS/JCOMMOPS).

---

## 📄 Documentation

### Land Stations
- **[WMO_OSCAR_ARCTIC_ANALYSIS.md](WMO_OSCAR_ARCTIC_ANALYSIS.md)** - Comprehensive
  technical analysis of the current (2026) land-station network: geographic
  distribution, country breakdown, latitude bands, station types, and reporting status
- **[ARCTIC_STATIONS_ANALYSIS.md](ARCTIC_STATIONS_ANALYSIS.md)** - Detailed
  geographic and regional breakdown, with a focus on the Finnish Meteorological
  Institute's network and High Arctic (70°N+) coverage
- **[ARCTIC_STATION_NETWORK_EVOLUTION_1980-PRESENT.md](ARCTIC_STATION_NETWORK_EVOLUTION_1980-PRESENT.md)** -
  How the land-station network has actually grown (and where it hasn't) from the
  1980s to today, using establishment **and** closure dates for a true historical
  active-count series — not just a snapshot of today's survivors

**Note on the reports above:** the two "Core Reports" describe a single 2026
snapshot of the station network (the bundled WMO OSCAR export only includes
currently-Operational stations) and still include 14 Bosnia and Herzegovina WMO
**test stations** (not real Arctic observing sites) in their totals and High
Arctic counts. The bundled `oscar_arctic_stations_60n.csv` export was also found
to **undercount even the Operational stations** by 10-46% depending on country —
for anything beyond a quick first look, use
[oscar_arctic_land_stations_allstatus_60n.csv](oscar_arctic_land_stations_allstatus_60n.csv)
instead, and see the evolution report for the full detail.

### Ocean/Marine Platforms
- **[ARCTIC_MARINE_OBSERVATIONS_AND_SHIP_DATA.md](ARCTIC_MARINE_OBSERVATIONS_AND_SHIP_DATA.md)** -
  Since the Arctic is mostly ocean, this extends the land-station analysis to ships
  and drifting sea-ice buoys: cross-references real-time ECMWF observation-monitoring
  data against the OSCAR register, explains why global ship-observation growth
  trends don't carry over to the Arctic Ocean, and reconstructs a 2000-2024 trend
  in Arctic drifting-buoy counts from public International Arctic Buoy Programme
  (IABP) data.
- **[ARCTIC_MARINE_OSCAR_REGISTRY.md](ARCTIC_MARINE_OSCAR_REGISTRY.md)** -
  Pulls OSCAR's own ship/buoy/float register (all declared statuses) for ≥60°N,
  cross-checks it against the external IABP estimate, and explains why these
  platforms' OSCAR establishment dates can't be used for a time-series analysis
  the way land-station dates can.
- **[ARCTIC_ARGO_OCEANOPS_ANALYSIS.md](ARCTIC_ARGO_OCEANOPS_ANALYSIS.md)** -
  Checks Argo-specific statistics directly from the Argo program's own data
  authority, OceanOPS/JCOMMOPS (ocean-ops.org): 694 floats ever deployed ≥60°N out
  of 22,393 worldwide, a genuine and sharply accelerating deployment trend in
  2025-2026, and a cross-check against OSCAR's own Argo-equivalent count.

### Geographic Context
- **[ARCTIC_LATITUDE_CIRCLE_GEOMETRY.md](ARCTIC_LATITUDE_CIRCLE_GEOMETRY.md)** -
  The latitude-band histograms elsewhere in this folder slice equal-sized degree
  bands that represent very different amounts of actual ground: this shows how
  sharply the circumference of the circle of latitude shrinks toward the pole, and
  checks (and confirms) that the High Arctic monitoring gap is real even after
  adjusting for that shrinking ring.

---

## 📊 Data Files

### Land Stations — Snapshot
- **[oscar_arctic_stations_60n.csv](oscar_arctic_stations_60n.csv)** (723 KB) —
  1,127 stations north of 60°N, 29 metadata columns, currently-Operational only
- **[oscar_high_arctic_stations_70n.csv](oscar_high_arctic_stations_70n.csv)** (98 KB) —
  144-station High Arctic (≥70°N) subset of the file above

### Land Stations — Evolution (all statuses, including closures)
- **[oscar_arctic_land_stations_allstatus_60n.csv](oscar_arctic_land_stations_allstatus_60n.csv)** —
  **Supersedes the snapshot above for historical analysis.** 1,621 land stations
  (`Land (fixed)` + `Land (on ice)`) north of 60°N, **all declared statuses**
  (Operational, Closed, Silent, Partly operational, Unknown), pulled directly from
  the OSCAR API, with `Date established` and `Date closed` for a true historical
  active-count series
- **[oscar_arctic_land_stations_by_decade_allstatus.csv](oscar_arctic_land_stations_by_decade_allstatus.csv)** —
  Established/closed/net-change/cumulative true-active counts per decade (pre-1980 through 2020s)
- **[oscar_arctic_stations_by_decade.csv](oscar_arctic_stations_by_decade.csv)** —
  *(Superseded — kept for history)* Same idea but from the undercounted,
  operational-only snapshot; see the evolution report for why the file above
  should be used instead

### Ocean/Marine Platforms
- **[iabp_arctic_buoy_counts_by_year.csv](iabp_arctic_buoy_counts_by_year.csv)** —
  Distinct International Arctic Buoy Programme (IABP) buoy IDs reporting from
  ≥60°N, for 13 sample years 2000-2024, reconstructed from IABP's public bulk data
- **[oscar_arctic_marine_platforms_allstatus_60n.csv](oscar_arctic_marine_platforms_allstatus_60n.csv)** —
  1,651 OSCAR-registered marine/ocean platforms (ships, drifting ice buoys, moored
  buoys, Argo floats) north of 60°N, all declared statuses, with program affiliation
- **[oceanops_argo_arctic_floats.csv](oceanops_argo_arctic_floats.csv)** —
  694 Argo floats with a deployment position ≥60°N, pulled directly from
  OceanOPS/JCOMMOPS, with real deployment dates, program/country, and current status

### Geographic Context
- **[latitude_circle_length_by_band.csv](latitude_circle_length_by_band.csv)** —
  Station count, latitude-circle circumference, and stations-per-1,000km-of-circle
  for each 5° band 60-90°N

---

## 📈 Visualizations

### Land Station Snapshot and Evolution
- **[oscar_arctic_stations_comprehensive.png](oscar_arctic_stations_comprehensive.png)** (1.3 MB) —
  9-panel dashboard: geographic map, latitude/country distributions, station types, reporting status
- **[oscar_arctic_stations_regional_focus.png](oscar_arctic_stations_regional_focus.png)** (348 KB) —
  4-panel regional analysis with High Arctic focus, elevation, and sector distribution
- **[oscar_arctic_land_stations_true_evolution.png](oscar_arctic_land_stations_true_evolution.png)** —
  TRUE cumulative active-station count by establishment year (1950-2026),
  accounting for real closures, plus stations established vs. closed per decade
- **[oscar_arctic_station_network_evolution.png](oscar_arctic_station_network_evolution.png)** —
  *(Superseded)* Earlier cumulative-growth chart from the undercounted,
  operational-only snapshot — see the true-evolution chart above instead

### Ocean/Marine Platforms
- **[ecmwf_synop_2m_temp_northpolar_monitoring.png](ecmwf_synop_2m_temp_northpolar_monitoring.png)** -
  ECMWF real-time observation-monitoring reference chart (2m temperature, SYNOP, 90°N/78°N domain)
- **[ecmwf_ship_pressure_global_monitoring.png](ecmwf_ship_pressure_global_monitoring.png)** -
  ECMWF real-time observation-monitoring reference chart (pressure from ship, global domain)
- **[iabp_arctic_buoy_count_trend.png](iabp_arctic_buoy_count_trend.png)** -
  Reconstructed count of distinct IABP drifting buoys reaching ≥60°N per year, 2000-2024
- **[oscar_arctic_marine_platforms_by_status.png](oscar_arctic_marine_platforms_by_status.png)** -
  OSCAR-registered marine/ocean platforms (ships, ice buoys, Argo floats) by type and current status
- **[oceanops_argo_arctic_deployments.png](oceanops_argo_arctic_deployments.png)** -
  Argo floats deployed ≥60°N by year (2001-2026), with cumulative total and current status breakdown

### Geographic Context
- **[oscar_latitude_distribution_with_circle_length.png](oscar_latitude_distribution_with_circle_length.png)** -
  Latitude-distribution histogram with the circumference of the circle of latitude overlaid on a secondary axis
- **[oscar_latitude_circle_length_vs_stations.png](oscar_latitude_circle_length_vs_stations.png)** -
  3-panel band view: station counts by 5° latitude band, circle-of-latitude circumference, and density-adjusted coverage

---

## 🎯 Key Findings

### Land stations
- 1,621 land stations have ever been registered north of 60°N across 11
  countries; 1,505 are currently Operational — ~10-46% more than the bundled
  snapshot export suggested, depending on country.
- The currently-active network has grown from 597 stations in 1980 to 1,338
  today (+124%), but growth has slowed every decade, closures have accelerated
  (32 already in the 2020s vs. 14 in the entire pre-1980 era), and the true
  cumulative total has been roughly flat to slightly declining since ~2020.
- The High Arctic (≥70°N) share of the network has stayed in a narrow 9-12% band
  for over 40 years — a persistent, not recent, monitoring gap — and remains
  real even after adjusting for the shrinking circumference of latitude circles
  toward the pole.
- Russia, Finland, and Canada are the largest contributors; most growth since
  1980 has added stations in the 60-70°N sub-Arctic band, not the High Arctic.

### Ocean/marine platforms
- Drifting sea-ice buoys (International Arctic Buoy Programme): grew from
  near-zero in 2000 to a peak of ~550 distinct buoys reporting from ≥60°N in
  2020, then declined to ~300 by 2024.
- Argo profiling floats: only 694 of 22,393 floats worldwide (3.1%) have ever
  been deployed ≥60°N, concentrated in the Nordic/Barents Seas and Fram Strait
  rather than the central Arctic basin — but deployment has accelerated sharply
  in 2025-2026, the one clearly growing signal found across this analysis.
- Global ship-based pressure observations have grown ~4x since 2000, but that
  growth is driven by automation of existing mid-latitude shipping lanes and
  does not reflect increased coverage of the Arctic Ocean itself.
- OSCAR's own marine/ocean register (1,651 platforms ≥60°N across ships, ice
  buoys, and Argo floats) captures only a fraction of the real international
  fleet (e.g. ~53 of OSCAR's "Sea (on ice)" records are IABP-tagged, vs. ~228
  IABP buoys reported active by NOAA), reflecting fragmented registration across
  many separate national programs.

---

## 📋 Data Dictionary (primary land-station files)

| Column | Type | Description |
|--------|------|-------------|
| Station | String | Official station name |
| Country | String | ISO country name |
| Latitude | Float | WGS84 latitude |
| Longitude | Float | WGS84 longitude |
| Elevation | Float | Meters above sea level |
| Date established | Date | Station installation date |
| Date closed | Date | Station closure date (if applicable) |
| Declared status | String | WMO declared operational status |
| Station type | String | "Land (fixed)", "Sea (mobile)", etc. |
| Programs/Networks | String | Affiliated monitoring networks |
| Reporting Status | String | Assessed operational status |

---

## ✅ Data Quality Notes

- **Coordinates:** 100% valid across all land-station files
- **Geographic bounds:** 60-85°N, -180 to 180°E verified
- **Duplicates:** None found among land stations
- **Establishment dates:** present for ~88% of land stations; reliable for
  historical analysis (unlike mobile marine-platform dates — see
  [ARCTIC_MARINE_OSCAR_REGISTRY.md](ARCTIC_MARINE_OSCAR_REGISTRY.md) for why)
- **Closure dates:** the bundled operational-only snapshot export has almost no
  closure data (1 of 1,127); the comprehensive all-status pull captures 91
  genuine closures, enabling the true-evolution analysis

**Data sources:** WMO OSCAR Surface Database (https://oscar.wmo.int/surface/),
OceanOPS/JCOMMOPS (https://www.ocean-ops.org), International Arctic Buoy
Programme (https://iabp.apl.uw.edu)

---

## 🌐 Resources

- **WMO OSCAR:** https://oscar.wmo.int/surface/
- **OceanOPS/JCOMMOPS:** https://www.ocean-ops.org
- **International Arctic Buoy Programme:** https://iabp.apl.uw.edu
- **FMI Open Data:** https://opendata.fmi.fi/
- **Arctic Council:** https://www.arcticcouncil.org/

---

## 📄 Citation

> Arctic observing network analysis based on the WMO OSCAR Surface Database and
> OceanOPS/JCOMMOPS. Data retrieved from https://oscar.wmo.int/surface/ and
> https://www.ocean-ops.org.
