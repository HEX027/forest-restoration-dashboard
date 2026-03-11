\# 🌳 Forest Restoration Monitoring Dashboard



A full-stack geospatial data platform that tracks reforestation progress across pilot regions in Africa. Built with Python, PostGIS, and Streamlit from raw satellite data ingestion through to an interactive analytics dashboard.



> Amisha Ganvir · github.com/HEX027



---



!\[Dashboard Overview](assets/screenshot\_dashboard.png)



---



\## The Problem



Reforestation programs generate enormous amounts of satellite imagery, but the people running those programs ecologists, NGO staff, government agencies have no easy way to see whether their interventions are actually working. Existing GIS tools require specialist knowledge. Spreadsheets lose the spatial context entirely.



This project bridges that gap: a pipeline that takes raw satellite-derived land cover data, validates it, stores it in a spatial database, and serves it through a dashboard that anyone can use.



---



\## What It Tracks



5 pilot restoration regions across West and East Africa, 2015–2024:



| Region | Country | Biome | Project Type |

|--------|---------|-------|--------------|

| Sahel\_Burkina\_01 | Burkina Faso | Sahel | Reforestation |

| Kenya\_Rift\_01 | Kenya | Dry Forest | Agroforestry |

| Ethiopia\_Highland | Ethiopia | Highland | Natural Regeneration |

| Ghana\_Volta\_01 | Ghana | Savanna | Reforestation |

| Tanzania\_Usambara | Tanzania | Montane Forest | Reforestation |



332,456 ha of tree cover monitored · +62,626 ha net gain · 97.6% data quality score



---



\## Dashboard



!\[Map View](assets/screenshot\_map.png)



The map shows each restoration site color-coded by current tree cover percentage. Green means above 30%, yellow is 20–30%, orange is 12–20%, red is below 12%. Click any marker for a full breakdown.



!\[Charts](assets/screenshot\_charts.png)



The time series shows each region's tree cover trajectory from 2015 to 2024. The bar chart shows net hectares gained or lost per site across the selected period.



!\[Quality Panel](assets/screenshot\_quality.png)



Every record passed through a 7-rule validation pipeline before loading. The quality panel shows per-region scores. The overall score is 97.6% — flagged records are exported to a JSON report, not silently dropped.



---



\## Architecture



Raw Data Sources

│

├── Global Forest Watch API     tree cover change JSON

├── ESA WorldCover 10m          land classification rasters

└── OpenStreetMap               administrative boundaries GeoJSON

│

▼

Python Pipeline

│

├── create\_demo\_data.py    generates pilot region dataset

├── process.py             CRS reprojection + spatial join + metrics

├── validate.py            7-rule automated quality validation

└── load\_db.py             loads into PostgreSQL + PostGIS

│

▼

PostgreSQL + PostGIS

│

├── restoration\_regions    polygon geometries EPSG:4326

└── annual\_metrics         FK to regions, UNIQUE region+year

│

▼

Streamlit Dashboard

│

├── Folium map             CartoDB dark basemap, clickable markers

├── Plotly line chart      tree cover % over time per region

├── Plotly bar chart       net gain ha per region

└── Quality panel          per-region validation scores





---



\## How the Pipeline Works



\*\*CRS handling\*\*

Everything is stored in EPSG:4326 for web map compatibility. Before any area calculation, geometries reproject to UTM Zone 36N (EPSG:32636). Skipping this is the number one source of silent errors in geospatial pipelines — areas come out wrong by a factor of 100 and nothing throws an error.



\*\*Windowed raster reading\*\*

ESA WorldCover tiles are 2GB+ files. Rasterio's windowed reading clips to each region's bounding box before loading pixels into memory. Loading the full file crashes the pipeline on any normal machine.



\*\*Validation pipeline\*\*



| Rule | What it checks |

|------|---------------|

| valid\_coordinates | Lat/lon within geographic bounds |

| valid\_geometry | No self-intersections, auto-repair with make\_valid() |

| no\_missing\_values | Required fields not null |

| no\_duplicates | No duplicate region + year combinations |

| valid\_year\_range | Year between 2010 and 2030 |

| valid\_pct\_range | Tree cover percentage between 0 and 100 |

| area\_consistency | Tree cover ha does not exceed total area ha |



\*\*PostGIS spatial index\*\*

GIST index on the geometry column. ST\_Intersects on 50K features without it takes ~30 seconds. With it, under 50ms.



\*\*Idempotent loading\*\*

ON CONFLICT DO UPDATE means the pipeline can re-run safely without creating duplicates.



---



\## Stack



| Layer | Technology |

|-------|-----------|

| Language | Python 3.11 |

| Geospatial | GeoPandas, Rasterio, Shapely, PyProj, Fiona |

| Database | PostgreSQL 16 + PostGIS 3.x |

| ORM | SQLAlchemy 2.0, psycopg2 |

| Dashboard | Streamlit, Folium, Plotly |



---



\## Running Locally



You need PostgreSQL 16 with PostGIS and conda for GDAL on Windows.



git clone https://github.com/HEX027/forest-restoration-dashboard.git

cd forest-restoration-dashboard

conda create -n forest\_env python=3.11 -y

conda activate forest\_env

conda install -c conda-forge geopandas rasterio shapely pyproj fiona -y

pip install -r requirements.txt

psql -U postgres -c "CREATE DATABASE forest\_restoration;"

psql -U postgres -d forest\_restoration -c "CREATE EXTENSION postgis;"

psql -U postgres -d forest\_restoration -f sql/schema.sql



Update DB\_URL in src/dashboard.py and src/load\_db.py with your credentials, then:



python src/create\_demo\_data.py

python src/process.py

python src/validate.py

python src/load\_db.py

streamlit run src/dashboard.py



---



\## Scaling to Production



\- Dask for parallel raster processing across regions

\- Apache Airflow for pipeline orchestration and scheduling

\- PostgreSQL table partitioning by year

\- pg\_tileserv or GeoServer as a tile server for large geometry datasets



---



\## About



Amisha Ganvir · \[github.com/HEX027](https://github.com/HEX027)

