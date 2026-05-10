from src.aircraft import Aircraft
from src.api_clients import AeroplanesAPI
from src.file_managers import JSONSaver
from src.utils import (filter_aeroplanes, get_aeroplanes_by_altitude, get_top_aeroplanes, print_aeroplanes,
                       sort_aeroplanes)


def user_interaction() -> None:
    """Функция для взаимодействия с пользователем"""

    print("=" * 60)
    print("  СИСТЕМА ОТСЛЕЖИВАНИЯ САМОЛЕТОВ")
    print("=" * 60)

    # Создание экземпляра класса для работы с API сайтов с самолетами
    api = AeroplanesAPI()

    # Создание экземпляра для сохранения данных
    json_saver = JSONSaver()

    # Переменная для хранения текущих самолетов
    aeroplanes = []

    while True:
        print("\n" + "=" * 60)
        print("ГЛАВНОЕ МЕНЮ")
        print("=" * 60)
        print("1. Получить информацию о самолетах над страной")
        print("2. Показать топ N самолетов по высоте полета")
        print("3. Фильтрация по стране регистрации")
        print("4. Фильтрация по диапазону высот")
        print("5. Показать все самолеты")
        print("6. Сохранить данные в файл")
        print("7. Выход")
        print("-" * 60)

        choice = input("Выберите действие (1-7): ").strip()

        if choice == "1":
            # Ввести название страны для запроса информации о самолетах
            country = input("\nВведите название страны: ").strip()

            if not country:
                print("[ОШИБКА] Название страны не может быть пустым!")
                continue

            print(f"\nПолучение информации о самолетах с opensky-network.org для страны: {country}")
            print("Пожалуйста, подождите...")

            try:
                # Получение информации о самолетах с opensky-network.org
                raw_data = api.get_aeroplanes(country)

                if raw_data:
                    # Преобразование набора данных в список объектов
                    aeroplanes = Aircraft.cast_to_object_list(raw_data)
                    print(f"\n✓ Получено самолетов: {len(aeroplanes)}")

                    # Сохранение в файл
                    for aircraft in aeroplanes:
                        json_saver.add_aircraft(aircraft)

                    print_aeroplanes(aeroplanes[:10])  # Показываем первые 10
                else:
                    print(f"\n✗ Самолеты над страной '{country}' не найдены")

            except Exception as e:
                print(f"\n[ОШИБКА] {e}")

        elif choice == "2":
            # Получить топ N самолетов по высоте полета
            if not aeroplanes:
                print("\n[ОШИБКА] Сначала получите данные о самолетах (пункт 1)")
                continue

            try:
                top_n = int(input("\nВведите количество самолетов для вывода в топ N: ").strip())

                if top_n <= 0:
                    print("[ОШИБКА] Количество должно быть больше нуля!")
                    continue

                # Сортировка и получение топа
                sorted_aeroplanes = sort_aeroplanes(aeroplanes)
                top_aeroplanes = get_top_aeroplanes(sorted_aeroplanes, top_n)

                print(f"\nТоп {top_n} самолетов по высоте полета:")
                print_aeroplanes(top_aeroplanes)

            except ValueError:
                print("[ОШИБКА] Введите целое число!")

        elif choice == "3":
            # Фильтрация по стране регистрации
            if not aeroplanes:
                print("\n[ОШИБКА] Сначала получите данные о самолетах (пункт 1)")
                continue

            filter_input = input(
                "\nВведите названия стран для фильтрации " "(через пробел, например: Spain USA): "
            ).strip()
            filter_words = filter_input.split() if filter_input else []

            filtered_aeroplanes = filter_aeroplanes(aeroplanes, filter_words)

            print(f"\nОтфильтровано самолетов: {len(filtered_aeroplanes)}")
            print_aeroplanes(filtered_aeroplanes)

        elif choice == "4":
            # Фильтрация по диапазону высот
            if not aeroplanes:
                print("\n[ОШИБКА] Сначала получите данные о самолетах (пункт 1)")
                continue

            altitude_range = input("\nВведите диапазон высот полета " "(например: 1000-5000): ").strip()

            ranged_aeroplanes = get_aeroplanes_by_altitude(aeroplanes, altitude_range)

            print(f"\nОтфильтровано самолетов: {len(ranged_aeroplanes)}")
            print_aeroplanes(ranged_aeroplanes)

        elif choice == "5":
            # Показать все самолеты
            if not aeroplanes:
                print("\n[ОШИБКА] Нет данных о самолетах")
                continue

            print_aeroplanes(aeroplanes)

        elif choice == "6":
            # Сохранить данные в файл
            if not aeroplanes:
                print("\n[ОШИБКА] Нет данных для сохранения")
                continue

            for aircraft in aeroplanes:
                json_saver.add_aircraft(aircraft)

            print("\n✓ Данные сохранены в файл aircraft_data.json")
            print(f"  Всего сохранено: {len(aeroplanes)} самолетов")

        elif choice == "7":
            print("\n" + "=" * 60)
            print("  Завершение работы программы")
            print("=" * 60)
            print("Данные сохранены в файл: aircraft_data.json")
            print("До свидания!")
            break

        else:
            print("\n[ОШИБКА] Неверный выбор! Введите число от 1 до 7.")


def main() -> int:
    """Главная функция"""
    print("Запуск системы отслеживания самолетов...")
    print("Используемые API:")
    print("  - nominatim.openstreetmap.org (геоданные)")
    print("  - opensky-network.org (данные о самолетах)")

    try:
        user_interaction()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
    except Exception as e:
        print(f"\n[КРИТИЧЕСКАЯ ОШИБКА] {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
