from typing import List

from src.aircraft import Aircraft


def filter_aeroplanes(aeroplanes: List[Aircraft], countries: List[str]) -> List[Aircraft]:
    """Фильтрация самолетов по странам регистрации"""
    if not countries or countries == [""]:
        return aeroplanes

    filtered = []
    for aircraft in aeroplanes:
        if aircraft.origin_country in countries:
            filtered.append(aircraft)

    return filtered


def get_aeroplanes_by_altitude(aeroplanes: List[Aircraft], altitude_range: str) -> List[Aircraft]:
    """Фильтрация самолетов по диапазону высот"""
    if not altitude_range or "-" not in altitude_range:
        return aeroplanes

    try:
        parts = altitude_range.split("-")
        min_altitude = float(parts[0].strip())
        max_altitude = float(parts[1].strip())

        filtered = []
        for aircraft in aeroplanes:
            if min_altitude <= aircraft.baro_altitude <= max_altitude:
                filtered.append(aircraft)

        return filtered
    except ValueError, IndexError:
        print("Неверный формат диапазона высот. Используйте формат: мин-макс")
        return aeroplanes


def sort_aeroplanes(aeroplanes: List[Aircraft], reverse: bool = True) -> List[Aircraft]:
    """Сортировка самолетов по высоте"""
    return sorted(aeroplanes, key=lambda x: x.baro_altitude, reverse=reverse)


def get_top_aeroplanes(aeroplanes: List[Aircraft], n: int) -> List[Aircraft]:
    """Получение топ N самолетов"""
    return aeroplanes[:n]


def print_aeroplanes(aeroplanes: List[Aircraft]) -> None:
    """Вывод информации о самолетах"""
    if not aeroplanes:
        print("Нет данных о самолетах для отображения")
        return

    print(f"\n{'=' * 60}")
    print(f"{'№':4s} {'Позывной':12s} {'Страна':20s} {'Высота (м)':12s} {'Скорость (м/с)':15s}")
    print(f"{'=' * 60}")

    for i, aircraft in enumerate(aeroplanes, 1):
        print(
            f"{i:4d} {aircraft.callsign:12s} {aircraft.origin_country:20s} "
            f"{aircraft.baro_altitude:12.1f} {aircraft.velocity:15.1f}"
        )

    print(f"{'=' * 60}")
    print(f"Всего самолетов: {len(aeroplanes)}")
