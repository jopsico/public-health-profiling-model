# Brazil Healthcare Analytics: SUS Utilization Dashboard & Clustering Model

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-2CA5E0?style=for-the-badge)
![Openpyxl](https://img.shields.io/badge/Openpyxl-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)

Welcome to my Public Health Data Engineering and Analytics project.

This repository contains an end-to-end data pipeline and an interactive web application that analyzes the utilization of the public healthcare system (SUS - Sistema Único de Saúde) across 184 municipalities in Ceará, Brazil. 

Going beyond basic exploratory data analysis, this project implements an automated ETL process and an unsupervised Machine Learning algorithm (K-Means) to categorize cities into distinct healthcare usage profiles based on attendance volume, demographics, and the Human Development Index (HDI).

## Data Architecture & Pipeline

The project is logically separated into three main layers to ensure modularity, scalability, and reproducibility:

1. **Data Processing & ETL (`tratamento.py`)**: Ingests raw healthcare attendance records and executes rigorous string normalization (Data Quality). The extraction layer actively consumes the IBGE API via `requests` to pull real-time 2022 Census data, and natively parses socio-economic HDI metrics directly from local Excel files using `openpyxl`. Missing values are automatically handled prior to modeling.
2. **Machine Learning Model (`modelo.py`)**: Applies K-Means clustering with feature scaling (`StandardScaler`) to segment municipalities into 4 utilization profiles. The model handles skewed population data using log transformation and was evaluated using inertia and silhouette scores.
3. **Interactive Dashboard (`app.py`)**: A fully responsive Streamlit front-end featuring descriptive statistics, interactive spatial mapping (`px.scatter_map`), and 3D cluster visualizations with strict categorical color mapping.

## Live Demo
You can access the deployed application here: **[Click here to access the live web app!](https://sus-data.streamlit.app/)**

## How to Run Locally

If you want to clone this repository and run the pipeline on your machine, follow these strict execution steps:

**1. Clone the repository and install dependencies:**
```bash
git clone https://github.com/jopsico/public-health-profiling-model.git
cd public-health-profiling-model
py -m pip install -r requirements.txt
```

**2. Run the ETL pipeline:**
*(This will fetch the API data, parse the Excel file, apply data quality rules, and create the enriched dataset)*
```bash
py tratamento.py
```

**3. Train the K-Means model:**
*(This will assign the clusters and generate the final dataset for the dashboard)*
```bash
py modelo.py
```

**4. Launch the Streamlit application:**
```bash
streamlit run app.py
```

## Key Insights & Visualizations
* **Geospatial Analysis:** Interactive map displaying healthcare demand across different regions, allowing the identification of critical hubs.
* **Proportional Ranking:** Normalizes raw attendance volume by municipality population to reveal true utilization intensity.
* **Cluster Profiling:** Identifies 4 distinct structural patterns among cities, helping to understand how HDI and population size affect the pressure on the public healthcare system.

---
*Developed by João Paulo Martins Penha*
