import sqlite3
from database import create_tables, connect_db
from datetime import date

def select_role():
    while True:
        print("\nSelect Role")
        print("1. HR")
        print("2. Employee")

        choice = input("Enter your choice: ")

        if choice == "1":
            return "HR"
        elif choice == "2":
            return "Employee"
        else:
            print("Invalid choice. Please try again.")


def sign_up():
    print("\n" + "=" * 45)
    print("SIGN UP")
    print("=" * 45)

    username = input("Enter username: ")
    password = input("Enter password: ")
    
    if not username or not password:
        print("Username and password cannot be empty.")
        return

    role = select_role()

    connection = connect_db()
    cursor = connection.cursor()

    try:

        # ---------------- HR SIGN UP ----------------

        if role == "HR":

            cursor.execute("""
                INSERT INTO users
                (username, password, role, employee_id)
                VALUES (?, ?, ?, ?)
            """, (
                username,
                password,
                "HR",
                None
            ))

        # ---------------- EMPLOYEE SIGN UP ----------------

        elif role == "Employee":

            try:
                employee_id = int(
                    input("Enter your Employee ID: ").strip()
                )
            except ValueError:
                print("Employee ID must be a number.")
                return

            email = input(
                "Enter your registered employee email: "
            ).strip()

            # Verify employee
            cursor.execute("""
                SELECT employee_id, name, email
                FROM employees
                WHERE employee_id = ?
                  AND email = ?
            """, (
                employee_id,
                email
            ))

            employee = cursor.fetchone()

            if not employee:
                print(
                    "\nEmployee ID and email do not match "
                    "any employee record."
                )
                return

            # Check whether this employee already has an account
            cursor.execute("""
                SELECT user_id
                FROM users
                WHERE employee_id = ?
            """, (employee_id,))

            existing_account = cursor.fetchone()

            if existing_account:
                print(
                    "\nThis employee already has a login account."
                )
                return

            # Create employee account
            cursor.execute("""
                INSERT INTO users
                (username, password, role, employee_id)
                VALUES (?, ?, ?, ?)
            """, (
                username,
                password,
                "Employee",
                employee_id
            ))

        connection.commit()

        print("\n" + "=" * 45)
        print("ACCOUNT CREATED SUCCESSFULLY")
        print("=" * 45)

        print(f"Username : {username}")
        print(f"Role     : {role}")

        if role == "Employee":
            print(f"Employee ID : {employee_id}")

        print("=" * 45)

    except sqlite3.IntegrityError as error:

        error_message = str(error).lower()

        if "username" in error_message:
            print("\nUsername already exists.")

        elif "employee_id" in error_message:
            print(
                "\nThis employee is already linked "
                "to another account."
            )

        else:
            print("\nUnable to create account.")
            print("Database error:", error)

    finally:
        connection.close()


def sign_in():
    print("\n" + "=" * 45)
    print("SIGN IN")
    print("=" * 45)

    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    if not username or not password:
        print("Username and password are required.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT
                user_id,
                username,
                role,
                employee_id
            FROM users
            WHERE username = ?
              AND password = ?
        """, (
            username,
            password
        ))

        user = cursor.fetchone()

    finally:
        connection.close()

    if not user:
        print("\nInvalid username or password.")
        return

    user_id = user[0]
    username = user[1]
    role = user[2]
    employee_id = user[3]

    print("\n" + "=" * 45)
    print("LOGIN SUCCESSFUL")
    print("=" * 45)

    print(f"Welcome : {username}")
    print(f"Role    : {role}")

    # ---------------- HR ----------------

    if role == "HR":

        hr_menu(
            user_id,
            username
        )

    # ---------------- EMPLOYEE ----------------

    elif role == "Employee":

        if employee_id is None:
            print(
                "\nError: This Employee account "
                "is not linked to an employee record."
            )
            return

        employee_menu(
            employee_id,
            username
        )


def role_menu(role, username, employee_id=None):

    if role == "HR":
        hr_menu()

    elif role == "Employee":
        employee_menu(employee_id)

def add_department():
    print("\n" + "============")
    print("ADD DEPARTMENT")
    print("============")

    department_name = input("Enter department name: ").strip()

    if department_name == "":
        print("Department name cannot be empty.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO departments (department_name)
            VALUES (?)
        """, (department_name,))

        connection.commit()
        print("Department added successfully.")

    except sqlite3.IntegrityError:
        print("Department already exists.")

    finally:
        connection.close()


