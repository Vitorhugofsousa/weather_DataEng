# Weather Data Engineering Pipeline: Brazilian Capitals Analysis

[![Python](https://img.shields.io/badge/Python-yellow.svg)](https://www.python.org/)
[![Airflow](https://img.shields.io/badge/Airflow-red.svg)](https://airflow.apache.org/)
[![Docker](https://img.shields.io/badge/Docker-blue.svg)](https://docker.org/)
[![Terraform](https://img.shields.io/badge/Terraform-purple.svg)](https://www.terraform.io/)
[![PostgreSQL](https://img.shields.io/badge/Postgres_18-blue.svg)](https://www.postgresql.org/)
[![Git](https://img.shields.io/badge/Git-orange.svg)](https://www.github.com/)

This project implements a robust, end-to-end Data Engineering pipeline designed to extract, transform, and load historical weather data for all 27 Brazilian capitals. Utilizing a modern tech stack, the pipeline ensures scalability, reproducibility through Infrastructure as Code (IaC), and interactive data visualization.

## 🏗️ Architecture
The data flow follows a standard medallion-like approach, though optimized for a local environment:
1. **Infrastructure (IaC):** Terraform provisions Docker volumes and network.
2. **Extraction:** Airflow DAG fetches batch data from **Open-Meteo API** (No API Key required).
3. **Transformation:** Data is cleaned, timezones are adjusted, and schema is flattened using **Pandas**.
4. **Storage:** Intermediate data is stored in **Parquet** format before being loaded into **PostgreSQL 18** using chunk-based insertion.
5. **Consumption:** An interactive **Streamlit** dashboard queries the database for insights.
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
```

## ⚙️ Getting Started
Prerequisites
 - Docker & Docker Compose installed.
 - Terraform installed.
 - Python installed.
 - Postgres 18 installed.
 - An IDE from your  preference.


### 1. Infrastructure Provisioning for setup
Before starting the services, use Terraform to set up the necessary network and volume structures.

in bash use the following commands:

```text
 cd terraform
 terraform init
 terraform apply
```
### 2. After Environment Setup
Create a .env file inside the config/ directory. Use the following template:

Snippet de código 
```text
user=your_db_username
password=your_db_password
database=weather_data
host=host.docker.internal
```

### 3. Deployment
Build and start the Airflow environment and the database:

In Bash use the following commands:
```text
docker-compose up --build
```

### 4. Executing the Pipeline
Access the Airflow Webserver at http://localhost:8081.

Search for the weather_dag and run it.

Trigger DAG w/ Config: Use the UI to specify start_date, end_date, and the dry_run flag 
 - (Set dry_run to False for actual database insertion).

## 📊 Interactive Dashboard
The dashboard allows for deep dives into the extracted historical data. To launch it locally:

In Bash use the following command:
```text
streamlit run dashboard.py
```

#### Features included:

Global Records: Hottest/Coldest absolute records and precipitation peaks.

Switchable Rankings: View Top 5 Hottest or Coldest cities by average temperature.

Side-by-Side Comparison: Compare temperature and rainfall trends between two capitals over the chosen period.

## 🧪 Quality Assurance & Testing
The project includes a comprehensive testing suite to ensure the ETL logic remains intact across changes. We use Mocks to simulate API responses and Database connections.

Run all tests with:

In Bash use the following command:
```text
pytest tests/ -v
```

## 🔑 Key Features
Time-Travel Enabled: Configure any historical date range via Airflow parameters to fetch data from previous years.

Dry Run Support: Integrated safety mode to test the entire pipeline (Extraction + Transformation) without affecting production data.

Memory Efficiency: Uses Parquet for intermediate storage and chunk-based loading for PostgreSQL to handle datasets with millions of rows.

Brazilian Timezone Alignment: Automatic handling of local time offsets for all capital coordinates.

**Developed by Vitor Hugo Ferreira Sousa**
