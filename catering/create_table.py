import psycopg2

connection = psycopg2.connect(
    dbname="catering_service",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)

cur = connection.cursor()

create_tables_query = '''
-- Create citizens table
CREATE TABLE IF NOT EXISTS citizens (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT CHECK (age >= 0),
    address TEXT,
    employment_status VARCHAR(100),
    education_level VARCHAR(100)
);


-- Create public_services table
CREATE TABLE IF NOT EXISTS public_services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);


-- Create service_usage table
CREATE TABLE IF NOT EXISTS service_usage (
    id SERIAL PRIMARY KEY,
    citizen_id INT REFERENCES citizens(id) ON DELETE CASCADE,
    service_id INT REFERENCES public_services(id) ON DELETE CASCADE,
    usage_date DATE NOT NULL,
    frequency INT DEFAULT 1
);


-- Create infrastructure table
CREATE TABLE IF NOT EXISTS infrastructure (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    location TEXT,
    last_maintenance_date DATE,
    scheduled_maintenance_date DATE
);


-- Create social_programs table
CREATE TABLE IF NOT EXISTS social_programs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    budget DECIMAL(15,2)
);


-- Create program_enrollment table
CREATE TABLE IF NOT EXISTS program_enrollment (
    id SERIAL PRIMARY KEY,
    citizen_id INT REFERENCES citizens(id) ON DELETE CASCADE,
    program_id INT REFERENCES social_programs(id) ON DELETE CASCADE,
    enrollment_date DATE NOT NULL
);


-- Create gov_employees table
CREATE TABLE IF NOT EXISTS gov_employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    role VARCHAR(100)
);


-- Create service_requests table
CREATE TABLE IF NOT EXISTS service_requests (
    id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES gov_employees(id) ON DELETE SET NULL,
    citizen_id INT REFERENCES citizens(id) ON DELETE CASCADE,
    service_id INT REFERENCES public_services(id) ON DELETE CASCADE,
    request_date DATE NOT NULL
);
'''


insert_citizens_query = '''
INSERT INTO citizens (name, age, address, employment_status, education_level)
VALUES
('John Doe', 35, '1234 Elm Street, Springfield', 'Employed', 'Bachelor'),
('Jane Smith', 28, '5678 Oak Avenue, Springfield', 'Unemployed', 'Master'),
('Emily Johnson', 45, '9101 Pine Road, Springfield', 'Employed', 'High School');
'''

cur.execute(insert_citizens_query)


insert_citizens_query = '''
INSERT INTO citizens (name, age, address, employment_status, education_level)
VALUES
('John Doe', 35, '1234 Elm Street, Springfield', 'Employed', 'Bachelor'),
('Jane Smith', 28, '5678 Oak Avenue, Springfield', 'Unemployed', 'Master'),
('Emily Johnson', 45, '9101 Pine Road, Springfield', 'Employed', 'High School');
'''

insert_public_services_query = '''
INSERT INTO public_services (name, description)
VALUES
('Healthcare', 'Medical care and health services'),
('Education', 'Primary and secondary education services'),
('Social Security', 'Government assistance for low-income families')
ON CONFLICT (name) DO NOTHING;
'''


insert_service_usage_query = '''
INSERT INTO service_usage (citizen_id, service_id, usage_date, frequency)
VALUES
(1, 1, '2025-01-10', 3),
(2, 2, '2025-01-15', 1),
(3, 3, '2025-01-20', 2);
'''

insert_infrastructure_query = '''
INSERT INTO infrastructure (name, type, location, last_maintenance_date, scheduled_maintenance_date)
VALUES
('Bridge 1', 'Bridge', 'Springfield River', '2024-12-01', '2025-03-01'),
('School A', 'School', 'Main Street', '2024-10-15', '2025-02-15'),
('Hospital 1', 'Hospital', 'East End', '2024-11-01', '2025-04-01');
'''

insert_social_programs_query = '''
INSERT INTO social_programs (name, description, budget)
VALUES
('Youth Education Program', 'Program to support youth education in low-income families', 100000.00),
('Senior Care Program', 'Providing healthcare and social services for seniors', 50000.00),
('Food Assistance Program', 'Providing food assistance to low-income individuals', 20000.00)
ON CONFLICT (name) DO NOTHING;
'''

insert_program_enrollment_query = '''
INSERT INTO program_enrollment (citizen_id, program_id, enrollment_date)
VALUES
(1, 1, '2025-01-05'),
(2, 2, '2025-01-10'),
(3, 3, '2025-01-15');
'''

insert_gov_employees_query = '''
INSERT INTO gov_employees (name, department, role)
VALUES
('Michael Brown', 'Health Department', 'Doctor'),
('Sarah White', 'Education Department', 'Teacher'),
('David Green', 'Social Services', 'Counselor');
'''

insert_service_requests_query = '''
INSERT INTO service_requests (employee_id, citizen_id, service_id, request_date)
VALUES
(1, 1, 1, '2025-01-12'),
(2, 2, 2, '2025-01-18'),
(3, 3, 3, '2025-01-22');
'''


# Выполнение запросов на создание таблиц и индексов
cur.execute(create_tables_query)

# Индексация для ускорения поиска граждан
index_queries = [
    "CREATE INDEX IF NOT EXISTS idx_service_usage_citizen_id ON service_usage(citizen_id);",
    "CREATE INDEX IF NOT EXISTS idx_program_enrollment_citizen_id ON program_enrollment(citizen_id);",
    "CREATE INDEX IF NOT EXISTS idx_service_usage_service_id ON service_usage(service_id);",
    "CREATE INDEX IF NOT EXISTS idx_program_enrollment_program_id ON program_enrollment(program_id);"
]

# Выполнение запросов для создания индексов
for query in index_queries:
    try:
        cur.execute(query)
        print(f"Index created: {query}")
    except psycopg2.errors.DuplicateObject:
        print(f"Index already exists: {query}")

# Выполнение запросов на вставку данных
cur.execute(insert_citizens_query)
cur.execute(insert_public_services_query)
cur.execute(insert_service_usage_query)
cur.execute(insert_infrastructure_query)
cur.execute(insert_social_programs_query)
cur.execute(insert_program_enrollment_query)
cur.execute(insert_gov_employees_query)
cur.execute(insert_service_requests_query)


# Создание материализованного представления для отслеживания ежемесячных тенденций использования услуг
cur.execute('''
CREATE MATERIALIZED VIEW IF NOT EXISTS monthly_service_usage AS
SELECT
    EXTRACT(YEAR FROM usage_date) AS usage_year,
    EXTRACT(MONTH FROM usage_date) AS usage_month,
    service_id,
    SUM(frequency) AS total_usage
FROM service_usage
GROUP BY
    usage_year, usage_month, service_id
ORDER BY
    usage_year, usage_month, service_id;
''')

# Обновление материализованного представления
cur.execute('REFRESH MATERIALIZED VIEW monthly_service_usage;')

connection.commit()

cur.close()

# Теперь создадим новое соединение для выполнения VACUUM вне транзакции
vacuum_connection = psycopg2.connect(
    dbname="catering_service",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)

# Отключаем автоматическое начало транзакции
vacuum_connection.autocommit = True

# Выполняем VACUUM в новом соединении
vacuum_cur = vacuum_connection.cursor()
vacuum_cur.execute("VACUUM (VERBOSE, ANALYZE);")

# Закрываем соединение для VACUUM
vacuum_cur.close()
vacuum_connection.close()

# Закрываем основное соединение
connection.close()
