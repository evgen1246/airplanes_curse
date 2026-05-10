from abc import ABC, abstractmethod
from typing import Any, Dict, List

import requests


class AbstractAPIClient(ABC):
    """Абстрактный класс для работы с API сервисами"""

    @abstractmethod
    def connect(self) -> bool:
        """Установка соединения с API"""
        pass

    @abstractmethod
    def get_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Получение данных от API"""
        pass


class NominatimAPI(AbstractAPIClient):
    """Класс для работы с Nominatim OpenStreetMap API"""

    def __init__(self) -> None:
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {"User-Agent": "tests-app/1.0"}
        self._connected = False

    def connect(self) -> bool:
        try:
            response = requests.head(self.base_url, headers=self.headers, timeout=5)
            self._connected = response.status_code == 200
            return self._connected
        except requests.RequestException:
            self._connected = False
            return self._connected

    def get_data(self, country: str = "", **kwargs: Any) -> Dict[str, Any]:
        """Получение географических координат страны"""
        if not self._connected:
            self.connect()

        params: Dict[str, Any] = {"country": country, "format": "json", "limit": 1}
        response = requests.get(self.base_url, params=params, headers=self.headers)
        response.raise_for_status()

        data = response.json()
        if not data:
            return {}

        bounding_box = data[0].get("boundingbox", [])
        return {
            "country": country,
            "south": float(bounding_box[0]),
            "north": float(bounding_box[1]),
            "west": float(bounding_box[2]),
            "east": float(bounding_box[3]),
        }


class OpenSkyAPI(AbstractAPIClient):
    """Класс для работы с OpenSky Network API"""

    def __init__(self) -> None:
        self.base_url = "https://opensky-network.org/api/states/all"
        self._connected = False

    def connect(self) -> bool:
        try:
            response = requests.head("https://opensky-network.org", timeout=5)
            self._connected = response.status_code == 200
            return self._connected
        except requests.RequestException:
            self._connected = False
            return self._connected

    def get_data(
        self, lamin: float = 0, lamax: float = 0, lomin: float = 0, lomax: float = 0, **kwargs: Any
    ) -> Dict[str, Any]:
        """Получение информации о самолетах в заданном регионе"""
        if not self._connected:
            self.connect()

        params: Dict[str, float] = {"lamin": lamin, "lamax": lamax, "lomin": lomin, "lomax": lomax}
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()

        result: Dict[str, Any] = response.json()
        return result


class AeroplanesAPI:
    """
    Основной класс для работы с API самолетов.
    Объединяет Nominatim и OpenSky API.
    """

    def __init__(self) -> None:
        self.nominatim_api = NominatimAPI()
        self.opensky_api = OpenSkyAPI()
        self._aeroplanes: List[List[Any]] = []

    def get_aeroplanes(self, country: str) -> List[List[Any]]:
        """Получение информации о самолетах над указанной страной"""
        country_data = self.nominatim_api.get_data(country=country)

        if not country_data:
            print(f"Страна '{country}' не найдена")
            self._aeroplanes = []
            return self._aeroplanes

        # Получаем данные о самолетах
        aircraft_data = self.opensky_api.get_data(
            lamin=country_data["south"],
            lamax=country_data["north"],
            lomin=country_data["west"],
            lomax=country_data["east"],
        )

        self._aeroplanes = aircraft_data.get("states", [])
        return self._aeroplanes
