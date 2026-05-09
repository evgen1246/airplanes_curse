from abc import ABC, abstractmethod
import requests
from typing import List, Dict, Optional, Any
import json
import csv
import os
from datetime import datetime
from functools import total_ordering


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


class Aircraft:
    """Класс, представляющий информацию о самолете"""

    def __init__(self, callsign: str, origin_country: str, velocity: float, baro_altitude: float):
        self._callsign = self._validate_callsign(callsign)
        self._origin_country = self._validate_country(origin_country)
        self._velocity = self._validate_velocity(velocity)
        self._baro_altitude = self._validate_altitude(baro_altitude)

    def _validate_callsign(self, callsign: str) -> str:
        """Валидация позывного"""
        if not isinstance(callsign, str):
            raise TypeError(f"Позывной должен быть строкой, получено: {type(callsign)}")
        if not callsign or not callsign.strip():
            raise ValueError("Позывной не может быть пустым")
        return callsign.strip()

    def _validate_country(self, country: str) -> str:
        """Валидация страны регистрации"""
        if not isinstance(country, str):
            raise TypeError(f"Страна должна быть строкой, получено: {type(country)}")
        if not country or not country.strip():
            raise ValueError("Страна регистрации не может быть пустой")
        return country.strip()

    def _validate_velocity(self, velocity: float) -> float:
        """Валидация скорости полета"""
        if not isinstance(velocity, (int, float)):
            raise TypeError(f"Скорость должна быть числом, получено: {type(velocity)}")
        if velocity < 0:
            raise ValueError(f"Скорость не может быть отрицательной: {velocity}")
        return float(velocity)

    def _validate_altitude(self, altitude: float) -> float:
        """Валидация высоты полета"""
        if not isinstance(altitude, (int, float)):
            raise TypeError(f"Высота должна быть числом, получено: {type(altitude)}")
        if altitude < 0:
            raise ValueError(f"Высота не может быть отрицательной: {altitude}")
        return float(altitude)

    def __eq__(self, other: 'Aircraft') -> bool:
        """Сравнение на равенство по скорости и высоте"""
        if not isinstance(other, Aircraft):
            return NotImplemented
        return (abs(self._velocity - other._velocity) < 0.01 and
                abs(self._baro_altitude - other._baro_altitude) < 0.01)

    def __lt__(self, other: 'Aircraft') -> bool:
        """Сравнение "меньше чем" (сначала по скорости, потом по высоте)"""

        if not isinstance(other, Aircraft):
            return NotImplemented

        # Сравниваем по скорости
        if abs(self._velocity - other._velocity) >= 0.01:
            return self._velocity < other._velocity

        # Если скорости равны, сравниваем по высоте
        return self._baro_altitude < other._baro_altitude

    def compare_velocity(self, other: 'Aircraft') -> int:
        """Сравнение только по скорости"""

        if not isinstance(other, Aircraft):
            raise TypeError(f"Нельзя сравнить с {type(other)}")

        if abs(self._velocity - other._velocity) < 0.01:
            return 0
        return -1 if self._velocity < other._velocity else 1

    def compare_altitude(self, other: 'Aircraft') -> int:
        """Сравнение только по высоте"""

        if not isinstance(other, Aircraft):
            raise TypeError(f"Нельзя сравнить с {type(other)}")

        if abs(self._baro_altitude - other._baro_altitude) < 0.01:
            return 0
        return -1 if self._baro_altitude < other._baro_altitude else 1


    def __str__(self) -> str:
        return (f"Самолет {self._callsign} ({self._origin_country}): "
                f"скорость {self._velocity} м/с, высота {self._baro_altitude} м")