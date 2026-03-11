\# 🌳 Forest Restoration Monitoring Dashboard



A full-stack geospatial data platform that tracks reforestation progress across pilot regions in Africa. Built with Python, PostGIS, and Streamlit — from raw satellite data ingestion through to an interactive analytics dashboard.



> MPS Data Science · University of Maryland Baltimore County (UMBC)

> Built by Amisha Ganvir · github.com/HEX027



---



!\[Dashboard Overview](assets/screenshot\_dashboard.png)



---



\## The Problem



Reforestation programs generate enormous amounts of satellite imagery, but the people running those programs — ecologists, NGO staff, government agencies — have no easy way to see whether their interventions are actually working. Existing GIS tools require specialist knowledge. Spreadsheets lose the spatial context entirely.



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



\*\*332,456 ha\*\* of tree cover monitored · \*\*+62,626 ha\*\* net gain · \*\*97.6%\*\* data quality score



---



\## Dashboard



!\[Map View](assets/screenshot\_map.png)



The map shows each restoration site color-coded by current tree cover percentage. Green means above 30%, yellow is 20–30%, orange is 12–20%, red is below 12%. Click any marker for a full breakdown.



!\[Charts](assets/screenshot\_charts.png)



The time series shows each region's tree cover trajectory from 2015 to 2024. The bar chart shows net hectares gained or lost per site across the selected period.



!\[Quality Panel](assets/screenshot\_quality.png)



Every record in the database passed through a 7-rule validation pipeline before loading. The quality panel shows per-region scores. The overall score is 97.6% — flagged records are exported to a JSON report, not silently dropped.



---



\## Architecture

