from datetime import datetime, date, time, timedelta

from db.database import Database


# КОНСТАНТЫ 
WORK_START = time(9, 0) # начало рабочего дня (старт первого слота времени)
LAST_SLOT_START = time(16, 30) # начало последнего временного слота для записи
APPOINTMENT_DURATION = timedelta(minutes=30) # длительность приема - 30 минут
BOOKING_HORIZON_DAYS = 14 # запись будет доступна на 14 дней вперед


def get_all_doctors(db: Database) -> list[tuple[int, str]]:
    """
    Получение списка всех врачей (id, ФИО).
    Используется во время записи пациента на прием.
    """
    conn = db.get_connection()
    
    query = """
        SELECT id, full_name
        FROM doctors
        ORDER BY id
    """

    with conn.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()    


def doctor_exists(db: Database, doctor_id: int) -> bool:
    """
    Проверка сущестования врача по id.
    """
    conn = db.get_connection()

    query = "SELECT 1 FROM doctors WHERE id = %s LIMIT 1"

    with conn.cursor() as cursor:
        cursor.execute(query, (doctor_id,))
        # запись о враче is not None = True (врач существует)
        return cursor.fetchone() is not None


def patient_exists(db: Database, patient_id: int) -> bool:
    """
    Проверка существования пациента по id.
    """
    conn = db.get_connection()

    query = "SELECT 1 FROM patients WHERE id = %s LIMIT 1"

    with conn.cursor() as cursor:
        cursor.execute(query, (patient_id,))
        # запись о пациенте is not None = True (пациент существует)
        return cursor.fetchone() is not None


def get_available_dates() -> list[date]:
    """
    Возвращает список доступных дат для записи.
    Сегодня + 14 дней.
    """
    today = date.today()

    return [today + timedelta(days=i) for i in range(BOOKING_HORIZON_DAYS)]


def generate_daily_slots(day: date) -> list[datetime]:
    """
    Генерирует все возможные слоты для записи на день.
    Первый - 9:00, последний - 16:30 (все по 30 минут).
    """
    slots = []

    current = datetime.combine(day, WORK_START)
    last_slot = datetime.combine(day, LAST_SLOT_START)

    while current <= last_slot:
        slots.append(current)
        current += APPOINTMENT_DURATION

    return slots


def get_busy_slots(db: Database, doctor_id: int, day: date) -> set[datetime]:
    """
    Возвращает занятые временные слоты врача за день.
    """
    conn = db.get_connection()

    query = """
        SELECT date_time
        FROM appointments
        WHERE doctor_id = %s
          AND DATE(date_time) = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (doctor_id, day))
        rows = cursor.fetchall()

    return {row[0] for row in rows}


def get_available_slots_for_day(db: Database, doctor_id: int, day: date) -> list[datetime]:
    """
    Возвращает доступные временные слоты врача на выбранный день.
    """
    all_slots = generate_daily_slots(day)
    busy_slots = get_busy_slots(db, doctor_id, day)

    now = datetime.now()

    available = []

    for slot in all_slots:
        # если сегодня — убираем прошедшие
        if day == now.date() and slot <= now:
            continue

        if slot not in busy_slots:
            available.append(slot)

    return available


def is_doctor_available(db: Database, doctor_id: int, appointment_datetime: datetime) -> bool:
    """
    Проверка, свободен ли доктор в указанный временной интервал.
    """
    conn = db.get_connection()

    new_start = appointment_datetime
    new_end = appointment_datetime + APPOINTMENT_DURATION

    query = """
        SELECT 1
        FROM appointments
        WHERE doctor_id = %s
          AND date_time < %s
          AND (date_time + INTERVAL '30 minutes') > %s
        LIMIT 1
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (doctor_id, new_end, new_start))
        # если ничего не вернулось, None is None = True (доктор свободен)
        return cursor.fetchone() is None 


def create_appointment(db: Database, patient_id: int, doctor_id: int, appointment_datetime: datetime) -> None:
    """
    Создание записи на прием.
    
    Примечания:
    - проверяется, существует ли выбранный пациент и доктор в БД;
    - проверяется, свободен ли врач в выбранное нами время;
    - учитывается длительность приема (30 минут);
    - расписание врачей не учитывается (!!!).
    """
    
    if not patient_exists(db, patient_id):
        raise ValueError("Пациент с таким id не найден.")
    
    if not doctor_exists(db, doctor_id):
        raise ValueError("Врач c таким id не найден.")
    
    if not is_doctor_available(db, doctor_id, appointment_datetime):
        raise ValueError("Врач уже занят в это время.")

    conn = db.get_connection()

    query = """
        INSERT INTO appointments (patient_id, doctor_id, date_time)
        VALUES (%s, %s, %s)
    """

    with conn.cursor() as cursor:
        cursor.execute(
            query,
            (patient_id, doctor_id, appointment_datetime)
        )

    conn.commit()


def get_future_appointments(db: Database) -> list[tuple[int, str, str, datetime]]:
    """
    Получение списка всех предстоящих записей (просто для просмотра).
    Список содержит id записи, имя пациента, ФИО доктора и дату и время приема.
    """
    conn = db.get_connection()

    query = """
        SELECT
            a.id,
            p.name AS patient_name,
            d.full_name AS doctor_name,
            a.date_time
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        WHERE a.date_time >= NOW()
        ORDER BY a.date_time
    """

    with conn.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def delete_appointment(db: Database, appointment_id: int) -> bool:
    """
    Отмена записи на прием по id.
    Возвращает True, если запись была удалена.
    """
    conn = db.get_connection()

    query = """
        DELETE FROM appointments
        WHERE id = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (appointment_id,))
        deleted = cursor.rowcount # получаем количество удаленных записей

    conn.commit()

    # если запись была удалена, возвращаем True
    return deleted > 0