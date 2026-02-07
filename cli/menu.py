import re
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from db.database import Database
from services.appointment_service import (
    create_appointment,
    delete_appointment,
    get_all_doctors,
    get_available_dates,
    get_available_slots_for_day,
    get_future_appointments,
)
from services.patient_service import (
    get_all_patients,
    get_patient_appointments,
    get_patient_card_info,
    register_patient,
    get_owner_by_phone
)


# шаблон для проверки номера телефона владельца
PHONE_PATTERN = re.compile(r"^\+7\d{10}$")

console = Console()


def show_header() -> None:
    """
    Заголовок главного меню программы.
    """
    console.print("\n",
        Panel(
            " Ветеринарная клиника ",
            style="bold cyan",
            expand=False
        )
    )


def show_menu() -> None:
    """
    Главное меню программы.
    """
    console.print("\n[bold]Выберите действие:[/bold]")
    console.print("1. Зарегистрировать нового пациента")
    console.print("2. Показать список пациентов")
    console.print("3. Записать пациента к врачу")
    console.print("4. Показать список предстоящих записей")
    console.print("5. Отменить запись")
    console.print("6. Просмотр медицинской карты пациента")
    console.print("0. Выход")
    

def register_patient_menu(db: Database) -> None:
    """
    Меню для регистрации пациента.

    Примечания:
    - телефон проверяется по шаблону +7XXXXXXXXXX;
    - при возникновении ошибки -> вывод сообщения и выход в главное меню.
    """
    while True:
        console.print("\n\n[bold cyan]Регистрация нового пациента[/bold cyan]")
        console.print("Для выхода из режима регистрации оставьте любое поле пустым (нажмите Enter).\n")

        owner_full_name = console.input("ФИО владельца: ").strip() # удаляем лишние пробелы
        
        if owner_full_name == "":
            console.print("[blue]Процесс регистрации прерван.[/blue]")
            console.input("Нажмите Enter, чтобы вернуться в меню...")
            return

        while True:
            owner_phone = console.input("Телефон владельца (+7XXXXXXXXXX): ").strip()
            
            if owner_phone == "":
                console.print("[blue]Процесс регистрации прерван.[/blue]")
                console.input("Нажмите Enter, чтобы вернуться в меню...")
                return
            
            # проверка телефона по шаблону
            if not PHONE_PATTERN.match(owner_phone):
                console.print("[red]Ошибка: телефон должен быть в формате +7XXXXXXXXXX.[/red]")
                console.input("Нажмите Enter, чтобы попробовать еще раз.")
                continue

            existing_owner = get_owner_by_phone(db, owner_phone)

            # если телефон уже есть и ФИО отличается — спрашиваем подтверждение
            if existing_owner is not None and existing_owner.full_name != owner_full_name:
                console.print(f"[blue]Найден владелец с этим телефоном:[/blue] {existing_owner.full_name}")

                use_existing: bool | None = None
                while True:
                    choice = console.input("Использовать этого владельца? (да/нет): ").strip().lower()
                    if choice == "да":
                        use_existing = True
                        break
                    elif choice == "нет":
                        use_existing = False
                        break
                    
                    console.print("[red]Неверное подтверждение, введите 'да' или 'нет'.")

                if use_existing is False:
                    console.print("[blue]Введите другой номер телефона.[/blue]")
                    continue    
            break

        patient_name = console.input("Имя животного: ").strip()

        if patient_name == "":
            console.print("[blue]Процесс регистрации прерван.[/blue]")
            console.input("Нажмите Enter, чтобы вернуться в меню...")
            return

        species = console.input("Вид животного: ").strip()

        if species == "":
            console.print("[blue]Процесс регистрации прерван.[/blue]")
            console.input("Нажмите Enter, чтобы вернуться в меню...")
            return

        try:
            patient = register_patient(
                db=db,
                owner_full_name=owner_full_name,
                owner_phone=owner_phone,
                patient_name=patient_name,
                species=species
            )
        except Exception as e:
            console.print("[red]Ошибка при регистрации пациента.[/red]")
            console.print(e) # отображаем сообщение ошибки
            console.input("Нажмите Enter, чтобы попробовать еще раз.")
            continue
        
        break # выход из главного цикла

    console.print(f"\n[green]Пациент успешно зарегистрирован![/green]\n{patient}")
    console.input("Нажмите Enter, чтобы вернуться в меню...")
    

