from typing import Optional
from datetime import datetime


class Owner:
    """Класс для представления хозяев животных"""

    def __init__(
            self,
            id: Optional[int],
            full_name: str,
            phone: str
    ):
        """
        Конструктор класса Owner
        
        Аргументы:
            id: идентификатор хозяина (может быть None до сохранения в БД)
            full_name: полное имя хозяина
            phone: номер телефона
        """
        self.id = id
        self.full_name = full_name
        self.phone = phone


    def __repr__(self):
        """Строковое представление (для отладки)"""
        return f"Owner(id={self.id}, full_name='{self.full_name}', phone='{self.phone}')"
    


class Patient:
    """Класс для представления пациентов клиники (животных)"""

    def __init__(
            self,
            id: Optional[int],
            owner_id: int,
            name: str,
            species: str       
    ):
        """
        Конструктор класса Patient

        Аргументы:
            id: идентификатор пациента (может быть None до сохранения в БД)
            owner_id: идентификатор хозяина
            name: имя животного
            species: вид (например, кошка или собака)
        """
        self.id = id
        self.owner_id = owner_id
        self.name = name
        self.species = species


    def __repr__(self):
        """Строковое представление (для отладки)"""
        return f"Patient(id={self.id}, owner_id={self.owner_id}, name='{self.name}', species='{self.species}')"
    


class Doctor:
    """Класс для представления докторов клиники"""
    def __init__(
            self,
            id: Optional[int],
            full_name: str
    ):
        """
        Конструктор класса Doctor

        Аргументы:
            id: идентификатор доктора (может быть None до сохранения в БД)
            full_name: полное имя доктора
            cabinet_number: номер кабинета
        """
        self.id = id
        self.full_name = full_name


    def __repr__(self):
        """Строковое представление (для отладки)"""
        return f"Doctor(id={self.id}, full_name='{self.full_name}')"
    


class Appointment:
    """Класс для представления записей на прием"""

    def __init__(
            self,
            id: Optional[int],
            patient_id: int,
            doctor_id: int,
            date_time: datetime
    ):
        """
        Конструктор класса Appointment

        Аргументы:
            id: идентификатор записи (может быть None до сохранения в БД)
            patient_id: идентификатор пациента, записанного на прием
            doctor_id: идентификатор доктора, проводящего прием
            date_time: дата и время приема
        """
        self.id = id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.date_time = date_time


    def __repr__(self):
        """Строковое представление (для отладки)"""
        return f"Appointment(id={self.id}, patient_id={self.patient_id}, doctor_id={self.doctor_id}, date_time='{self.date_time}')"