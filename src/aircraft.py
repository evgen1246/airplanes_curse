from typing import List, Dict, Any
from functools import total_ordering


@total_ordering
class Aircraft:
    """
    Класс, представляющий информацию о самолете.

    Атрибуты:
    - callsign: позывной
    - origin_country: страна регистрации
    - velocity: скорость полета (м/с)
    - baro_altitude: высота полета (метры)
    """

    def __init__(self, callsign: str, origin_country: str,
                 velocity: float, baro_altitude: float):
        """Конструктор класса с одним самолетом"""
        self._callsign = self._validate_callsign(callsign)
        self._origin_country = self._validate_country(origin_country)
        self._velocity = self._validate_velocity(velocity)
        self._baro_altitude = self._validate_altitude(baro_altitude)

    # ========== Валидация ==========

    @staticmethod
    def _validate_callsign(callsign: str) -> str:
        if not isinstance(callsign, str):
            raise TypeError(f"Позывной должен быть строкой")
        if not callsign or not callsign.strip():
            raise ValueError("Позывной не может быть пустым")
        return callsign.strip()

    @staticmethod
    def _validate_country(country: str) -> str:
        if not isinstance(country, str):
            raise TypeError(f"Страна должна быть строкой")
        if not country or not country.strip():
            raise ValueError("Страна не может быть пустой")
        return country.strip()

    @staticmethod
    def _validate_velocity(velocity: float) -> float:
        if not isinstance(velocity, (int, float)):
            raise TypeError(f"Скорость должна быть числом")
        if velocity < 0:
            raise ValueError(f"Скорость не может быть отрицательной: {velocity}")
        return float(velocity)

    @staticmethod
    def _validate_altitude(altitude: float) -> float:
        if not isinstance(altitude, (int, float)):
            raise TypeError(f"Высота должна быть числом")
        if altitude < 0:
            raise ValueError(f"Высота не может быть отрицательной: {altitude}")
        return float(altitude)

    #Свойства

    @property
    def callsign(self) -> str:
        return self._callsign

    @property
    def origin_country(self) -> str:
        return self._origin_country

    @property
    def velocity(self) -> float:
        return self._velocity

    @property
    def baro_altitude(self) -> float:
        return self._baro_altitude

    #Методы сравнения

    def __eq__(self, other: 'Aircraft') -> bool:
        if not isinstance(other, Aircraft):
            return NotImplemented
        return (abs(self._velocity - other._velocity) < 0.01 and
                abs(self._baro_altitude - other._baro_altitude) < 0.01)

    def __lt__(self, other: 'Aircraft') -> bool:
        if not isinstance(other, Aircraft):
            return NotImplemented
        if abs(self._velocity - other._velocity) >= 0.01:
            return self._velocity < other._velocity
        return self._baro_altitude < other._baro_altitude

    def compare_velocity(self, other: 'Aircraft') -> int:
        """Сравнение по скорости: -1, 0, 1"""
        if not isinstance(other, Aircraft):
            raise TypeError(f"Нельзя сравнить с {type(other)}")
        if abs(self._velocity - other._velocity) < 0.01:
            return 0
        return -1 if self._velocity < other._velocity else 1

    def compare_altitude(self, other: 'Aircraft') -> int:
        """Сравнение по высоте: -1, 0, 1"""
        if not isinstance(other, Aircraft):
            raise TypeError(f"Нельзя сравнить с {type(other)}")
        if abs(self._baro_altitude - other._baro_altitude) < 0.01:
            return 0
        return -1 if self._baro_altitude < other._baro_altitude else 1



    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'callsign': self._callsign,
            'origin_country': self._origin_country,
            'velocity': self._velocity,
            'baro_altitude': self._baro_altitude,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Aircraft':
        """Создание из словаря"""
        return cls(
            callsign=data['callsign'],
            origin_country=data['origin_country'],
            velocity=data['velocity'],
            baro_altitude=data['baro_altitude'],
        )

    @classmethod
    def cast_to_object_list(cls, states: List[List]) -> List['Aircraft']:
        """ Преобразование набора данных из API в список объектов Aircraft"""
        aircraft_list = []
        if states:
            for state in states:
                try:
                    aircraft = cls._from_state(state)
                    aircraft_list.append(aircraft)
                except (ValueError, TypeError) as e:
                    print(f"Ошибка при создании объекта: {e}")
        return aircraft_list

    @classmethod
    def _from_state(cls, state: List[Any]) -> 'Aircraft':
        """Создание объекта из состояния самолета (внутренний метод) """
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

    def __repr__(self) -> str:
        return (f"Aircraft(callsign='{self._callsign}', "
                f"country='{self._origin_country}', "
                f"velocity={self._velocity}, altitude={self._baro_altitude})")