def render_patients_table(patients: list[tuple[int, str, str, str, str]]) -> Table:
    """
    Строит таблицу пациентов.
    """
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID")
    table.add_column("Имя")
    table.add_column("Вид")
    table.add_column("Владелец")
    table.add_column("Телефон")

    for pid, name, species, owner, phone in patients:
        table.add_row(str(pid), name, species, owner, phone)
    
    return table


def render_doctors_table(doctors: list[tuple[int, str]]) -> Table:
    """
    Строит таблицу врачей.
    """
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID")
    table.add_column("ФИО")

    for did, full_name in doctors:
        table.add_row(str(did), full_name)
    
    return table


def render_appointments_table(appointments: list[tuple[int, str, str, str, str, str, datetime]]) -> Table:
    """
    Строит таблицу записей.
    """
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID")
    table.add_column("Пациент")
    table.add_column("Вид")
    table.add_column("Владелец")
    table.add_column("Контакты владельца")
    table.add_column("Доктор")
    table.add_column("Дата и время")

    for aid, name, species, owner, owner_phone, full_name, date_time in appointments:
        table.add_row(str(aid), name, species, owner, owner_phone, full_name, date_time.strftime("%Y-%m-%d %H:%M"))
    
    return table


def show_patients(db: Database) -> None:
    """
    Вывод списка пациентов с информацией о владельцах в виде таблицы.
    """
    console.print("\n[bold cyan]Список пациентов[/bold cyan]")

    patients = get_all_patients(db)

    # если список пациентов оказался пустым -> информируем пользователя
    if not patients:
        console.print("[blue]Пациентов пока нет.[/blue]")
        console.input("\nНажмите Enter, чтобы вернуться в меню...")
        return

    console.print(render_patients_table(patients))
    console.input("\nНажмите Enter, чтобы вернуться в меню...")


