import psycopg2

connection = psycopg2.connect(
    dbname="catering_service",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)

cur = connection.cursor()

# 1
query = """
    SELECT ps.name AS service_name, COUNT(su.id) AS usage_count
    FROM service_usage su
    JOIN public_services ps ON su.service_id = ps.id
    GROUP BY ps.name
    ORDER BY usage_count DESC;
"""

cur.execute(query)

results = cur.fetchall()

for row in results:
    print(f"Service: {row[0]}, Usage Count: {row[1]}")


# 2
age_groups_query = '''
SELECT
    CASE
        WHEN c.age BETWEEN 0 AND 17 THEN '0-17'
        WHEN c.age BETWEEN 18 AND 35 THEN '18-35'
        WHEN c.age BETWEEN 36 AND 50 THEN '36-50'
        WHEN c.age BETWEEN 51 AND 65 THEN '51-65'
        ELSE '65+'
    END AS age_group,
    COUNT(su.id) AS service_usage_count
FROM citizens c
JOIN service_usage su ON c.id = su.citizen_id
GROUP BY age_group
ORDER BY service_usage_count DESC;
'''

cur.execute(age_groups_query)
age_groups = cur.fetchall()

print("Age Groups and Service Usage Count:")
for row in age_groups:
    print(f"Age Group: {row[0]}, Service Usage Count: {row[1]}")
print("\n")


# 3
social_programs_query = '''
SELECT sp.name AS program_name, COUNT(pe.id) AS enrollment_count
FROM program_enrollment pe
JOIN social_programs sp ON pe.program_id = sp.id
GROUP BY sp.name
ORDER BY enrollment_count DESC
LIMIT 5;
'''

cur.execute(social_programs_query)
programs = cur.fetchall()

print("Top 5 Social Programs by Enrollment Count:")
for row in programs:
    print(f"Program Name: {row[0]}, Enrollment Count: {row[1]}")
print("\n")


# 4
gov_employees_query = '''
SELECT ge.name AS employee_name, COUNT(sr.id) AS requests_handled
FROM service_requests sr
JOIN gov_employees ge ON sr.employee_id = ge.id
GROUP BY ge.name
ORDER BY requests_handled DESC
LIMIT 5;
'''

cur.execute(gov_employees_query)
employees = cur.fetchall()

print("Top 5 Government Employees by Requests Handled:")
for row in employees:
    print(f"Employee Name: {row[0]}, Requests Handled: {row[1]}")
print("\n")

# 5
infrastructure_query = '''
SELECT i.name AS infrastructure_name, i.last_maintenance_date, i.scheduled_maintenance_date
FROM infrastructure i
WHERE i.scheduled_maintenance_date < CURRENT_DATE
AND (i.last_maintenance_date IS NULL OR i.last_maintenance_date < i.scheduled_maintenance_date);
'''

cur.execute(infrastructure_query)
infrastructure_projects = cur.fetchall()

print("Overdue Infrastructure Projects for Maintenance:")
for row in infrastructure_projects:
    print(f"Infrastructure Name: {row[0]}, Last Maintenance: {row[1]}, Scheduled Maintenance: {row[2]}")


cur.close()
connection.close()
