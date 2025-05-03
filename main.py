import sqlite3
import sys

class StudentskaBasa:
    def __init__(self, shlah_do_basi="university.db"):
        self.zednanya = None
        self.cursor = None
        self.pidkluchiti_bazu(shlah_do_basi)
        self.stvoriti_tablici()

    def pidkluchiti_bazu(self, file):
        try:
            self.zednanya = sqlite3.connect(file)
            self.cursor = self.zednanya.cursor()
            print(">> db pidkluchina")
        except Exception as pomilka:
            print(f"Pomilka pidkluchina: {pomilka}")
            sys.exit(1)

    def stvoriti_tablici(self):
        zapit_studenti = """
        CREATE TABLE IF NOT EXISTS studenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            im_ya TEXT NOT NULL,
            vik INTEGER CHECK (vik >= 16 AND vik <= 80),
            specialnist TEXT DEFAULT 'NE VKAZANO'
        );"""

        zapit_cursi = """
        CREATE TABLE IF NOT EXISTS cursi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nazva TEXT UNIQUE NOT NULL,
            vikladach TEXT NOT NULL,
            kilkisty_misc INTEGER DEFAULT 30
        );"""

        zapit_zapisi = """
        CREATE TABLE IF NOT EXISTS zapisi (
            id_studenta INTEGER,
            id_cursa INTEGER,
            data_zapisu DATE DEFAULT CURRENT_DATE,
            PRIMARY KEY (id_studenta, id_cursu),
            FOREIGN KEY (id_studenta) REFERENCES studenti(id),
            FOREIGN KEY (id_cursu) REFERENCES cursi(id)
        );"""

        try:
            self.cursor.execute(zapit_studenti)
            self.cursor.execute(zapit_cursi)
            self.cursor.execute(zapit_zapisi)
            self.zednanya.commit()
        except Exception as pomilka:
            print(f"Pomilka stvorenya tablic: {pomilka}")

    def dodati_studenta(self, im_ya, vik, specialnist=None):
        parametri = (im_ya, vik)
        zapit = "INSERT INTO studenti(im_ya, vik)"

        if specialnist:
            zapit += ", specialnist) VALUES(?, ?, ?"
            parametri += (specialnist,)
        else:
            zapit += ") VALEUS(?, ?)"

        try:
            self.cursor.execute(zapit, parametri)
            self.zednanya.commit()
            return self.cursor.lastrowid
        except Exception as pomilka:
            print(f"Pomilka dodavanya: {pomilka}")
            return None

    def zapisatsya_na_curs(self, id_studenta, id_cursu):
        self.cursor.execute("SELECT 1 FROM studenti WHERE id = ?", (id_studenta,))
        if not self.cursor.fetchone():
            print(">> Pomilka: Studenta z takim ID ne isnue")
            return False

        self.cursor.execute("SELECT 1 FROM cursi WHERE id = ?", (id_cursu,))
        if not self.cursor.fetchone():
            print(">> Pomilka: cursu z takim ID ne isnue")
            return False

        self.cursor.execute("""
            SELECT k.kilkist_misc, COUNT(z.id_studenta)
            FROM cursi k
            LEFT JOIN zapisi з ON к.id = з.id_cursu
            WHERE k.id = ?
            GROUP BY k.id
        """, (id_cursu,))
        rezultat = self.cursor.fetchone()
        if rezultat and rezultat[1] >= rezultat[0]:
            print(">> Pomilka: Na cursi vzhe nemae vilnih misc")
            return False

        try:
            self.cursor.execute("""
                INSERT INTO zapisi(studenta, cursu)
                VALUES(?, ?)
            """, (id_studenta, id_cursu))
            self.zednanya.commit()
            print(">> Studenta uspishno zapisano на curs")
            return True
        except Exception as pomilka:
            print(f">> Pomilka zapisu: {pomilka}")
            return False

    def pokazati_cursi_studenta(self, id_studenta):
        zapit = """
        SELECT k.nazva, k.vikladach
        FROM cursi k
        JOIN zapisi z ON k.id = z.id_cursu
        WHERE z.id_studenta = ?
        """
        self.cursor.execute(zapit, (id_studenta,))
        return self.cursor.fetchall()

def golovne_menu():
    print("\n=== Universitetska sistema ===")
    print("1. Dodati novogo studenta")
    print("2. Zapisati studenta na curs")
    print("3. Pereglanuti cursi studenta")
    print("4. Viyti")
    return input("> Oberit diyu: ")

def osnovny_cicl():
    baza = StudentskaBasa()

    while True:
        vibir = golovne_menu()

        if vibir == '1':
            im_ya = input("Im`ya studenta: ")
            vik = int(input("Vik studenta: "))
            spec = input("Specialnist (enter - propustiti): ") or None
            baza.dodati_studenta(im_ya, vik, spec)
            print("Studenta dodano!")

        elif vibir == '2':
            try:
                print("\nSpisoc studentiv:")
                baza.cursor.execute("SELECT id, im_ya, vik FROM studenti")
                studenti = baza.cursor.fetchall()
                for st in studenti:
                    print(f"ID: {st[0]}, Im`ya: {st[1]}, Вік: {st[2]}")

                print("\nDostupni cursi:")
                baza.cursor.execute("SELECT id, nazva, vikladach FROM cursi")
                cursi = baza.cursor.fetchall()
                for curs in cursi:
                    print(f"ID: {curs[0]}, Nazva: {curs[1]}, Vikladach: {curs[2]}")

                id_studenta = int(input("\nVvedit ID studenta: "))
                id_cursu = int(input("Vvedit ID cursu: "))

                if baza.zapisatsya_na_curs(id_studenta, id_cursu):
                    print("Operacia uspishna!")

                else:
                    print("Не vdalosya vikonati zapis")

            except ValueError:
                print("Pomilka: nekorektniy format ID")
            except Exception as e:
                print(f"Stalasya pomilka: {e}")

        elif vibir == '3':
            id_stud = int(input("ID studenta"))
            cursi = baza.pokazati_cursi_studenta(id_stud)
            for curs in cursi:
                print(f"- {curs[0]} (vikl. {curs[1]})")

        elif vibir == '4':
            baza.zednanya.close()
            break

if __name__ == "__main__":
    print("Zapusk sistemi...")
    osnovny_cicl()
    print("Robotu zaversheno")
    print("https://github.com/AyrexSigma/university_db")