def create_appointment_menu(db: Database) -> None:
    """
    Меню для записи пациентов на прием.

    Примечания:
    - в любом поле можно нажать Enter для отмены;
    - дата выбирается из списка (2 недели вперед);
    - время выбирается из доступных слотов (09:00-16:30, шаг 30 минут).
    """
    console.print("\n\n[bold cyan]Запись к врачу[/bold cyan]")
    console.print("Для выхода из режима записи к врачу оставьте любое поле пустым (нажмите Enter).\n")

    # получаем список пациентов
    patients = get_all_patients(db)
    # если он пуст -> сообщаем пользователю и возвращаемся в главное меню
    if not patients:
        console.print("[blue]Нет пациентов для записи.[/blue]")
        console.input("Нажмите Enter, чтобы вернуться в меню...")
        return
    
    # получаем список врачей
    doctors = get_all_doctors(db)
    if not doctors:
        console.print("[blue]Нет врачей для записи[/blue]")
        console.input("Нажмите Enter, чтобы вернуться в меню...")
        return
    
    # собираем id пациентов и врачей для дальнейшей проверки ввода
    patient_ids = {pid for pid, *_ in patients}
    doctor_ids = {did for did, _ in doctors}

    # показываем пациентов
    console.print(render_patients_table(patients))

    while True:
        patient_id_str = console.input("Введите ID пациента: ").strip()

        if patient_id_str == "":
            console.print("[blue]Процесс записи прерван.[/blue]")
            console.input("Нажмите Enter, чтобы вернуться в меню...")
            return
        
        if not patient_id_str.isdigit():
            console.print("[red]ID пациента должен быть числом.[/red]")
            console.input("Нажмите Enter, чтобы попробовать еще раз.")
            continue

        patient_id = int(patient_id_str)

        if patient_id not in patient_ids:
            console.print("[red]Пациент с таким ID не найден.[/red]")
            console.input("Нажмите Enter, чтобы попробовать еще раз.")
            continue

        break # выходим из цикла выбора пациента

    # показваем врачей
    console.print("\n", render_doctors_table(doctors))

    while True:
        doctor_id_str = console.input("Введите ID врача: ").strip()

        if doctor_id_str == "":
            console.print("[blue]Процесс записи прерван.[/blue]")
            console.input("Нажмите Enter, чтобы вернуться в меню...")
            return
        
        if not doctor_id_str.isdigit():
            console.print("[red]ID врача должен быть числом.[/red]")
            console.input("Нажмите Enter, чтобы попробовать еще раз.")
            continue

        doctor_id = int(doctor_id_str)

        if doctor_id not in doctor_ids:
            console.print("[red]Врач с таким ID не найден.[/red]")
            console.input("Нажмите Enter, чтобы попробовать еще раз.")
            continue

        break # выходим из цикла выбора врача

    dates = get_available_dates()

    console.print("\n[bold]Выберите дату:[/bold]")
    for i, d in enumerate(dates, start=1):
        console.print(f"{i}. {d.strftime('%Y-%m-%d')}")

    # выбор времени
    while True:
        date_choice = console.input("Номер даты: ").strip()

        if date_choice == "":
            console.print("[blue]Процесс записи прерван.[/blue]")
            console.input("Нажмите Enter, чтобы вернуться в меню...")
            return
        
        if not date_choice.isdigit():
            console.print("[red]Номер даты должен быть числом.[/red]")
            console.input("Нажмите Enter, чтобы попробовать еще раз.")
            continue
    
        date_idx = int(date_choice) - 1
        if not (0 <= date_idx < len(dates)):
            console.print("[red]Неверный номер даты.[/red]")
            console.input("Нажмите Enter, чтобы попробовать еще раз.")
            continue

        chosen_day = dates[date_idx]

        # выбор времени
        slots = get_available_slots_for_day(db, doctor_id, chosen_day)
        if not slots:
            console.print("[blue]На выбранную дату нет доступных номерков.[/blue]")
            console.input("Нажмите Enter, чтобы выбрать другую дату...")
            continue

        console.print("\n[bold]Доступное время:[/bold]")
        for i, slot in enumerate(slots, start=1):
            console.print(f"{i}. {slot.strftime('%H:%M')}")
        
        while True:
            slot_choice = console.input("Номер времени: ").strip()

            if slot_choice == "":
                console.print("[blue]Процесс записи прерван.[/blue]")
                console.input("Нажмите Enter, чтобы вернуться в меню...")
                return
            
            if not slot_choice.isdigit():
                console.print("[red]Номер времени должен быть числом.[/red]")
                console.input("Нажмите Enter, чтобы попробовать еще раз.")
                continue
        
            slot_idx = int(slot_choice) - 1
            if not (0 <= slot_idx < len(slots)):
                console.print("[red]Неверный номер времени.[/red]")
                console.input("Нажмите Enter, чтобы попробовать еще раз.")
                continue
        
            appointment_dt = slots[slot_idx]
            break # выходим из цикла выбора времени

        break  # выходим из цикла выбора даты

    # создаем запись
    try:
        create_appointment(db, patient_id, doctor_id, appointment_dt)
    except Exception as e:
        console.print("[red]Ошибка при создании записи.[/red]")
        console.print(e)
        console.input("Нажмите Enter, чтобы вернуться в меню...")
        return

    console.print("[green]Запись успешно создана![/green]")
    console.input("Нажмите Enter, чтобы вернуться в меню...")
    return


def show_future_appointments(db: Database) -> None:
    """
    Выводит список предстоящих записей на прием.
    """
    console.print("\n[bold cyan]Список записей к врачу[/bold cyan]")

    appointments = get_future_appointments(db)

    if not appointments:
        console.print("[blue]Записей пока нет[/blue]")
        console.input("\nНажмите Enter, чтобы вернуться в главное меню...")
        return

    console.print(render_appointments_table(appointments))
    console.input("\nНажмите Enter, чтобы вернуться в главное меню...")
    return


