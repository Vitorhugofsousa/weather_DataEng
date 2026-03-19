# Weather Data Engineering Pipeline: Brazilian Capitals Analysis

This project implements a robust, end-to-end Data Engineering pipeline designed to extract, transform, and load historical weather data for all 27 Brazilian capitals. Utilizing a modern tech stack, the pipeline ensures scalability, reproducibility through Infrastructure as Code (IaC), and interactive data visualization.

## 🚀 Overview

The pipeline automates the collection of historical weather data (temperature, precipitation, humidity, and wind speed) from the **Open-Meteo API**. It processes thousands of records in batches, handling data from the last several years to provide a comprehensive climate analysis of the Brazilian summer seasons.

## 🛠️ Tech Stack

* **Orchestration:** Apache Airflow
* **Infrastructure:** Terraform (IaC)
* **Containerization:** Docker & Docker Compose
* **Database:** PostgreSQL 18
* **Processing:** Python (Pandas, SQLAlchemy, PyArrow)
* **Data Format:** Parquet (Optimized for storage and speed)
* **Visualization:** Streamlit & Plotly
* **Testing:** Pytest (Unit testing with Mocks)

## 📁 Project Structure

```text
.
├── dags/                # Airflow DAG definitions
├── src/                 # Core ETL logic (Extract, Transform, Load)
├── terraform/           # IaC scripts for infrastructure provisioning
├── tests/               # Unit and integration test suite
├── notebooks/           # Exploratory Data Analysis (EDA)
├── config/              # Environment and configuration files (local only)
├── dashboard.py         # Streamlit interactive dashboard
├── docker-compose.yaml  # Container orchestration
├── Dockerfile           # Custom Airflow image definition
├── requirements.txt     # Python dependencies
└── pyproject.toml       # Project metadata and tool configuration