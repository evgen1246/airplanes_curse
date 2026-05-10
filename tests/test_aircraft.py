import pytest

from src.aircraft import Aircraft


class TestAircraftInit:
    """Тесты инициализации объекта Aircraft"""

    def test_create_valid_aircraft(self):
        """Тест создания самолета с валидными данными"""
        aircraft = Aircraft("UAL123", "United States", 250.5, 10000.0)

        assert aircraft.callsign == "UAL123"
        assert aircraft.origin_country == "United States"
        assert aircraft.velocity == 250.5
        assert aircraft.baro_altitude == 10000.0

    def test_create_with_spaces(self):
        """Тест создания с пробелами в позывном"""
        aircraft = Aircraft("  UAL123  ", "United States", 250.5, 10000.0)
        assert aircraft.callsign == "UAL123"

    def test_create_with_zero_values(self):
        """Тест создания с нулевыми значениями"""
        aircraft = Aircraft("TEST", "USA", 0.0, 0.0)
        assert aircraft.velocity == 0.0
        assert aircraft.baro_altitude == 0.0

    def test_create_with_integers(self):
        """Тест создания с целыми числами"""
        aircraft = Aircraft("TEST", "USA", 250, 10000)
        assert isinstance(aircraft.velocity, float)
        assert isinstance(aircraft.baro_altitude, float)


class TestAircraftValidation:
    """Тесты валидации данных"""

    def test_empty_callsign_raises_error(self):
        """Тест пустого позывного"""
        with pytest.raises(ValueError, match="Позывной не может быть пустым"):
            Aircraft("", "USA", 100, 5000)

    def test_whitespace_callsign_raises_error(self):
        """Тест позывного из пробелов"""
        with pytest.raises(ValueError, match="Позывной не может быть пустым"):
            Aircraft("   ", "USA", 100, 5000)

    def test_empty_country_raises_error(self):
        """Тест пустой страны"""
        with pytest.raises(ValueError, match="Страна не может быть пустой"):
            Aircraft("TEST", "", 100, 5000)

    def test_negative_velocity_raises_error(self):
        """Тест отрицательной скорости"""
        with pytest.raises(ValueError, match="Скорость не может быть отрицательной"):
            Aircraft("TEST", "USA", -100, 5000)

    def test_negative_altitude_raises_error(self):
        """Тест отрицательной высоты"""
        with pytest.raises(ValueError, match="Высота не может быть отрицательной"):
            Aircraft("TEST", "USA", 100, -5000)

    def test_wrong_type_callsign_raises_error(self):
        """Тест неверного типа позывного"""
        with pytest.raises(TypeError, match="Позывной должен быть строкой"):
            Aircraft(123, "USA", 100, 5000)

    def test_wrong_type_country_raises_error(self):
        """Тест неверного типа страны"""
        with pytest.raises(TypeError, match="Страна должна быть строкой"):
            Aircraft("TEST", 123, 100, 5000)

    def test_wrong_type_velocity_raises_error(self):
        """Тест неверного типа скорости"""
        with pytest.raises(TypeError, match="Скорость должна быть числом"):
            Aircraft("TEST", "USA", "fast", 5000)

    def test_wrong_type_altitude_raises_error(self):
        """Тест неверного типа высоты"""
        with pytest.raises(TypeError, match="Высота должна быть числом"):
            Aircraft("TEST", "USA", 100, "high")


