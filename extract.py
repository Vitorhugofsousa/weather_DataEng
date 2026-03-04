import requests
import json
from pathlib import Path


def extract_weather_data(url:str) -> list:
    response = requests.get(url)
    data = response.json()


    if response.status_code != 200:
        raise Exception(f"Failed to found data: {response.status_code} - {response.text}")
        return []

    output_path = Path("data/weather_data.json")
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)


    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)
    return data

