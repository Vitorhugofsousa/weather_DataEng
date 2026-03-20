## Technical Report: Climate Data Engineering (Brazilian Capitals)
This project was developed with the goal of exercising technical skills in data orchestration and infrastructure as code, and has evolved into a technical auditing platform for historical climate analysis of the 27 Brazilian capitals. The core objective was to move from simple, ad-hoc collection to an automated system capable of processing massive volumes of data—with thousands of records per execution—to achieve data integrity and ease of visual consumption.

### What does the project do?
Through an ETL pipeline, a mass data extraction is performed from the Open-Meteo API, containing various climate metrics. The scope was defined to extract hourly weather data for all Brazilian capitals during the 2025/2026 summer to enable direct comparison between capitals, identify flow differences, and compare temperature development throughout the season.
Accordingly, I developed a Python notebook to execute the end-to-end ETL process: extracting from the API, performing all necessary transformations to normalize the data, and ingesting it into the database, enabling consumption by a Streamlit dashboard.

<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/293b294d-c6e5-47ff-b877-7ae824c8a1e7" />

## Architecture and Technical Capability
The solution was designed to be fully reproducible and isolated, utilizing market best practices:

Infrastructure as Code (IaC): Use of Terraform and Docker to provision volumes and networks, ensuring the environment is identical on any machine by using code containerization to form a single unit.

End-to-End Orchestration: Apache Airflow managing the pipeline, with support for dynamic parameters for "time travel" (collecting any historical period).

High-Performance Storage: Utilization of Parquet as an intermediary layer to achieve compression efficiency, and PostgreSQL 18 as the final database, operating with batch insertions to support large volumes without memory bottlenecks caused by the mass extraction of tens/hundreds of thousands of records in a short time interval.

Analytical Interface: Streamlit dashboard optimized with data caching to facilitate the data query process in an automated dashboard.

## Critical Decisions and Evolution
The project went through strategic development points that defined its current maturity:

1. Data Scalability: OpenWeather vs. Open-Meteo
The most impactful decision was the migration from the OpenWeather API to Open-Meteo. I initially used the OpenWeather API, which limited historical data collection and required an API key that restricted the number of requests with low limits, preventing massive information gathering. Due to this barrier, I decided to switch to the Open-Meteo API, which allows for a massive hourly extraction of entire years in a single network call, free of charge and with higher precision.

2. Granularity Refinement (Date/Time)
Unlike simple models that save only the timestamp, I opted to logically separate Date and Time in the database to facilitate data queries and enable hourly comparisons for each city. This allows for granular analysis in the Dashboard (e.g., comparing temperatures specifically at noon between two cities), facilitating insight generation without heavy processing.

3. Safety Mode (Dry Run)
I implemented a Dry Run mechanism via Airflow Params, which allows testing the integrity of new historical extractions (such as summers from 10 years ago) without the risk of corrupting or duplicating data in the production database before final validation.

## Capabilities and Generated Insights
Currently, the system delivers a deep analytical view of the Brazilian urban climate, analyzing extremes by identifying temperature records and accumulated precipitation peaks across the national territory. The visual interface has the capacity to confront thermal and rainfall behavior between two capitals simultaneously (e.g., the contrast between the dry season in Boa Vista and the rain in Curitiba during the same period).
 The dashboard processes over 50,000 records smoothly, offering trend metrics (averages) and daily heat/cold peaks.

## Tech Stack
 - Language: Python (Pandas, SQLAlchemy)
 - Infrastructure: Docker, Terraform
 - Orchestration: Apache Airflow
 - Database: PostgreSQL 18
 - Visualization: Streamlit, Plotly

Quality: Pytest (Mocks for total isolation)

Developed by: Vitor Hugo Ferreira Sousa