def view_departments():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT department_id, department_name
        FROM departments
        ORDER BY department_id
    """)

    departments = cursor.fetchall()

    connection.close()

    print("\n" + "============")
    print("DEPARTMENTS")
    print("============")

    if not departments:
        print("No departments found.")
        return

    print("ID\tDepartment")
    print("-" * 40)

    for department in departments:
        print(f"{department[0]}\t{department[1]}")


def employee_management_menu():

    while True:

        print("\n" + "=" * 50)
        print("              EMPLOYEE MANAGEMENT")
        print("=" * 50)

        print("1. Add Employee")
        print("2. View All Employees")
        print("3. Search Employee")
        print("4. Update Employee")
        print("5. Delete Employee")
        print("6. Back")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        if choice == "1":
            add_employee()

        elif choice == "2":
            view_employees()

        elif choice == "3":
            search_employee()

        elif choice == "4":
            update_employee()

        elif choice == "5":
            delete_employee()
            
        elif choice == "6":
            break

        else:
            print("Invalid choice.")


def add_employee():
    print("\n" + "=" * 50)
    print("                  ADD EMPLOYEE")
    print("=" * 50)

    name = input("Enter employee name: ").strip()
    email = input("Enter email: ").strip()
    phone = input("Enter phone number: ").strip()
    designation = input("Enter designation: ").strip()

    if not name or not email or not phone or not designation:
        print("\nAll fields are required.")
        return

    # Email validation
    if "@" not in email or "." not in email.split("@")[-1]:
        print("\nInvalid email address.")
        return

    # Phone validation
    if not phone.isdigit() or not 7 <= len(phone) <= 15:
        print("\nPhone number must contain 7 to 15 digits.")
        return

    # Display departments
    view_departments()

    try:
        department_id = int(
            input("\nEnter Department ID: ").strip()
        )
    except ValueError:
        print("Department ID must be a number.")
        return

    try:
        salary = float(
            input("Enter salary: ").strip()
        )
    except ValueError:
        print("Salary must be a number.")
        return

    if salary < 0:
        print("Salary cannot be negative.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    try:
        # Check department
        cursor.execute("""
            SELECT department_id
            FROM departments
            WHERE department_id = ?
        """, (department_id,))

        if cursor.fetchone() is None:
            print("\nDepartment does not exist.")
            return

        # Insert employee
        cursor.execute("""
            INSERT INTO employees
            (
                name,
                email,
                phone,
                department_id,
                designation,
                salary
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            email,
            phone,
            department_id,
            designation,
            salary
        ))

        connection.commit()

        employee_id = cursor.lastrowid

        print("\nEmployee added successfully.")
        print(f"Employee ID: {employee_id}")

    except sqlite3.IntegrityError as error:

        if "email" in str(error).lower():
            print("\nAn employee with this email already exists.")
        else:
            print("\nUnable to add employee.")
            print("Database error:", error)

    finally:
        connection.close()


