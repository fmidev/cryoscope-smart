# XGBoost for air and soil temperature ML model in CryoSCOPE WP4

# Goals

# Training target variables 

Two models (air temp and soil temp) combining target variables from several sources

sources for each
air temp
soil temp 

|Target|Source 1|Source 2|Source 3|
|:-|:-|:-|:-|
|2m air temperature|||
| Soil temperature (top level)|||

# notes below

Muistarit: 
Kiinnostaa 2m lämpötila ja stl1 opetustavoitteena (output tavoite). Mitä opetustargetteja siihen kerätään: 
- yhdistelmä 3sta eri lähteestä opetustarget
- tiesääasemat ja niiden road service temp (stl1 vertautuva) ja air temp mittaukset 1000 asemaa suomessa, mutta tehdään suoraan alueelle mitä Rasmuksella ~400 -> aineisto valmiina vain siellä pitää uudelleen koostaa lähimmän, tunnin era5 ja era5l on haettu jostain, jossain on havainnot tunnin välein ja era5 kamat tunnin välein jo haettuna  
- soiltemp db havainnot euroopasta ja mitä meillä jo on 2500. Ei ole ilman lämpötila havaintoja välttämättä kohteista mukana. 15cm maan yllä on jo lähempänä 2m lämpötilaa kuin maanpinnnan., validointiin sitten Joonas etc 
- havaintoasemapaikat (aws asemat avs asemat) joista ilmanlämpötilamittaus, käytetäänkin satelliittihavaintoja niissä pisteissä, yksin oli huono ja paljon härödataa, opetusmalli niin että on semmosiakin lähteitä missä ei ole häröä ja datan runsaus korvaa häröt, niille hetkille havaintodatat uusiksi koko päivän tiedot. Havaintoasemat paikat ne jotka osuu alueelle missä satkudataa on (helsinki, tampere). 
trs on joku tiesäälämpötila
2 tulosta erikseen
- vektoriopetus
- koetetaan ratkaista yhtäaikaa
opetusaineistot kasvaa kun yhdistetaan monen aineiston aineksia ja yhtenäismalli 
soiltemp malli pelikkä soiltemp asemilla hyvä
tiesääasemat tunnin välein 
päiväsignaali opetettua 
Katso Rasmuksen se malli 
AMSR, SSMI SSMI YLI LAIDAN, AMSR Yleinen siivous että jos älyttömän kylmää (droppaa kahden mittauksen v'lillä valtavasti niin suodatetaan pois edellisen ja seuraavan mittauksen vertailu että droppaa 30 asteen erolla sen kylmemmän tai 20 astetta) 
Lopputuloksen kannalta (aurora hankkeessa) että me validoidaan niillä satkudatatuotteilla meidän hommia. Jos käytetään tätä opetukseen ja validoidaan tai ei käytetä ja validoidaan niin hyvyyden vertailua (2 ensimmäistä havaintoaineistoa opetus ja sitten 3 vaan validointiin, toinen malli 3lla datalla ja validoidaan).Mikon hommaa.

# Air + Soil Temperature Models — Working Notes (CryoSCOPE)

Goal: an ML model that predicts **2 m air temperature** and **stl1** (ERA5/ERA5‑Land soil temperature level 1, 0–7 cm) as the training/output targets. The work reuses and improves two earlier FMI model lineages — the Aurora UHI air‑temperature model and the HarvesterDestinE soil‑temperature model. Both work on training stations but fail to generalise; CryoSCOPE is about fixing those failure modes. All models are XGBoost gradient boosting, tuned with Optuna, validated by year‑sampled K‑fold. Owners: Rasmus (road‑weather / station model), Joonas (validation), Mikko (Aurora validation strategy, WP4).

---

## 1. Lineage — the two earlier versions and where they fall short

This is the key context: what already exists, and exactly where it isn't good enough.

### v1 — HarvesterDestinE soil‑temperature model (DE_370d, Jan 2024)

The earlier **soil‑temperature‑only** model. Target = **Stl1x** (soil temp level 1, 0–7 cm), predictand = SoilTemp‑database near‑surface soil observations.

- Trained on **2486 SoilTemp points across Europe**, filtered to **−5 cm sensor height only** (most observations sit there). Period 2015–2022; validation years 2019 & 2021, rest for training.
- Predictors: Copernicus DEM terrain, IFS terrain stats, ~56 ERA5‑Land variables (28 finally used), LSASAF LST (night `sktn` / day `sktd`), Soilgrids, and a day‑of‑year soil‑temp climatology. Key idea: use **night** skin temperature to mimic soil (night driven by soil heat, day by sun).
- Result: **XGBoost RMSE 2.25 K** (MAE 1.62 K); LightGBM 2.30 K (MAE 1.68 K) → XGBoost chosen. For reference the pure IFS baseline (Albergel 2015) is RMSE 2.54 K at 5 cm in Europe.

**Where it fails / is not good enough:**
- **Over‑reliant on latitude and longitude** — clear lat/lon bands visible in the output maps; day‑of‑year, lat and lon were the top predictors. Quality deemed not good enough.
- **stl1x too cold in general** — large negative offset vs observed night LST; the ML effect is too strong.
- **Too tied to climatological boundaries** — can't alert for extremes, which is exactly what a trafficability service needs.
- **1 km production for ensembles infeasible** — float32 structures too large; needs 8/16‑bit packing. Only ~4 km / single‑member (Extremes DT) was practical.
- Downscales accurately *for the included training stations* but generalisation is poor.

**Improvement levers already identified:** 2299 new stations received (more in Finland) + ~9 M more time‑series observations; add sensor depths beyond −5 cm; engineer features strong enough to overpower lat/lon; test the model with vs without lat/lon.

### v2 — Aurora D4.1 UHI model (May 2026)

The more recent **two‑step air‑temperature / skin‑temperature** model for Urban Heat Islands over the Fenno‑Baltic 1000×1000 km domain.

- **Step 1 (gap‑filler):** XGBoost predicts skin temperature (SKT/LST); target = EO LST from **three products** (MODIS CCI 0.01°, SSM/I CCI 0.25° passive microwave, LSASAF METOP TIR), plus a feature telling the model which product a row came from. Satellite LST is the *validation* here.
- **Step 2 (air temp):** XGBoost predicts 2 m air temperature; predictand = **station air‑temperature measurements**, with the gap‑filled SKT as a key feature (wants the high‑res EO signal in).
- Predictors (67 in production): Copernicus DEM (DTM with forest height subtracted, slope/aspect/TWI), IFS terrain stats at 333 m, ~50 ERA5/ERA5‑Land surface + 3‑pressure‑level variables, and temporal features (day‑of‑year, month, closest hour, minute).
- Training stations: Finnish + Estonian weather + road‑weather stations. First **110** (Helsinki + Tampere) → lat/lon overreliance again → expanded to **413** in S. Finland + Estonia, which proved sufficient. Series up to 20 yr, up to 6 values/day cloud‑free (realistically ~2/day, since only SSM/I is available daily).
- Result: SKT model **RMSE ~1.42 °C**; 2 m air model **sub‑0.9 °C**. SHAP top features: ERA5‑L `t2`, pressure‑level temps, `stl1`, tmax/tmin, and temporal features; SKT ranks high in the air model (good).

**Where it fails / is not good enough — the "Helsinki syndrome":**
- **SSM/I passive‑microwave LST has semi‑frequent extreme cold outliers** that QC didn't catch. Since SSM/I is the bulk of the training data (it's the only cloud‑immune, always‑available source), the model learned the cold bias and **reversed the UHI signal** — Helsinki came out *colder* than its surroundings.
- Some **LSASAF cold outliers** too (imperfect cloud mask → cloud‑top instead of land‑surface temperature), but rarer. The **MODIS CCI** product was clean.
- **Large systematic error** in the 2019–2024 production check (road‑surface in‑situ vs ML SKT): RMSE ~9 K, MAE ~6.5–7.9 K, with MAE ≈ mean error → systematic, not random. The lat/lon problem was largely solved by the 413 stations; the SSM/I outliers are the killer.
- Production was run 2024→backward and **stopped at 2018** when the Helsinki problem was spotted; the LST→2 m air step was omitted. 7 years of SKT were produced before the issue surfaced.

