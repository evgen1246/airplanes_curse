from src.aircraft import Aircraft
from src.utils import (filter_aeroplanes, get_aeroplanes_by_altitude, get_top_aeroplanes, print_aeroplanes,
                       sort_aeroplanes)


class TestFilterAeroplanes:
    """Тесты фильтрации по странам"""

    def test_filter_by_single_country(self, sample_aircraft_list):
        """Фильтрация по одной стране"""
        result = filter_aeroplanes(sample_aircraft_list, ["USA"])
        assert len(result) == 2
        assert all(a.origin_country == "USA" for a in result)

    def test_filter_by_multiple_countries(self, sample_aircraft_list):
        """Фильтрация по нескольким странам"""
        result = filter_aeroplanes(sample_aircraft_list, ["USA", "Germany"])
        assert len(result) == 3

    def test_filter_empty_countries(self, sample_aircraft_list):
        """Пустой список стран - возвращает все"""
        result = filter_aeroplanes(sample_aircraft_list, [])
        assert len(result) == 5

    def test_filter_empty_string(self, sample_aircraft_list):
        """Список с пустой строкой"""
        result = filter_aeroplanes(sample_aircraft_list, [""])
        assert len(result) == 5

    def test_filter_nonexistent_country(self, sample_aircraft_list):
        """Несуществующая страна"""
        result = filter_aeroplanes(sample_aircraft_list, ["Mars"])
        assert len(result) == 0

    def test_filter_exact_match(self, sample_aircraft_list):
        """Точное совпадение названия"""
        result = filter_aeroplanes(sample_aircraft_list, ["United Kingdom"])
        assert len(result) == 1
        assert result[0].callsign == "BAW001"


class TestGetAeroplanesByAltitude:
    """Тесты фильтрации по высоте"""

    def test_filter_by_range(self, sample_aircraft_list):
        """Фильтрация по диапазону"""
        result = get_aeroplanes_by_altitude(sample_aircraft_list, "9000-11000")
        assert len(result) == 3
        assert all(9000 <= a.baro_altitude <= 11000 for a in result)

    def test_filter_exact_value(self, sample_aircraft_list):
        """Точное значение"""
        result = get_aeroplanes_by_altitude(sample_aircraft_list, "8000-8000")
        assert len(result) == 1
        assert result[0].baro_altitude == 8000.0

    def test_filter_empty_string(self, sample_aircraft_list):
        """Пустая строка"""
        result = get_aeroplanes_by_altitude(sample_aircraft_list, "")
        assert len(result) == 5

    def test_filter_no_dash(self, sample_aircraft_list):
        """Строка без дефиса"""
        result = get_aeroplanes_by_altitude(sample_aircraft_list, "invalid")
        assert len(result) == 5

    def test_filter_invalid_format(self, sample_aircraft_list):
        """Неверный формат чисел"""
        result = get_aeroplanes_by_altitude(sample_aircraft_list, "abc-xyz")
        assert len(result) == 5

    def test_filter_reversed_range(self, sample_aircraft_list):
        """Обратный диапазон (мин > макс)"""
        result = get_aeroplanes_by_altitude(sample_aircraft_list, "11000-9000")
        assert len(result) == 0  # Никто не попадает

    def test_filter_with_spaces(self, sample_aircraft_list):
        """Пробелы вокруг чисел"""
        result = get_aeroplanes_by_altitude(sample_aircraft_list, " 9000 - 11000 ")
        assert len(result) == 3


class TestSortAeroplanes:
    """Тесты сортировки"""

    def test_sort_descending(self, sample_aircraft_list):
        """Сортировка по убыванию"""
        result = sort_aeroplanes(sample_aircraft_list)
        altitudes = [a.baro_altitude for a in result]
        assert altitudes == sorted(altitudes, reverse=True)
        assert result[0].baro_altitude == 12000.0

    def test_sort_ascending(self, sample_aircraft_list):
        """Сортировка по возрастанию"""
        result = sort_aeroplanes(sample_aircraft_list, reverse=False)
        altitudes = [a.baro_altitude for a in result]
        assert altitudes == sorted(altitudes)
        assert result[0].baro_altitude == 8000.0

    def test_sort_empty_list(self):
        """Пустой список"""
        result = sort_aeroplanes([])
        assert result == []

    def test_sort_single_element(self):
        """Один элемент"""
        aircraft = Aircraft("TEST", "USA", 100, 5000)
        result = sort_aeroplanes([aircraft])
        assert len(result) == 1
        assert result[0] == aircraft


class TestGetTopAeroplanes:
    """Тесты получения топа"""

    def test_get_top_3(self, sample_aircraft_list):
        """Топ-3"""
        sorted_list = sort_aeroplanes(sample_aircraft_list)
        result = get_top_aeroplanes(sorted_list, 3)
        assert len(result) == 3
        assert result[0].baro_altitude == 12000.0
        assert result[1].baro_altitude == 11000.0
        assert result[2].baro_altitude == 10000.0

    def test_get_top_more_than_length(self, sample_aircraft_list):
        """N больше длины списка"""
        sorted_list = sort_aeroplanes(sample_aircraft_list)
        result = get_top_aeroplanes(sorted_list, 10)
        assert len(result) == 5

    def test_get_top_zero(self, sample_aircraft_list):
        """N = 0"""
        sorted_list = sort_aeroplanes(sample_aircraft_list)
        result = get_top_aeroplanes(sorted_list, 0)
        assert len(result) == 0

    def test_get_top_one(self, sample_aircraft_list):
        """N = 1"""
        sorted_list = sort_aeroplanes(sample_aircraft_list)
        result = get_top_aeroplanes(sorted_list, 1)
        assert len(result) == 1


class TestPrintAeroplanes:
    """Тесты вывода"""

    def test_print_with_data(self, sample_aircraft_list, capsys):
        """Вывод с данными"""
        print_aeroplanes(sample_aircraft_list)
        captured = capsys.readouterr()

        assert "AFL123" in captured.out
        assert "USA" in captured.out
        assert "10000.0" in captured.out
        assert "250.5" in captured.out
        assert "Всего самолетов: 5" in captured.out

    def test_print_empty_list(self, capsys):
        """Вывод пустого списка"""
        print_aeroplanes([])
        captured = capsys.readouterr()
        assert "Нет данных о самолетах" in captured.out

    def test_print_single_aircraft(self, sample_aircraft, capsys):
        """Вывод одного самолета"""
        print_aeroplanes([sample_aircraft])
        captured = capsys.readouterr()
        assert "UAL123" in captured.out
        assert "Всего самолетов: 1" in captured.out