def view_employees():
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                e.employee_id,
                e.name,
                e.email,
                e.phone,
                d.department_name,
                e.designation,
                e.salary
            FROM employees e
            JOIN departments d
                ON e.department_id = d.department_id
            ORDER BY e.employee_id
        """)

        employees = cursor.fetchall()

        print("\n" + "=" * 90)
        print("                     EMPLOYEE LIST")
        print("=" * 90)

        if not employees:
            print("No employees found.")
            return

        for employee in employees:

            print(f"\nEmployee ID : {employee[0]}")
            print(f"Name        : {employee[1]}")
            print(f"Email       : {employee[2]}")
            print(f"Phone       : {employee[3]}")
            print(f"Department  : {employee[4]}")
            print(f"Designation : {employee[5]}")
            print(f"Salary      : ₹{employee[6]:,.2f}")

            print("-" * 55)

    except sqlite3.Error as error:
        print(f"Database error: {error}")

    finally:
        connection.close()


def search_employee():
    print("\n" + "=" * 50)
    print("                 SEARCH EMPLOYEE")
    print("=" * 50)

    keyword = input(
        "Enter Employee ID or Name: "
    ).strip()

    if not keyword:
        print("Search value cannot be empty.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    try:

        if keyword.isdigit():

            cursor.execute("""
                SELECT
                    e.employee_id,
                    e.name,
                    e.email,
                    e.phone,
                    d.department_name,
                    e.designation,
                    e.salary
                FROM employees e
                JOIN departments d
                    ON e.department_id = d.department_id
                WHERE e.employee_id = ?
            """, (int(keyword),))

        else:

            cursor.execute("""
                SELECT
                    e.employee_id,
                    e.name,
                    e.email,
                    e.phone,
                    d.department_name,
                    e.designation,
                    e.salary
                FROM employees e
                JOIN departments d
                    ON e.department_id = d.department_id
                WHERE e.name LIKE ?
                ORDER BY e.name
            """, (
                "%" + keyword + "%",
            ))

        employees = cursor.fetchall()

        if not employees:
            print("\nEmployee not found.")
            return

        print("\nSearch Results")
        print("-" * 60)

        for employee in employees:

            print(f"Employee ID : {employee[0]}")
            print(f"Name        : {employee[1]}")
            print(f"Email       : {employee[2]}")
            print(f"Phone       : {employee[3]}")
            print(f"Department  : {employee[4]}")
            print(f"Designation : {employee[5]}")
            print(f"Salary      : ₹{employee[6]:,.2f}")

            print("-" * 60)

    except sqlite3.Error as error:
        print(f"Database error: {error}")

    finally:
        connection.close()


def update_employee():
    print("\n" + "=" * 50)
    print("                 UPDATE EMPLOYEE")
    print("=" * 50)

    try:
        employee_id = int(
            input("Enter Employee ID: ").strip()
        )
    except ValueError:
        print("Employee ID must be a number.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT
                name,
                email,
                phone,
                department_id,
                designation,
                salary
            FROM employees
            WHERE employee_id = ?
        """, (employee_id,))

        employee = cursor.fetchone()

        if not employee:
            print("\nEmployee not found.")
            return

        print("\nPress Enter to keep the existing value.")

        name = input(
            f"Name [{employee[0]}]: "
        ).strip() or employee[0]

        email = input(
            f"Email [{employee[1]}]: "
        ).strip() or employee[1]

        phone = input(
            f"Phone [{employee[2]}]: "
        ).strip() or employee[2]

        designation = input(
            f"Designation [{employee[4]}]: "
        ).strip() or employee[4]

        if "@" not in email or "." not in email.split("@")[-1]:
            print("Invalid email address.")
            return

        if not phone.isdigit() or not 7 <= len(phone) <= 15:
            print("Phone number must contain 7 to 15 digits.")
            return

        view_departments()

        department_input = input(
            f"Department ID [{employee[3]}]: "
        ).strip()

        if department_input:
            try:
                department_id = int(department_input)
            except ValueError:
                print("Department ID must be a number.")
                return
        else:
            department_id = employee[3]

        cursor.execute("""
            SELECT department_id
            FROM departments
            WHERE department_id = ?
        """, (department_id,))

        if cursor.fetchone() is None:
            print("Department does not exist.")
            return

        salary_input = input(
            f"Salary [{employee[5]}]: "
        ).strip()

        if salary_input:
            try:
                salary = float(salary_input)
            except ValueError:
                print("Salary must be a number.")
                return
        else:
            salary = employee[5]

        if salary < 0:
            print("Salary cannot be negative.")
            return

        cursor.execute("""
            UPDATE employees
            SET
                name = ?,
                email = ?,
                phone = ?,
                department_id = ?,
                designation = ?,
                salary = ?
            WHERE employee_id = ?
        """, (
            name,
            email,
            phone,
            department_id,
            designation,
            salary,
            employee_id
        ))

        connection.commit()

        print("\nEmployee updated successfully.")

    except sqlite3.IntegrityError:

        print(
            "\nAnother employee already uses this email."
        )

    except sqlite3.Error as error:

        print(f"\nDatabase error: {error}")

    finally:
        connection.close()


