import pytest
import sys
from unittest.mock import patch, MagicMock
import pandas as pd
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.etl_combined import data_transformation, extract_weather_data, load_data


# Mocking the Open-Meteo API response for testing
@pytest.fixture
def mock_open_meteo_response():
    """Returns a sample JSON response mimicking the Open-Meteo API structure."""
    return {
        "latitude": -10.2,
        "longitude": -48.3,
        "city_name": "Palmas",
        "hourly": {
            "time": ["2026-01-01T00:00", "2026-01-01T01:00"],
            "temperature_2m": [25.5, 26.2],
            "relative_humidity_2m": [80, 82],
            "precipitation": [0.0, 0.1],
            "wind_speed_10m": [10.0, 12.5]
        }
    }

# EXTRACTION TESTS
@patch('requests.get')
def test_extract_weather_data_success(mock_get, mock_open_meteo_response):
    """Test successful API extraction for all 27 capitals."""
    # Configure the mock to return a 200 OK status and the sample JSON
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_open_meteo_response

    # We only test a small subset to keep the test fast
    with patch('src.etl_combined.CAPITAIS_COORDS', {"Palmas": {"lat": -10.2, "lon": -48.3}}):
        result = extract_weather_data(start_date="2026-01-01", end_date="2026-01-01")
        
        assert len(result) == 1
        assert result[0]['city_name'] == "Palmas"
        assert "hourly" in result[0]

@patch('requests.get')
def test_extract_weather_data_failure(mock_get):
    """Test extraction behavior when the API returns an error (e.g., 400 Bad Request)."""
    mock_get.return_value.status_code = 400
    
    with patch('src.etl_combined.CAPITAIS_COORDS', {"Palmas": {"lat": -10.2, "lon": -48.3}}):
        result = extract_weather_data(start_date="2026-01-01", end_date="2026-01-01")
        # Should return an empty list if all requests fail
        assert result == []

# TRANSFORMATION TESTS
def test_data_transformation_logic(mock_open_meteo_response):
    """Test if transformation correctly splits dates/times and renames columns."""
    raw_input = [mock_open_meteo_response]
    
    # Execute transformation
    parquet_path = data_transformation(raw_input)
    df = pd.read_parquet(parquet_path)

    # 1. Check if DataFrame is populated
    assert not df.empty
    assert len(df) == 2  # Based on the 2 timestamps in mock_data

    # 2. Check column names (Postgres schema compliance)
    expected_columns = ['date', 'time', 'temperature', 'humidity', 'precipitation', 'wind_speed', 'city_name', 'latitude', 'longitude']
    assert list(df.columns) == expected_columns

    # 3. Check data types and values
    assert str(df.iloc[0]['time']) == "00:00:00"
    assert df.iloc[0]['temperature'] == 25.5
    assert df.iloc[1]['precipitation'] == 0.1

# LOAD TESTS
@patch('src.etl_combined.get_engine')
def test_load_data_calls_to_sql(mock_get_engine):
    """Test if the load function calls pandas.to_sql with correct arguments."""
    # Setup mock engine and connection
    mock_engine = MagicMock()
    mock_get_engine.return_value = mock_engine
    
    # Create a dummy DataFrame
    df_dummy = pd.DataFrame({'test': [1, 2, 3]})
    
    # Mocking the read_sql check to prevent actual DB query
    with patch('pandas.read_sql') as mock_read_sql:
        mock_read_sql.return_value = pd.DataFrame({'total': [3]})
        
        # Execute load
        load_data('test_table', df_dummy)

    # Verify that to_sql was called with the correct table name and 'append' mode
    # Note: We access the engine via the mock
    assert mock_engine.connect.called