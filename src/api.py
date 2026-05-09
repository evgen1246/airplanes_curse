from abc import ABC, abstractmethod
import requests
from typing import Dict


class AbstractAPIClient(ABC):
    """Абстрактный класс для работы с API сервисами"""

    @abstractmethod
    def connect(self) -> bool:
        """Установка соединения с API"""
        pass

    @abstractmethod
    def get_data(self, **kwargs) -> Dict:
        """Получение данных от API"""
        pass


class NominatimAPI(AbstractAPIClient):
    """Класс для работы с Nominatim OpenStreetMap API"""

    def __init__(self):
        self.base_url = 'https://nominatim.openstreetmap.org/search'
        self.headers = {
            'User-Agent': 'test-app/1.0',
        }
        self._connected = False

    def connect(self) -> bool:
        try:
            # Проверка доступности сервиса
            response = requests.head(self.base_url, headers=self.headers, timeout=5)
            self._connected = response.status_code == 200
            return self._connected
        except requests.RequestException:
            self._connected = False
            return self._connected


def get_data(self, country: str = "", **kwargs) -> Dict:
    """Получение географических координат страны"""

    if not self._connected:
        self.connect()

    params = {
        'country': country,
        'format': 'json',
        'limit': 1,
    }

    response = requests.get(self.base_url, params=params, headers=self.headers)
    response.raise_for_status()

    data = response.json()

    if not data:
        return {}

    bounding_box = data[0].get('boundingbox', [])

    return {
        'country': country,
        'south': float(bounding_box[0]),
        'north': float(bounding_box[1]),
        'west': float(bounding_box[2]),
        'east': float(bounding_box[3]),
    }


class OpenSkyAPI(AbstractAPIClient):
    """Класс для работы с OpenSky Network API"""

    def __init__(self):
        self.base_url = 'https://opensky-network.org/api/states/all'
        self._connected = False

    def connect(self) -> bool:
        try:
            response = requests.head('https://opensky-network.org', timeout=5)
            self._connected = response.status_code == 200
            return self._connected
        except requests.RequestException:
            self._connected = False
            return self._connected

    def get_data(self, lamin: float = 0, lamax: float = 0,
                 lomin: float = 0, lomax: float = 0, **kwargs) -> Dict:
        """Получение информации о самолетах в заданном регионе"""

        if not self._connected:
            self.connect()

        params = {
            'lamin': lamin,
            'lamax': lamax,
            'lomin': lomin,
            'lomax': lomax,
        }

        response = requests.get(self.base_url, params=params)
        response.raise_for_status()

        return response.json()