def delete_employee():
    print("\n" + "=" * 50)
    print("                 DELETE EMPLOYEE")
    print("=" * 50)

    try:
        employee_id = int(
            input("Enter Employee ID: ").strip()
        )
    except ValueError:
        print("Employee ID must be a number.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT
                name,
                email
            FROM employees
            WHERE employee_id = ?
        """, (employee_id,))

        employee = cursor.fetchone()

        if not employee:
            print("\nEmployee not found.")
            return

        print("\nEmployee Details")
        print("-" * 40)
        print(f"Employee ID : {employee_id}")
        print(f"Name        : {employee[0]}")
        print(f"Email       : {employee[1]}")

        confirmation = input(
            "\nAre you sure you want to delete this employee? (y/n): "
        ).strip().lower()

        if confirmation != "y":
            print("Deletion cancelled.")
            return

        cursor.execute("""
            DELETE FROM employees
            WHERE employee_id = ?
        """, (employee_id,))

        connection.commit()

        print("\nEmployee deleted successfully.")

    except sqlite3.IntegrityError as error:

        print("\nEmployee cannot be deleted.")
        print("Database error:", error)

    except sqlite3.Error as error:

        print("\nDatabase error:", error)

    finally:
        connection.close()


def mark_attendance():
    print("\n" + "=" * 55)
    print("                 MARK ATTENDANCE")
    print("=" * 55)

    try:
        employee_id = int(
            input("Enter Employee ID: ").strip()
        )
    except ValueError:
        print("Employee ID must be a number.")
        return

    attendance_date = input(
        "Enter date (YYYY-MM-DD) [Today]: "
    ).strip()

    if attendance_date == "":
        attendance_date = date.today().isoformat()

    # Validate date
    try:
        date.fromisoformat(attendance_date)
    except ValueError:
        print("Invalid date. Use YYYY-MM-DD.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    try:
        # Check employee
        cursor.execute("""
            SELECT
                employee_id,
                name
            FROM employees
            WHERE employee_id = ?
        """, (employee_id,))

        employee = cursor.fetchone()

        if not employee:
            print("\nEmployee not found.")
            return

        print("\nEmployee:")
        print(f"ID   : {employee[0]}")
        print(f"Name : {employee[1]}")

        print("\nSelect Attendance Status")
        print("1. Present")
        print("2. Absent")
        print("3. Leave")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        status_map = {
            "1": "Present",
            "2": "Absent",
            "3": "Leave"
        }

        if choice not in status_map:
            print("Invalid attendance status.")
            return

        status = status_map[choice]

        # Insert or update attendance
        cursor.execute("""
            INSERT INTO attendance
            (
                employee_id,
                attendance_date,
                status
            )
            VALUES (?, ?, ?)

            ON CONFLICT(employee_id, attendance_date)
            DO UPDATE SET
                status = excluded.status
        """, (
            employee_id,
            attendance_date,
            status
        ))

        connection.commit()

        print("\nAttendance saved successfully.")
        print(f"Employee : {employee[1]}")
        print(f"Date     : {attendance_date}")
        print(f"Status   : {status}")

    except sqlite3.Error as error:
        print(f"\nDatabase error: {error}")

    finally:
        connection.close()


def view_attendance():
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                a.attendance_id,
                e.employee_id,
                e.name,
                d.department_name,
                a.attendance_date,
                a.status
            FROM attendance a

            JOIN employees e
                ON a.employee_id = e.employee_id

            JOIN departments d
                ON e.department_id = d.department_id

            ORDER BY
                a.attendance_date DESC,
                e.employee_id
        """)

        records = cursor.fetchall()

        print("\n" + "=" * 95)
        print("                         ALL ATTENDANCE")
        print("=" * 95)

        if not records:
            print("No attendance records found.")
            return

        print(
            f"{'ID':<6}"
            f"{'Emp ID':<9}"
            f"{'Name':<25}"
            f"{'Department':<20}"
            f"{'Date':<15}"
            f"{'Status':<12}"
        )

        print("-" * 87)

        for record in records:

            print(
                f"{record[0]:<6}"
                f"{record[1]:<9}"
                f"{record[2][:23]:<25}"
                f"{record[3][:18]:<20}"
                f"{record[4]:<15}"
                f"{record[5]:<12}"
            )

        print("-" * 87)

    except sqlite3.Error as error:
        print(f"Database error: {error}")

    finally:
        connection.close()


