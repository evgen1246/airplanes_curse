from abc import ABC, abstractmethod
import requests
from typing import List, Dict, Any
import json
import os
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


class AircraftTracker:
    """Основной класс для отслеживания самолетов"""

    def __init__(self, storage: AbstractFileManager = None):
        self.nominatim_api = NominatimAPI()
        self.opensky_api = OpenSkyAPI()
        self.storage = storage or JSONFileManager()

    def fetch_aircraft_by_country(self, country: str) -> List[Aircraft]:
        """Получение самолетов над указанной страной"""

        # Получаем координаты страны
        country_data = self.nominatim_api.get_data(country=country)

        if not country_data:
            print(f"Страна '{country}' не найдена")
            return []

        # Получаем данные о самолетах
        aircraft_data = self.opensky_api.get_data(
            lamin=country_data['south'],
            lamax=country_data['north'],
            lomin=country_data['west'],
            lomax=country_data['east'],
        )

        # Преобразуем в объекты Aircraft
        aircraft_list = []
        if aircraft_data.get('states'):
            for state in aircraft_data['states']:
                try:
                    aircraft = Aircraft.from_api_response(state)
                    aircraft_list.append(aircraft)
                    # Сохраняем в хранилище
                    self.storage.add_aircraft(aircraft)
                except (ValueError, TypeError) as e:
                    print(f"Ошибка при создании объекта Aircraft: {e}")

        return aircraft_list

    def get_top_by_altitude(self, n: int = 10) -> List[Aircraft]:
        """Получение топ N самолетов по высоте"""
        all_aircraft = self.storage.get_all_aircraft()

        # Сортируем по высоте (по убыванию)
        sorted_aircraft = sorted(all_aircraft,
                                 key=lambda x: x.baro_altitude,
                                 reverse=True)

        return sorted_aircraft[:n]

    def get_aircraft_by_registration(self, country: str) -> List[Aircraft]:
        """Получение самолетов по стране регистрации"""
        return self.storage.get_aircraft_by_country(country)


def user_interface():
    """Функция для взаимодействия с пользователем через консоль."""

    print("=" * 50)
    print("  СИСТЕМА ОТСЛЕЖИВАНИЯ САМОЛЕТОВ")
    print("=" * 50)

    # Создаем объект для работы с API и данными
    tracker = AircraftTracker()

    while True:
        print("\n" + "=" * 50)
        print("ГЛАВНОЕ МЕНЮ")
        print("=" * 50)
        print("1. Запросить информацию о самолетах над страной")
        print("2. Получить топ N самолетов по высоте полета")
        print("3. Получить самолеты по стране регистрации")
        print("4. Выход")
        print("-" * 50)

        choice = input("Выберите действие (1-4): ").strip()

        # 1:Запрос самолетов над страной
        if choice == "1":
            print("\n--- Запрос информации о самолетах над страной ---")
            country = input("Введите название страны (например, Russia, USA, France): ").strip()

            if not country:
                print("[ОШИБКА] Название страны не может быть пустым!")
                continue

            print(f"\nВыполняется запрос к opensky-network.org для страны: {country}")
            print("Пожалуйста, подождите...")

            try:
                aircraft_list = tracker.fetch_aircraft_by_country(country)

                if aircraft_list:
                    print(f"\n✓ Найдено самолетов: {len(aircraft_list)}")
                    print("-" * 50)
                    for i, aircraft in enumerate(aircraft_list, 1):
                        print(f"{i:3d}. {aircraft}")
                    print("-" * 50)
                    print(f"Данные сохранены в файл aircraft_data.json")
                else:
                    print(f"\n✗ Самолеты над страной '{country}' не найдены")
                    print("Возможные причины:")
                    print("  - Неправильное название страны")
                    print("  - В данный момент нет самолетов в воздушном пространстве")
                    print("  - Проблемы с подключением к API")

            except Exception as e:
                print(f"\n[ОШИБКА] Не удалось получить данные: {e}")

        # 2: Топ N самолетов по высоте
        elif choice == "2":
            print("\n--- Получение топа самолетов по высоте полета ---")

            try:
                n_input = input("Введите количество самолетов для отображения (N): ").strip()
                n = int(n_input)

                if n <= 0:
                    print("[ОШИБКА] Количество должно быть больше нуля!")
                    continue

                print(f"\nПоиск топ-{n} самолетов по высоте полета...")
                top_aircraft = tracker.get_top_by_altitude(n)

                if top_aircraft:
                    print(f"\n✓ Топ-{len(top_aircraft)} самолетов по высоте полета:")
                    print("-" * 50)
                    print(f"{'№':3s} {'Позывной':10s} {'Страна':15s} {'Высота (м)':12s} {'Скорость (м/с)':15s}")
                    print("-" * 50)

                    for i, aircraft in enumerate(top_aircraft, 1):
                        print(f"{i:3d} {aircraft.callsign:10s} {aircraft.origin_country:15s} "
                              f"{aircraft.baro_altitude:12.1f} {aircraft.velocity:15.1f}")
                    print("-" * 50)
                else:
                    print("\n✗ Нет данных о самолетах!")
                    print("Сначала выполните действие 1 для получения информации о самолетах.")

            except ValueError:
                print("[ОШИБКА] Пожалуйста, введите целое положительное число!")

        # 3: Поиск по стране регистрации
        elif choice == "3":
            print("\n--- Получение самолетов по стране регистрации ---")
            country = input("Введите страну регистрации (например, Russia, USA, Germany): ").strip()

            if not country:
                print("[ОШИБКА] Страна регистрации не может быть пустой!")
                continue

            print(f"\nПоиск самолетов с регистрацией в стране: {country}...")
            aircraft_list = tracker.get_aircraft_by_registration(country)

            if aircraft_list:
                print(f"\n✓ Найдено самолетов из {country}: {len(aircraft_list)}")
                print("-" * 50)
                for i, aircraft in enumerate(aircraft_list, 1):
                    print(f"{i:3d}. Позывной: {aircraft.callsign}, "
                          f"Высота: {aircraft.baro_altitude} м, "
                          f"Скорость: {aircraft.velocity} м/с")
                print("-" * 50)
            else:
                print(f"\n✗ Самолеты с регистрацией в '{country}' не найдены")
                print("Сначала выполните действие 1 для получения информации о самолетах.")

        # 4: Выход
        elif choice == "4":
            print("\n" + "=" * 50)
            print("  Завершение работы программы")
            print("=" * 50)
            print(f"Данные сохранены в файл: aircraft_data.json")
            print("До свидания!")
            break

        else:
            print("\n[ОШИБКА] Неверный выбор! Введите число от 1 до 4.")

    return 0