def cancel_appointment_menu(db: Database) -> None:
    """
    Меню отмены записи к врачу.
    """

    console.print("\n[bold cyan]Отмена записи[/bold cyan]")
    console.print("Для выхода из режима отмены записи к врачу оставьте любое поле пустым (нажмите Enter).\n")

    appointments = get_future_appointments(db)

    if not appointments:
        console.print("[blue]Нет предстоящих записей.[/blue]")
        console.input("Нажмите Enter, чтобы вернуться в меню...")
        return

    console.print(render_appointments_table(appointments))

    # множество id для проверки
    appointment_ids = {aid for aid, *_ in appointments}

    while True:
        aid_str = console.input("Введите ID записи для отмены: ").strip()

        if aid_str == "":
            console.print("[blue]Процесс отмены записи прерван.[/blue]")
            console.input("Нажмите Enter, чтобы вернуться меню...")
            return

        if not aid_str.isdigit():
            console.print("[red]ID должен быть числом.[/red]")
            console.input("Нажмите Enter, чтобы попробовать еще раз.")
            continue

        appointment_id = int(aid_str)

        if appointment_id not in appointment_ids:
            console.print("[red]Запись с таким ID не найдена.[/red]")
            console.input("Нажмите Enter, чтобы попробовать еще раз.")
            continue

        # подтверждение
        success = False
        while True:
            confirm = console.input("\nВы уверены, что хотите отменить эту запись? (да/нет): ").strip().lower()

            if confirm == "да":
                success = delete_appointment(db, appointment_id) # удаление
                break
            elif confirm == "нет":
                console.print("[blue]Запись не будет удалена.[/blue]")
                console.input("Нажмите Enter, чтобы вернуться в меню...")
                return
            else:
                console.print("[red]Неверное подтверждение удаления, введите 'да' или 'нет'.")
                console.input("Нажмите Enter, чтобы попробовать еще раз.")
                continue

        if success:
            console.print("[green]Запись успешно отменена.[/green]")
        else:
            console.print("[red]Не удалось удалить запись.[/red]")

        console.input("Нажмите Enter, чтобы вернуться в меню...")
        return


def show_medical_card_menu(db: Database) -> None:
    """
    Просмотр медицинской карты пациента.
    """
    console.print("\n[bold cyan]Просмотр медицинской карты[/bold cyan]")
    console.print("Нажмите Enter в любом поле для отмены.\n")

    patients = get_all_patients(db)
    if not patients:
        console.print("[blue]Пациентов пока нет.[/blue]")
        console.input("Нажмите Enter, чтобы вернуться в меню...")
        return

    # Показываем список пациентов (полная таблица)
    console.print(render_patients_table(patients))

    patient_ids = {pid for pid, *_ in patients}

    while True:
        patient_id_str = console.input("Введите ID пациента (Enter — выход): ").strip()
        if patient_id_str == "":
            console.print("[blue]Просмотр медкарты отменен.[/blue]")
            console.input("Нажмите Enter, чтобы вернуться в меню...")
            return
        if not patient_id_str.isdigit():
            console.print("[red]ID пациента должен быть числом.[/red]")
            console.input("Нажмите Enter, чтобы попробовать еще раз.")
            continue

        patient_id = int(patient_id_str)
        if patient_id not in patient_ids:
            console.print("[red]Пациент с таким ID не найден.[/red]")
            console.input("Нажмите Enter, чтобы попробовать еще раз.")
            continue
        break

    # Шапка медкарты
    info = get_patient_card_info(db, patient_id)
    if info is None:
        console.print("[red]Не удалось найти данные пациента.[/red]")
        console.input("Нажмите Enter, чтобы вернуться в меню...")
        return

    pid, patient_name, species, owner_name, owner_phone = info

    header_text = (
        f"[bold]Пациент:[/bold] {patient_name}\n"
        f"[bold]Вид:[/bold] {species}\n\n"
        f"[bold]Владелец:[/bold] {owner_name}\n"
        f"[bold]Телефон:[/bold] {owner_phone}"
    )

    
    console.print("\n", Panel(header_text, title=f"Медкарта №{pid}", style="cyan", expand=False))

    # Записи пациента
    appointments = get_patient_appointments(db, pid)

    if not appointments:
        console.print("\n[blue]Записей к врачу нет.[/blue]")
        console.input("\nНажмите Enter, чтобы вернуться в меню...")
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID")
    table.add_column("Врач")
    table.add_column("Дата и время")

    for aid, doctor_full_name, date_time in appointments:
        table.add_row(
            str(aid),
            doctor_full_name,
            date_time.strftime("%Y-%m-%d %H:%M")
        )

    console.print("\n[bold]Записи к врачу:[/bold]")
    console.print(table)

    console.input("\nНажмите Enter, чтобы вернуться в меню...")


def run_menu(db: Database):
    while True:
        show_header()
        show_menu()

        choice = console.input("\nВаш выбор: ")

        if choice == "1":
            register_patient_menu(db)
        elif choice == "2":
            show_patients(db)
        elif choice == "3":
            create_appointment_menu(db)
        elif choice == "4":
            show_future_appointments(db)
        elif choice == "5":
            cancel_appointment_menu(db)
        elif choice == "6":
            show_medical_card_menu(db)
        elif choice == "0":
            break
        else:
            console.print("[red]Неверный выбор, попробуйте снова.[/red]")