def view_employee_attendance(employee_id=None):

    if employee_id is None:

        try:
            employee_id = int(
                input("Enter Employee ID: ").strip()
            )
        except ValueError:
            print("Employee ID must be a number.")
            return

    connection = connect_db()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT
                employee_id,
                name
            FROM employees
            WHERE employee_id = ?
        """, (employee_id,))

        employee = cursor.fetchone()

        if not employee:
            print("\nEmployee not found.")
            return

        cursor.execute("""
            SELECT
                attendance_date,
                status
            FROM attendance
            WHERE employee_id = ?
            ORDER BY attendance_date DESC
        """, (employee_id,))

        records = cursor.fetchall()

        print("\n" + "=" * 65)
        print("                 EMPLOYEE ATTENDANCE")
        print("=" * 65)

        print(f"Employee ID : {employee[0]}")
        print(f"Employee    : {employee[1]}")
        print("-" * 50)

        if not records:
            print("No attendance records found.")
            return

        print(
            f"{'Date':<25}"
            f"{'Status':<15}"
        )

        print("-" * 40)

        for record in records:

            print(
                f"{record[0]:<25}"
                f"{record[1]:<15}"
            )

        print("-" * 40)

    except sqlite3.Error as error:
        print(f"Database error: {error}")

    finally:
        connection.close()


def attendance_summary():

    connection = connect_db()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT
                e.employee_id,
                e.name,

                SUM(
                    CASE
                        WHEN a.status = 'Present'
                        THEN 1
                        ELSE 0
                    END
                ) AS present_days,

                SUM(
                    CASE
                        WHEN a.status = 'Absent'
                        THEN 1
                        ELSE 0
                    END
                ) AS absent_days,

                SUM(
                    CASE
                        WHEN a.status = 'Leave'
                        THEN 1
                        ELSE 0
                    END
                ) AS leave_days,

                COUNT(a.attendance_id) AS total_days

            FROM employees e

            LEFT JOIN attendance a
                ON e.employee_id = a.employee_id

            GROUP BY
                e.employee_id,
                e.name

            ORDER BY e.employee_id
        """)

        records = cursor.fetchall()

        print("\n" + "=" * 100)
        print("                       ATTENDANCE SUMMARY")
        print("=" * 100)

        if not records:
            print("No employees found.")
            return

        print(
            f"{'Emp ID':<10}"
            f"{'Name':<25}"
            f"{'Present':<12}"
            f"{'Absent':<12}"
            f"{'Leave':<12}"
            f"{'Total':<10}"
            f"{'Percentage':<12}"
        )

        print("-" * 93)

        for record in records:

            employee_id = record[0]
            name = record[1]

            present = record[2] or 0
            absent = record[3] or 0
            leave = record[4] or 0
            total = record[5] or 0

            if total > 0:
                percentage = (
                    present / total
                ) * 100
            else:
                percentage = 0

            print(
                f"{employee_id:<10}"
                f"{name[:23]:<25}"
                f"{present:<12}"
                f"{absent:<12}"
                f"{leave:<12}"
                f"{total:<10}"
                f"{percentage:.2f}%"
            )

        print("-" * 93)

    except sqlite3.Error as error:
        print(f"Database error: {error}")

    finally:
        connection.close()


def attendance_menu():

    while True:

        print("\n" + "=" * 55)
        print("              ATTENDANCE MANAGEMENT")
        print("=" * 55)

        print("1. Mark / Update Attendance")
        print("2. View All Attendance")
        print("3. View Employee Attendance")
        print("4. Attendance Summary")
        print("5. Back")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        if choice == "1":

            mark_attendance()

        elif choice == "2":

            view_attendance()

        elif choice == "3":

            view_employee_attendance()

        elif choice == "4":

            attendance_summary()

        elif choice == "5":

            break

        else:

            print("Invalid choice. Please try again.")


def department_management_menu():

    while True:

        print("\n" + "=" * 50)
        print("              DEPARTMENT MANAGEMENT")
        print("=" * 50)

        print("1. Add Department")
        print("2. View Departments")
        print("3. Update Department")
        print("4. Delete Department")
        print("5. Back")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        if choice == "1":
            add_department()

        elif choice == "2":
            view_departments()

        elif choice == "3":
            update_department()

        elif choice == "4":
            delete_department()

        elif choice == "5":
            break

        else:
            print("Invalid choice.")


def update_department():
    print("\n" + "=" * 50)
    print("                UPDATE DEPARTMENT")
    print("=" * 50)

    view_departments()

    try:
        department_id = int(
            input("\nEnter Department ID: ").strip()
        )
    except ValueError:
        print("Department ID must be a number.")
        return

    new_name = input(
        "Enter new department name: "
    ).strip()

    if not new_name:
        print("Department name cannot be empty.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE departments
            SET department_name = ?
            WHERE department_id = ?
        """, (
            new_name,
            department_id
        ))

        if cursor.rowcount == 0:
            print("Department not found.")
        else:
            connection.commit()
            print("Department updated successfully.")

    except sqlite3.IntegrityError:
        print("A department with this name already exists.")

    finally:
        connection.close()


def delete_department():
    print("\n" + "=" * 50)
    print("                DELETE DEPARTMENT")
    print("=" * 50)

    view_departments()

    try:
        department_id = int(
            input("\nEnter Department ID: ").strip()
        )
    except ValueError:
        print("Department ID must be a number.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT department_name
            FROM departments
            WHERE department_id = ?
        """, (department_id,))

        department = cursor.fetchone()

        if not department:
            print("Department not found.")
            return

        # Check whether employees belong to this department
        cursor.execute("""
            SELECT COUNT(*)
            FROM employees
            WHERE department_id = ?
        """, (department_id,))

        employee_count = cursor.fetchone()[0]

        if employee_count > 0:
            print(
                f"\nCannot delete this department."
                f"\n{employee_count} employee(s) currently "
                f"belong to this department."
            )
            print(
                "Move those employees to another department "
                "before deleting it."
            )
            return

        confirmation = input(
            f"\nDelete '{department[0]}'? (y/n): "
        ).strip().lower()

        if confirmation != "y":
            print("Deletion cancelled.")
            return

        cursor.execute("""
            DELETE FROM departments
            WHERE department_id = ?
        """, (department_id,))

        connection.commit()

        print("Department deleted successfully.")

    finally:
        connection.close()



