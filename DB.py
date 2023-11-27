import sqlite3
class DB:
    def __init__(self):
        self.conn = sqlite3.connect('book_bd.db') #установили связь с БД (или создали если ее нет)
        self.c = self.conn.cursor() #создали курсор
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS "book" (
                       "id_book" INTEGER NOT NULL,
                        "name" TEXT NOT NULL,
                        "year_publishing" INTEGER NOT NULL,
                        "kolvo_stranic" INTEGER NOT NULL,
                        "price" REAL NOT NULL,
                        "id_mesto_izdaniya" INTEGER NOT NULL,
                        "id_izdatelstvo" INTEGER NOT NULL,
                        "ID" INTEGER NOT NULL,
                        "id_uniquel" INTEGER NOT NULL,
                        PRIMARY KEY("id_book" AUTOINCREMENT)
                        )''')
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS "mesto_izdaniya" (
                        "id_mesto_izdaniya" INTEGER NOT NULL,
                        "mesto_izdaniya" TEXT NOT NULL,
                        PRIMARY KEY("id_mesto_izdaniya" AUTOINCREMENT)
                        )''')
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS "izdatelstvo" (
                        "id_izdatelstvo" INTEGER NOT NULL,
                        "name" TEXT NOT NULL,
                        PRIMARY KEY("id_izdatelstvo" AUTOINCREMENT)
                        )''')
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS "genre" (
                        "ID" INTEGER NOT NULL,
                        "name_genre" TEXT NOT NULL,
                        PRIMARY KEY("ID" AUTOINCREMENT)
                        )''')
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS "author" (
                        "id_uniquel" INTEGER NOT NULL,
                        "name_author" TEXT NOT NULL,
                        PRIMARY KEY("id_uniquel" AUTOINCREMENT)
                        )''')
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS "student" (
                        "id_student" INTEGER NOT NULL,
                        "name_student" TEXT NOT NULL,
                        "group" TEXT NOT NULL,
                        "id_vozvrat" INTEGER NOT NULL,
                        "id_vidacha" INTEGER NOT NULL,
                        PRIMARY KEY("id_student" AUTOINCREMENT)
                        )''')
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS "vozvrat" (
                        "id_vozvrat" INTEGER NOT NULL,
                        "data_vozvrat" TEXT NOT NULL,
                        PRIMARY KEY("id_vozvrat" AUTOINCREMENT)
                        )''')
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS "vidacha" (
                        "id_vidacha" INTEGER NOT NULL,
                        "data_vidacha" TEXT NOT NULL,
                        PRIMARY KEY("id_vidacha" AUTOINCREMENT)
                        )''')

        self.conn.commit()
db = DB()