**Fix plan (Aurora next steps, feeds straight into CryoSCOPE):** retrain on a dataset that cleans the SSM/I and LSASAF cold outliers; backfill the reduced training set using New Space CCM LST scenes (Constellr 30 m for Helsinki/Tampere/Pori, Ororatech 300 m) and add their station locations; validate against the New Space TIR products and against Helsinki/Tampere city weather monitoring (since 2023). Publication planned.

---

## 2. Targets (model outputs)

Two predictands: **2 m air temperature** and **stl1**. In CryoSCOPE these are pursued together, reusing the air‑temp side from Aurora (v2) and the soil side from HarvesterDestinE (v1). Training labels come from a **combination of three observation sources**.

---

## 3. Training‑target sources

### Source 1 — Road weather stations (tiesääasemat)
- Road‑surface temperature (`trs` / road service temp — the **stl1‑comparable** label) plus air‑temperature measurements.
- ~1000 stations in Finland, but the ready set is the **~400 in Rasmus's area** (= the 413 S. Finland + Estonia stations from Aurora v2). Dataset exists there; needs nearest‑gridpoint **re‑composition**, hourly, with ERA5 / ERA5‑Land already fetched and aligned hourly to the observations.
- → reuse Rasmus's model; road stations hourly; diurnal/daily signal already trained.

