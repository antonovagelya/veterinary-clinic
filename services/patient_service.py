from typing import Optional
from datetime import datetime

from db.database import Database
from db.models import Owner, Patient


def get_owner_by_phone(db: Database, phone: str) -> Optional[Owner]:
    """
    Ищет владельца по номеру телефона.
    Возвращает Owner или None, если хозяин не найден.
    """
    conn = db.get_connection() 

    query = """
        SELECT id, full_name, phone
        FROM owners
        WHERE phone = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (phone,))
        row = cursor.fetchone()

    if row is None:
        return None

    return Owner(
        id=row[0],
        full_name=row[1],
        phone=row[2]
    )


def create_owner(db: Database, owner: Owner) -> Owner:
    """
    Создает нового владельца в БД и возвращает его с id.
    """
    conn = db.get_connection()

    query = """
        INSERT INTO owners (full_name, phone)
        VALUES (%s, %s)
        RETURNING id
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (owner.full_name, owner.phone))
        owner_id = cursor.fetchone()[0]

    conn.commit()

    owner.id = owner_id # присваиваем объекту id, назначенный базой данных
    return owner


def create_patient(db: Database, patient: Patient) -> Patient:
    """
    Создает нового пациента в БД и возвращает его с id.
    """
    conn = db.get_connection()

    query = """
        INSERT INTO patients (owner_id, name, species)
        VALUES (%s, %s, %s)
        RETURNING id
    """

    with conn.cursor() as cursor:
        cursor.execute(
            query,
            (patient.owner_id, patient.name, patient.species)
        )
        patient_id = cursor.fetchone()[0]

    conn.commit()

    patient.id = patient_id
    return patient


def register_patient(
    db: Database,
    owner_full_name: str,
    owner_phone: str,
    patient_name: str,
    species: str
) -> Patient:
    """
    Регистрирует нового пациента.
    Если владелец уже существует — используется он, иначе создается новый.
    """
    owner = get_owner_by_phone(db, owner_phone)

    if owner is None:
        owner = Owner(
            id=None,
            full_name=owner_full_name,
            phone=owner_phone
        )
        owner = create_owner(db, owner)

    patient = Patient(
        id=None,
        owner_id=owner.id,
        name=patient_name,
        species=species
    )

    return create_patient(db, patient)


def get_all_patients(db: Database) -> list[tuple[int, str, str, str, str]]:
    """
    Возвращает список всех пациентов с данными о владельцах.
    """
    conn = db.get_connection()

    query = """
        SELECT
            p.id,
            p.name,
            p.species,
            o.full_name,
            o.phone
        FROM patients p
        JOIN owners o ON p.owner_id = o.id
        ORDER BY p.id
    """

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    return rows


def get_patient_card_info(db: Database, patient_id: int) -> Optional[tuple[int, str, str, str, str]]:
    """
    Возвращает информацию для шапки медкарты пациента
    """
    conn = db.get_connection()

    query = """
        SELECT
            p.id,
            p.name,
            p.species,
            o.full_name,
            o.phone
        FROM patients p
        JOIN owners o ON p.owner_id = o.id
        WHERE p.id = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (patient_id,))
        return cursor.fetchone()


def get_patient_appointments(db: Database, patient_id: int) -> list[tuple[int, str, datetime]]:
    """
    Возвращает список всех записей клиента (прошедших и будущих).
    Используется в медкарте.
    """
    conn = db.get_connection()

    query = """
        SELECT
            a.id,
            d.full_name,
            a.date_time
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        WHERE a.patient_id = %s
        ORDER BY a.date_time
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (patient_id,))
        return cursor.fetchall()

