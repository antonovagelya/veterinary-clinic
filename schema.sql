-- Таблица владельцев
CREATE TABLE owners (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) UNIQUE NOT NULL
);

-- Таблица пациентов (животных)
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    species VARCHAR(100) NOT NULL,
    CONSTRAINT fk_patients_owner
        FOREIGN KEY (owner_id)
        REFERENCES owners(id)
);

-- Таблица врачей
CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL
);

-- Таблица записей на прием
CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    date_time TIMESTAMP NOT NULL,
    CONSTRAINT fk_appointments_patient
        FOREIGN KEY (patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_appointments_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctors(id)
        ON DELETE CASCADE,
    CONSTRAINT unique_doctor_datetime
        UNIQUE (doctor_id, date_time)

);

-- Тестовые данные
INSERT INTO owners (full_name, phone) VALUES
('Иванов Иван Иванович', '+79161234567'),
('Петрова Анна Сергеевна', '+79031234568'),
('Сидоров Алексей Владимирович', '+79261234569');

INSERT INTO patients (owner_id, name, species) VALUES
(1, 'Барсик', 'Кот'),
(1, 'Шарик', 'Собака'),
(2, 'Мурка', 'Кошка'),
(3, 'Кеша', 'Попугай');

INSERT INTO doctors (full_name) VALUES
('Смирнова Ольга Петровна'),
('Кузнецов Дмитрий Алексеевич');
