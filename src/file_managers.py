from abc import ABC, abstractmethod
from typing import List, Dict
import json
import os
from aircraft import Aircraft


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


class JSONSaver(AbstractFileManager):
    """Класс для сохранения информации в JSON-файл"""

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

        # Проверка на дубликаты по позывному
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

    def delete_aircraft(self, aircraft: Aircraft) -> None:
        """Удаление информации о самолете"""
        data = self._load_data()
        data = [item for item in data if item.get('callsign') != aircraft.callsign]
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

    def get_all_aircraft(self) -> List[Aircraft]:
        raise NotImplementedError("Database integration not implemented yet")