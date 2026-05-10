import pytest
import json
import os
import tempfile

from src.aircraft import Aircraft


@pytest.fixture
def sample_aircraft():
    """Тестовый самолёт"""
    return Aircraft(
        callsign="UAL123",
        origin_country="United States",
        velocity=250.5,
        baro_altitude=10000.0
    )


@pytest.fixture
def sample_aircraft_list():
    """Список тестовых самолётов"""
    return [
        Aircraft("AFL123", "USA", 250.5, 10000.0),
        Aircraft("UAL456", "United States", 300.0, 12000.0),
        Aircraft("DLH789", "Germany", 280.0, 8000.0),
        Aircraft("BAW001", "United Kingdom", 220.0, 9500.0),
        Aircraft("SBI002", "USA", 200.0, 11000.0),
    ]


@pytest.fixture
def sample_nominatim_response():
    """Пример ответа от Nominatim API"""
    return [{
        "boundingbox": ["40.0", "50.0", "-130.0", "-60.0"],
        "display_name": "Test Country"
    }]


@pytest.fixture
def sample_api_response():
    """Ответ от OpenSky API"""
    return {
        'states': [
            ["abc123", "UAL123 ", "United States", 1609459200, 1609459200,
             37.6173, 55.7558, 10000.0, False, 250.5],
            ["def456", "AFL456 ", "USA", 1609459200, 1609459200,
             37.6173, 55.7558, 8500.0, False, 220.0],
        ]
    }


@pytest.fixture
def temp_json_file():
    """Создание временного JSON файла"""
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)

    # Создание пустого JSON файла
    with open(path, 'w', encoding='utf-8') as f:
        json.dump([], f)

    yield path

    # Удаление после тестов
    if os.path.exists(path):
        os.remove(path)
