import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import pytest
import pandas as pd
from src.etl_combined import data_transformation

def test_data_transformation_logic():
    mock_raw_data = {
        "main": {"temp": 300.15, "humidity": 50},
        "dt": 1710432000,
        "name": "Petrolina"
    }

    df = data_transformation(mock_raw_data)
    

    assert isinstance(df, pd.DataFrame), "The output should be a DataFrame"
    assert not df.empty, "The DataFrame should not be empty"
    assert "Petrolina" in df.values, "The city name should be present in the processed data"
    

    if 'temp_celsius' in df.columns:
        assert df.loc[0, 'temp_celsius'] == 27.0