class TestAircraftComparison:
    """Тесты сравнения самолетов"""

    def test_equality_same_values(self):
        """Тест равенства одинаковых самолетов"""
        a1 = Aircraft("A", "USA", 200, 5000)
        a2 = Aircraft("B", "USA", 200, 5000)
        assert a1 == a2

    def test_equality_different_velocity(self):
        """Тест неравенства по скорости"""
        a1 = Aircraft("A", "USA", 200, 5000)
        a2 = Aircraft("B", "USA", 300, 5000)
        assert a1 != a2

    def test_equality_different_altitude(self):
        """Тест неравенства по высоте"""
        a1 = Aircraft("A", "USA", 200, 5000)
        a2 = Aircraft("B", "USA", 200, 6000)
        assert a1 != a2

    def test_less_than_by_velocity(self):
        """Тест сравнения по скорости"""
        a1 = Aircraft("A", "USA", 200, 5000)
        a2 = Aircraft("B", "USA", 300, 5000)
        assert a1 < a2
        assert not a2 < a1

    def test_less_than_by_altitude(self):
        """Тест сравнения по высоте при равной скорости"""
        a1 = Aircraft("A", "USA", 200, 5000)
        a2 = Aircraft("B", "USA", 200, 6000)
        assert a1 < a2
        assert not a2 < a1

    def test_less_than_equal_velocity(self):
        """Тест сравнения при равной скорости"""
        a1 = Aircraft("A", "USA", 200, 5000)
        a2 = Aircraft("B", "USA", 200, 5000)
        assert not a1 < a2
        assert not a2 < a1

    def test_compare_velocity(self):
        """Тест метода compare_velocity"""
        a1 = Aircraft("A", "USA", 200, 5000)
        a2 = Aircraft("B", "USA", 300, 5000)

        assert a1.compare_velocity(a2) == -1
        assert a2.compare_velocity(a1) == 1

    def test_compare_velocity_equal(self):
        """Тест сравнения равных скоростей"""
        a1 = Aircraft("A", "USA", 200, 5000)
        a2 = Aircraft("B", "USA", 200, 6000)

        assert a1.compare_velocity(a2) == 0

    def test_compare_altitude(self):
        """Тест метода compare_altitude"""
        a1 = Aircraft("A", "USA", 200, 5000)
        a2 = Aircraft("B", "USA", 200, 6000)

        assert a1.compare_altitude(a2) == -1
        assert a2.compare_altitude(a1) == 1

    def test_compare_altitude_equal(self):
        """Тест сравнения равных высот"""
        a1 = Aircraft("A", "USA", 200, 5000)
        a2 = Aircraft("B", "USA", 300, 5000)

        assert a1.compare_altitude(a2) == 0

    def test_compare_with_non_aircraft_raises_error(self):
        """Тест сравнения с не-Aircraft объектом"""
        a1 = Aircraft("A", "USA", 200, 5000)

        with pytest.raises(TypeError):
            a1.compare_velocity("not an aircraft")

        with pytest.raises(TypeError):
            a1.compare_altitude(123)


class TestAircraftSerialization:
    """Тесты сериализации"""

    def test_to_dict(self):
        """Тест преобразования в словарь"""
        aircraft = Aircraft("UAL123", "United States", 250.5, 10000.0)
        data = aircraft.to_dict()

        assert data == {
            "callsign": "UAL123",
            "origin_country": "United States",
            "velocity": 250.5,
            "baro_altitude": 10000.0,
        }

    def test_from_dict(self):
        """Тест создания из словаря"""
        data = {
            "callsign": "UAL123",
            "origin_country": "United States",
            "velocity": 250.5,
            "baro_altitude": 10000.0,
        }
        aircraft = Aircraft.from_dict(data)

        assert aircraft.callsign == "UAL123"
        assert aircraft.origin_country == "United States"
        assert aircraft.velocity == 250.5
        assert aircraft.baro_altitude == 10000.0

    def test_roundtrip_serialization(self):
        """Тест полного цикла сериализации"""
        original = Aircraft("UAL123", "United States", 250.5, 10000.0)
        data = original.to_dict()
        restored = Aircraft.from_dict(data)
        assert original == restored


class TestAircraftCastToList:
    """Тесты создания списка объектов из API ответа"""

    def test_cast_to_object_list(self, sample_api_response):
        """Тест преобразования ответа API в список объектов"""
        result = Aircraft.cast_to_object_list(sample_api_response["states"])

        assert len(result) == 2
        assert result[0].callsign == "UAL123"
        assert result[0].origin_country == "United States"
        assert result[0].velocity == 250.5
        assert result[0].baro_altitude == 10000.0

    def test_cast_to_object_list_empty(self):
        """Тест с пустым списком"""
        result = Aircraft.cast_to_object_list([])
        assert result == []

    def test_cast_to_object_list_with_errors(self, capsys):
        """Тест с некорректными данными"""
        states = [["abc", "", "USA", 0, 0, 0, 0, -100, False, 200]]
        result = Aircraft.cast_to_object_list(states)

        assert len(result) == 0
        captured = capsys.readouterr()
        assert "Ошибка" in captured.out


class TestAircraftStringRepresentation:
    """Тесты строкового представления"""

    def test_str(self):
        """Тест __str__"""
        aircraft = Aircraft("UAL123", "United States", 250.5, 10000.0)
        result = str(aircraft)

        assert "UAL123" in result
        assert "United States" in result
        assert "250.5" in result
        assert "10000.0" in result

    def test_repr(self):
        """Тест __repr__"""
        aircraft = Aircraft("UAL123", "United States", 250.5, 10000.0)
        result = repr(aircraft)

        assert "Aircraft" in result
        assert "UAL123" in result
