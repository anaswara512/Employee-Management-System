import sqlite3

DATABASE_NAME = "employee_management.db"


def connect_db():
    connection = sqlite3.connect(DATABASE_NAME)

    # Enable foreign-key enforcement
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_tables():
    connection = connect_db()
    cursor = connection.cursor()

    # ---------------- DEPARTMENTS ----------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            department_id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_name TEXT NOT NULL UNIQUE
        )
    """)

    # ---------------- EMPLOYEES ----------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            department_id INTEGER NOT NULL,
            designation TEXT NOT NULL,
            salary REAL NOT NULL CHECK(salary >= 0),

            FOREIGN KEY (department_id)
                REFERENCES departments(department_id)
        )
    """)

    # ---------------- USERS ----------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,

            role TEXT NOT NULL
                CHECK(role IN ('HR', 'Employee')),

            employee_id INTEGER UNIQUE,

            FOREIGN KEY (employee_id)
                REFERENCES employees(employee_id)
                ON UPDATE CASCADE
                ON DELETE SET NULL
        )
    """)

    # ---------------- ATTENDANCE ----------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,

            status TEXT NOT NULL
                CHECK(status IN ('Present', 'Absent', 'Leave')),

            FOREIGN KEY (employee_id)
                REFERENCES employees(employee_id)
                ON UPDATE CASCADE
                ON DELETE CASCADE,

            UNIQUE(employee_id, attendance_date)
        )
    """)

    connection.commit()
    connection.close()

    print("Employee Management System database created successfully.")


if __name__ == "__main__":
    create_tables()