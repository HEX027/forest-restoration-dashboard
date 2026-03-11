\# 🌳 Forest Restoration Monitoring Dashboard



An end-to-end geospatial data platform tracking reforestation progress across pilot regions in Africa using satellite-derived land cover data, spatial databases, and an interactive analytics dashboard.



\## Project Overview



This project builds a full data pipeline for monitoring forest restoration initiatives across 5 pilot regions in West and East Africa (Burkina Faso, Kenya, Ethiopia, Ghana, Tanzania). It ingests satellite imagery metadata, processes geospatial raster and vector data, validates data quality automatically, stores spatial features in a PostGIS database, and serves insights through a professional Streamlit dashboard.



Built as part of MPS Data Science coursework at UMBC.



\## Live Dashboard Features



\- Interactive Folium map with color-coded restoration sites and clickable popups

\- Tree cover trend lines from 2015 to 2024 per region

\- Net gain bar chart showing hectares gained or lost per site

\- Data quality panel with validation scores

\- Regional summary table with start, end, delta, peak, and net gain

\- CSV export to download filtered data



\## Tech Stack



\- Language: Python 3.11

\- Geospatial: GeoPandas, Rasterio, Shapely, PyProj

\- Database: PostgreSQL 16 + PostGIS 3.x

\- ORM: SQLAlchemy, psycopg2

\- Dashboard: Streamlit, Folium, Plotly

\- Version control: Git + GitHub



\## Key Metrics



\- Pilot regions monitored: 5

\- Years of data: 2015 to 2024

\- Total records: 50

\- Data quality score: 97.6%

\- Validation rules: 7

\- Total tree cover tracked: 332,456 ha

\- Net gain 2015 to 2024: +62,626 ha



\## Project Structure



forest\_project/

├── src/

│   ├── create\_demo\_data.py

│   ├── process.py

│   ├── validate.py

│   ├── load\_db.py

│   └── dashboard.py

├── sql/

│   └── schema.sql

├── data/

│   ├── raw/

│   └── processed/

├── requirements.txt

├── .gitignore

└── README.md



\## Setup



1\. Clone the repo: git clone https://github.com/HEX027/forest-restoration-dashboard.git

2\. Create environment: conda create -n forest\_env python=3.11 -y

3\. Install geospatial libs: conda install -c conda-forge geopandas rasterio shapely -y

4\. Install rest: pip install -r requirements.txt

5\. Set up PostgreSQL and update DB\_URL in dashboard.py and load\_db.py

6\. Run pipeline: python src/create\_demo\_data.py then process.py then validate.py then load\_db.py

7\. Launch: streamlit run src/dashboard.py



\## Author



Amisha Ganvir

GitHub: https://github.com/HEX027

