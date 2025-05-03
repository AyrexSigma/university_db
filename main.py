import sqlite3
import sys

class StudentDB:
    def __init__(self, shlah_do_basi="university.db"):
        self.connection = None
        self.cursor = None
        self.connect_base(shlah_do_basi)
        self.create_tables()

    def connect_base(self, file):
        try:
            self.connection = sqlite3.connect(file)
            self.cursor = self.connection.cursor()
            print(">> db connection")
        except Exception as error:
            print(f"Error connection: {error}")
            sys.exit(1)

    def create_tables(self):
        student_query = """
        CREATE TABLE IF NOT EXISTS studenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER CHECK (age >= 16 AND age <= 80),
            majors TEXT DEFAULT 'NE VKAZANO'
        );"""

        course_query = """
        CREATE TABLE IF NOT EXISTS cursi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            teacher TEXT NOT NULL,
            number_of_seats INTEGER DEFAULT 30
        );"""

        report_request = """
        CREATE TABLE IF NOT EXISTS zapisi (
            id_student INTEGER,
            id_course INTEGER,
            entry_data DATE DEFAULT CURRENT_DATE,
            PRIMARY KEY (id_student, id_course),
            FOREIGN KEY (id_student) REFERENCES students(id),
            FOREIGN KEY (id_course) REFERENCES courses(id)
        );"""

        try:
            self.cursor.execute(student_query)
            self.cursor.execute(course_query)
            self.cursor.execute(report_request)
            self.connection.commit()
        except Exception as error:
            print(f"Error with creating tables: {error}")

    def add_student(self, name, age, major=None):
        settings = (name, age)
        query = "INSERT INTO studenti(name, age)"

        if major:
            query += ", major) VALUES(?, ?, ?"
            settings += (major,)
        else:
            query += ") VALEUS(?, ?)"

        try:
            self.cursor.execute(query, settings)
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as error:
            print(f"Error with adding: {error}")
            return None

    def enroll_in_a_course(self, id_student, id_course):
        self.cursor.execute("SELECT 1 FROM student WHERE id = ?", (id_student,))
        if not self.cursor.fetchone():
            print(">> Error: Student with this ID does not exist")
            return False

        self.cursor.execute("SELECT 1 FROM course WHERE id = ?", (id_course,))
        if not self.cursor.fetchone():
            print(">> Error: course with this ID does not exist")
            return False

        self.cursor.execute("""
            SELECT k.number_of_seats, COUNT(z.id_students)
            FROM courses k
            LEFT JOIN entry з ON k.id = з.id_course
            WHERE k.id = ?
            GROUP BY k.id
        """, (id_course,))
        result = self.cursor.fetchone()
        if result and result[1] >= result[0]:
            print(">> Error: This course dont have free seats")
            return False

        try:
            self.cursor.execute("""
                INSERT INTO zapisi(students, courses)
                VALUES(?, ?)
            """, (id_student, id_course))
            self.connection.commit()
            print(">> Student successfully entries the course")
            return True
        except Exception as error:
            print(f">> Error with entry: {error}")
            return False

    def show_students_courses(self, id_student):
        query = """
        SELECT k.nazva, k.vikladach
        FROM cursi k
        JOIN zapisi z ON k.id = z.id_cursu
        WHERE z.id_studenta = ?
        """
        self.cursor.execute(query, (id_student,))
        return self.cursor.fetchall()

def main_menu():
    print("\n=== University system ===")
    print("1. Add new student")
    print("2. Entry student to course")
    print("3. Check students courses")
    print("4. Exit")
    return input("> Choose action: ")

def main_cycle():
    base = StudentDB()

    while True:
        choice = main_menu()

        if choice == '1':
            name = input("Students name: ")
            age = int(input("Students age: "))
            major = input("Major (enter - skip): ") or None
            base.add_student(name, age, major)
            print("Student added!")

        elif choice == '2':
            try:
                print("\nList of students: ")
                base.cursor.execute("SELECT id, name, age FROM student")
                studenti = base.cursor.fetchall()
                for st in studenti:
                    print(f"ID: {st[0]}, Name: {st[1]}, Age: {st[2]}")

                print("\nAvailable courses:")
                base.cursor.execute("SELECT id, name, teacher FROM course")
                courses = base.cursor.fetchall()
                for course in courses:
                    print(f"ID: {course[0]}, Nazva: {course[1]}, Vikladach: {course[2]}")

                id_studenta = int(input("\nEnter students ID: "))
                id_cursu = int(input("Enter course ID: "))

                if base.enroll_in_a_course(id_studenta, id_cursu):
                    print("Operation successful!")

                else:
                    print("Cannot do entry")

            except ValueError:
                print("Error: incorrect ID format")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '3':
            id_stud = int(input("Students ID"))
            courses = base.show_students_courses(id_stud)
            for course in courses:
                print(f"- {course[0]} (age. {course[1]})")

        elif choice == '4':
            base.connection.close()
            break

if __name__ == "__main__":
    print("Starting system...")
    main_cycle()
    print("Ending work")
    print("https://github.com/AyrexSigma/university_db")