import requests
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_weather_data(url:str) -> list:
    response = requests.get(url)
    data = response.json()


    if response.status_code != 200:
        logging.error(f"Failed to fetch data. Status code: {response.status_code}, Response: {data}")
        return []

    if not data:
        logging.warning("No data found in the response.")
        return []

    output_path = Path("data/weather_data.json")
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)


    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)
    

    print(f"Data extracted and saved to {output_path}")
    return data