### Source 2 — SoilTemp database
- European soil‑temperature observations, ~2500 (the 2486 from v1). Often **no air‑temperature observation** at the site. A sensor ~15 cm above ground is already closer to 2 m air temp than the surface is.
- Role: leaning toward **validation** (Joonas). A SoilTemp‑only model (v1) fits the training stations well but is the one with the lat/lon + too‑cold problems, so treat its "good" result cautiously.

### Source 3 — AWS locations + satellite observations
- AWS air‑temp sites combined with passive‑microwave satellite LST (**AMSR / AMSR2, SSM/I**), restricted to AWS points inside satellite coverage (Helsinki, Tampere).
- Noisy alone — full of garbage ("härö") — this is literally the **SSM/I cold‑outlier source** behind the Helsinki syndrome. Strategy: keep clean sources in the mix so **data abundance compensates**, and re‑pull whole‑day observation data for affected timestamps.

---

## 4. Predictors (shared across models)
Copernicus DEM terrain (DTM with forest height subtracted; slope, aspect, TWI) · IFS terrain statistics at 333 m (urban / high‑/low‑vegetation / lake fractions, lake depth, soil type) · ~50 ERA5 / ERA5‑Land variables (surface + three pressure levels) · temporal features for **diurnal + annual signal** (day‑of‑year, month, closest hour, minute). v1 additionally used a day‑of‑year soil‑temp climatology and night LST to proxy soil.

---

## 5. Modelling approaches
- **Separate vs joint:** v1 and v2 solved soil and air sequentially (v2: SKT → 2 m air). The CryoSCOPE question is whether to predict stl1 and 2 m air **as a vector / jointly** ("vektoriopetus" / "ratkaista yhtäaikaa") vs two separate models.
- **SoilTemp‑only baseline** retained (v1).
- Combining ingredients from multiple datasets into one **unified model** grows the training set and should reduce single‑source overfitting.

---

## 6. QC / cleaning on satellite data (AMSR, SSM/I) — the critical fix
A **despike filter** on the passive‑microwave LST: compare each value to its previous and next neighbour and drop anomalous cold drops — discard the colder point if it falls roughly **30 °C** (or **20 °C**) below its neighbours. This directly targets the SSM/I outliers that caused the Helsinki syndrome. *"Quality data in, quality model out"* is the lesson from Aurora.

> Open: pin down the two thresholds (when 30 vs 20 °C applies; absolute vs relative to local trend), and whether LSASAF gets the same treatment (it had rarer cloud‑mask cold outliers).

---

## 7. Validation experiment (Mikko / Aurora)
Validate against satellite LST products. Designed "goodness" comparison:
- **Model A:** train on sources **1 + 2**, hold out source **3** for validation.
- **Model B:** train on all **three (1 + 2 + 3)**, then validate.
- Question: does folding the satellite/AWS data into *training* help, or is it better kept out and used only for validation?
- Additional independent validation tracks: New Space CCM TIR scenes (Constellr / Ororatech), Helsinki/Tampere city weather monitoring (since 2023), and — from v1 — NASA GLDAS for extremes.

---

## 8. What CryoSCOPE improves (summary of open decisions)
- **Beat the lat/lon overreliance** (both v1 and the early v2) via more/denser stations and stronger feature engineering; test with vs without lat/lon.
- **Clean SSM/I (and LSASAF) cold outliers** before training — the despike rule above; this is the single biggest fix.
- **Resolve the too‑cold soil bias** in stl1x (v1).
- **Decide joint vs separate** prediction of stl1 and 2 m air.
- **Confirm SoilTemp's role** — training (per the A/B design) vs validation (the "Joonas" note); the notes pull both ways.
- **Confirm ERA5/ERA5‑Land provenance** ("haettu jostain") and consistent hourly obs↔reanalysis alignment across all three sources.
- **Add data** identified for v1: 2299 new stations (Finland‑heavy) + ~9 M observations; sensor depths beyond −5 cm.
- **Production feasibility** at 1 km for ensembles — 8/16‑bit packing instead of float32.