def hr_menu(user_id, username):

    while True:

        print("\n" + "=" * 55)
        print("                     HR MENU")
        print("=" * 55)

        print(f"Welcome, {username}!")
        print()

        print("1. Employee Management")
        print("2. Department Management")
        print("3. Attendance Management")
        print("4. Logout")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        if choice == "1":

            employee_management_menu()

        elif choice == "2":

            department_management_menu()

        elif choice == "3":

            attendance_menu()

        elif choice == "4":

            print("\nLogged out successfully.")
            break

        else:

            print("\nInvalid choice. Please try again.")


def view_my_details(employee_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                e.employee_id,
                e.name,
                e.email,
                e.phone,
                d.department_name,
                e.designation,
                e.salary
            FROM employees e
            JOIN departments d
                ON e.department_id = d.department_id
            WHERE e.employee_id = ?
        """, (employee_id,))

        employee = cursor.fetchone()

        print("\n" + "=" * 55)
        print("                    MY DETAILS")
        print("=" * 55)

        if not employee:
            print("Employee record not found.")
            return

        print(f"Employee ID : {employee[0]}")
        print(f"Name        : {employee[1]}")
        print(f"Email       : {employee[2]}")
        print(f"Phone       : {employee[3]}")
        print(f"Department  : {employee[4]}")
        print(f"Designation : {employee[5]}")
        print(f"Salary      : ₹{employee[6]:,.2f}")

        print("=" * 55)

    except sqlite3.Error as error:
        print(f"Database error: {error}")

    finally:
        connection.close()


def view_my_attendance(employee_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                attendance_date,
                status
            FROM attendance
            WHERE employee_id = ?
            ORDER BY attendance_date DESC
        """, (employee_id,))

        records = cursor.fetchall()

        print("\n" + "=" * 60)
        print("                  MY ATTENDANCE")
        print("=" * 60)

        if not records:
            print("No attendance records found.")
            return

        print(f"{'Date':<20}{'Status':<15}")
        print("-" * 35)

        for record in records:
            print(f"{record[0]:<20}{record[1]:<15}")

        print("-" * 35)

        # Calculate attendance statistics
        total_days = len(records)

        present_days = sum(
            1 for record in records
            if record[1] == "Present"
        )

        absent_days = sum(
            1 for record in records
            if record[1] == "Absent"
        )

        leave_days = sum(
            1 for record in records
            if record[1] == "Leave"
        )

        attendance_percentage = (
            present_days / total_days * 100
            if total_days > 0
            else 0
        )

        print(f"Total Records       : {total_days}")
        print(f"Present             : {present_days}")
        print(f"Absent              : {absent_days}")
        print(f"Leave               : {leave_days}")
        print(f"Attendance          : {attendance_percentage:.2f}%")

        print("=" * 60)

    except sqlite3.Error as error:
        print(f"Database error: {error}")

    finally:
        connection.close()


def employee_menu(employee_id, username):

    while True:
        print("\n" + "===============")
        print("EMPLOYEE MENU")
        print("===============")

        print("1. View My Details")
        print("2. View My Attendance")
        print("3. Logout")

        choice = input("Enter your choice: ")

        if choice == "1":
            view_my_details(employee_id)

        elif choice == "2":
            view_my_attendance(employee_id)

        elif choice == "3":
            print("Logged out successfully.")
            break

        else:
            print("Invalid choice.")


def main():

    create_tables()

    while True:

        print("\n" + "===============")
        print("EMPLOYEE MANAGEMENT SYSTEM")
        print("===============")

        print("1. Sign Up")
        print("2. Sign In")
        print("3. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            sign_up()

        elif choice == "2":
            sign_in()

        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()