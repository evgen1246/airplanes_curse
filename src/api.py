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

@total_ordering
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

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для сохранения"""
        return {
            'callsign': self._callsign,
            'origin_country': self._origin_country,
            'velocity': self._velocity,
            'baro_altitude': self._baro_altitude,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Aircraft':
        """Создание объекта из словаря"""
        return cls(
            callsign=data['callsign'],
            origin_country=data['origin_country'],
            velocity=data['velocity'],
            baro_altitude=data['baro_altitude'],
        )

    @classmethod
    def from_api_response(cls, state: List[Any]) -> 'Aircraft':
        """Создание объекта из ответа OpenSky API"""
        callsign = state[1].strip() if state[1] else "UNKNOWN"
        origin_country = state[2] if state[2] else "Unknown"
        velocity = float(state[9]) if state[9] is not None else 0.0
        baro_altitude = float(state[7]) if state[7] is not None else 0.0

        return cls(
            callsign=callsign,
            origin_country=origin_country,
            velocity=velocity,
            baro_altitude=baro_altitude,
        )

    def __str__(self) -> str:
        return (f"Самолет {self._callsign} ({self._origin_country}): "
                f"скорость {self._velocity} м/с, высота {self._baro_altitude} м")


class AbstractFileManager(ABC):
    """Абстрактный класс для работы с хранилищем данных"""

    @abstractmethod
    def add_aircraft(self, aircraft: Aircraft) -> None:
        """Добавление информации о самолете"""
        pass

    @abstractmethod
    def get_aircraft_by_country(self, country: str) -> List[Aircraft]:
        """Получение самолетов по стране регистрации"""
        pass

    @abstractmethod
    def delete_aircraft(self, callsign: str) -> None:
        """Удаление информации о самолете"""
        pass

    @abstractmethod
    def get_all_aircraft(self) -> List[Aircraft]:
        """Получение всех самолетов"""
        pass


class JSONFileManager(AbstractFileManager):
    """Класс для работы с JSON-файлом"""

    def __init__(self, filename: str = "aircraft_data.json"):
        self.filename = filename
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Создание файла, если он не существует"""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _load_data(self) -> List[Dict]:
        """Загрузка данных из файла"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_data(self, data: List[Dict]) -> None:
        """Сохранение данных в файл"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_aircraft(self, aircraft: Aircraft) -> None:
        """Добавление самолета в файл"""
        data = self._load_data()
        aircraft_dict = aircraft.to_dict()
        self._save_data(data)
        found = False
        for i, item in enumerate(data):
            if item.get('callsign') == aircraft.callsign:
                data[i] = aircraft_dict
                found = True
                break

        if not found:
            data.append(aircraft_dict)

        self._save_data(data)

    def get_aircraft_by_country(self, country: str) -> List[Aircraft]:
        """Получение самолетов по стране регистрации"""
        data = self._load_data()
        result = []

        for item in data:
            if item.get('origin_country', '').lower() == country.lower():
                result.append(Aircraft.from_dict(item))

        return result

    def delete_aircraft(self, callsign: str) -> None:
        """Удаление самолета по позывному"""
        data = self._load_data()
        data = [item for item in data if item.get('callsign') != callsign]
        self._save_data(data)

    def get_all_aircraft(self) -> List[Aircraft]:
        """Получение всех самолетов из файла"""
        data = self._load_data()
        return [Aircraft.from_dict(item) for item in data]


class DatabaseFileManager(AbstractFileManager):
    """Заглушка для будущей интеграции с базой данных"""

    def __init__(self, connection_string: str = ""):
        self.connection_string = connection_string
        print("Warning: DatabaseFileManager is not implemented yet")

    def add_aircraft(self, aircraft: Aircraft) -> None:
        raise NotImplementedError("Database integration not implemented yet")

    def get_aircraft_by_country(self, country: str) -> List[Aircraft]:
        raise NotImplementedError("Database integration not implemented yet")

    def delete_aircraft(self, callsign: str) -> None:
        raise NotImplementedError("Database integration not implemented yet")

