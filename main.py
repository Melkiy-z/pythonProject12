import sqlite3, xlsxwriter, sys, os
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from PIL import Image
from DB import DB
import pandas as pd
from tkinter.messagebox import showerror, showinfo

author = ["№", "Имена авторов"]
book = ["№", "Название книги", "Год публикации", "Количество страниц","Цена", "Место издания", "Издательство", "Жанр",
        "Автор"]
genre = ["№", "Жанр книги"]
izdatelstvo = ["№", "Наименование издательства"]
mesto_izdaniya = ["№", "Место издания"]
vidacha = ["№", "Дата выдачи"]
vozvrat = ["№", "Дата возврата"]
student = ["№", "ФИО Читателя", "Группа читателя", "Возврат", "Выдача", "Название книги"]
chitatel = ["№", "Имя", "Фамилия", "Отчество"]
postavshik = ["№", "Наименование поставщика"]
spisanie = ["№", "Дата списания", "Причина списания", "№ книги"]

ctk.set_default_color_theme("green")


class WindowMain(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Городская библиотека')
        self.wm_iconbitmap()
        self.iconphoto(True, tk.PhotoImage(file="image\\image\\5606108.png"))
        self.last_headers = None

        # Создание фрейма для отображения таблицы
        self.table_frame = ctk.CTkFrame(self, width=700, height=400)
        self.table_frame.grid(row=0, column=0, padx=5, pady=5)

        # Загрузка фона
        bg = ctk.CTkImage(Image.open("image\\image\\fon 2.jpg"), size=(700, 400))
        lbl = ctk.CTkLabel(self.table_frame, image=bg, text='Таблица не открыта', font=("Calibri", 40))
        lbl.place(relwidth=1, relheight=1)

        # Создание меню
        self.menu_bar = tk.Menu(self, background='#555', foreground='white')

        # Меню "Файл"
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Выход", command=self.quit)
        self.menu_bar.add_cascade(label="Файл", menu=file_menu)

        # Меню "Справочники"
        references_menu = tk.Menu(self.menu_bar, tearoff=0)
        references_menu.add_command(label="Имена Авторов", command=lambda: self.show_table("SELECT * FROM author", author))
        references_menu.add_command(label="Выдача", command=lambda: self.show_table("SELECT * FROM vidacha", vidacha))
        references_menu.add_command(label="Возврат", command=lambda: self.show_table("SELECT * FROM vozvrat", vozvrat))
        references_menu.add_command(label="Жанр книги", command=lambda: self.show_table("SELECT * FROM genre", genre))
        references_menu.add_command(label="Издательство", command=lambda: self.show_table("SELECT * FROM izdatelstvo", izdatelstvo))
        references_menu.add_command(label="Место издательства", command=lambda: self.show_table("SELECT * FROM mesto_izdaniya", mesto_izdaniya))
        self.menu_bar.add_cascade(label="Справочники таблиц", menu=references_menu)



        # Меню "Таблицы"
        tables_menu = tk.Menu(self.menu_bar, tearoff=0)
        tables_menu.add_command(label="Формулятор", command=lambda: self.show_table('''
            SELECT student.id_student, student.name_student, student."group", vozvrat.data_vozvrat, vidacha.data_vidacha, student.name_knigi
            FROM student
            JOIN vozvrat ON student.id_vozvrat = vozvrat.id_vozvrat
            JOIN vidacha ON student.id_vidacha = vidacha.id_vidacha
        ''', student))

        tables_menu.add_command(label="Книги", command=lambda: self.show_table('''
            SELECT book.id_book, book.name, book.year_publishing, book.kolvo_stranic, book.price,
                mesto_izdaniya.mesto_izdaniya, izdatelstvo.name, genre.name_genre, author.name_author
            FROM book
            JOIN mesto_izdaniya ON book.id_mesto_izdaniya = mesto_izdaniya.id_mesto_izdaniya
            JOIN izdatelstvo ON book.id_izdatelstvo = izdatelstvo.id_izdatelstvo
            JOIN genre ON book.ID = genre.ID
            JOIN author ON book.id_uniquel = author.id_uniquel
        ''', book))
        tables_menu.add_command(label="Читатель", command=lambda: self.show_table('''
                                    SELECT * FROM chitatel''', chitatel))
        tables_menu.add_command(label="Поставщик", command=lambda: self.show_table('''
                                    SELECT * FROM postavshik''', postavshik))
        tables_menu.add_command(label="Списание", command=lambda: self.show_table('''
                                    SELECT * FROM spisanie''', spisanie))
        self.menu_bar.add_cascade(label="Таблицы", menu=tables_menu)

        # Меню "Отчёты"
        reports_menu = tk.Menu(self.menu_bar, tearoff=0)
        reports_menu.add_command(label="Создать Отчёт", command=self.to_xlsx)
        self.menu_bar.add_cascade(label="Отчёты", menu=reports_menu)

        # Меню "Сервис"
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="Руководство пользователя", command=lambda: self.open_help())
        help_menu.add_command(label="O программе", command=lambda: self.info_n())
        self.menu_bar.add_cascade(label="Сервис", menu=help_menu)

        # Настройка цветов меню
        file_menu.configure(bg='#555', fg='white')
        references_menu.configure(bg='#555', fg='white')
        tables_menu.configure(bg='#555', fg='white')
        reports_menu.configure(bg='#555', fg='white')
        help_menu.configure(bg='#555', fg='white')

        # Установка меню в главное окно
        self.config(menu=self.menu_bar)

        btn_width = 150
        pad = 5


        # Создание кнопок и виджетов для поиска и редактирования данных
        # передача значения переменным ввиде изображений
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "image\\image icon")
        self.deletes = ctk.CTkImage(Image.open(os.path.join(image_path, "delete.png")),size=(20, 20))
        self.change_add = ctk.CTkImage(Image.open(os.path.join(image_path, "change and add.png")), size=(20, 20))
        self.searchs = ctk.CTkImage(Image.open(os.path.join(image_path, "search.png")), size=(20, 20))
        self.cancellation = ctk.CTkImage(Image.open(os.path.join(image_path, "cancellation.png")), size=(20, 20))
        self.logo_image = ctk.CTkImage(Image.open(os.path.join(image_path, "change_navig.png")) ,size=(26, 26))

        # create navigation frame
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=15)
        self.navigation_frame.grid(row=0, column=1, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        # редактирование
        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="Редактирование", image=self.logo_image, compound="right", font=ctk.CTkFont(size=18, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # создание тем
        self.appearance_mode_label = ctk.CTkLabel(self.navigation_frame, text="Тема", anchor="w", font=ctk.CTkFont(size=13, weight="bold"))
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        #тема у умолчанию
        self.appearance_mode_optionemenu.set("Dark")

        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=0, column=1)
        ctk.CTkButton(btn_frame, text="Добавить", font=ctk.CTkFont(size=15, weight="bold"), image=self.change_add, compound="right", width=btn_width, command=self.add).pack(pady=pad)
        ctk.CTkButton(btn_frame, text="Удалить", font=ctk.CTkFont(size=15, weight="bold"), image=self.deletes, compound="right", width=btn_width, command=self.delete).pack(pady=pad)
        ctk.CTkButton(btn_frame, text="Изменить", font=ctk.CTkFont(size=15, weight="bold"), image=self.change_add, compound="right", width=btn_width, command=self.change).pack(pady=pad)

        search_frame = ctk.CTkFrame(self)
        search_frame.grid(row=1, column=0, pady=pad)
        self.search_entry = ctk.CTkEntry(search_frame, width=300, placeholder_text="Поиск строк")
        self.search_entry.grid(row=0, column=0, padx=pad)
        ctk.CTkButton(search_frame, text="Поиск", image=self.searchs, compound="right", width=50, font=ctk.CTkFont(size=13, weight="bold"), command=self.search).grid(row=0, column=1, padx=pad)
        ctk.CTkButton(search_frame, text="Искать далее", width=50, font=ctk.CTkFont(size=13, weight="bold"), command=self.search_next).grid(row=0, column=2, padx=pad)
        ctk.CTkButton(search_frame, text="Сброс", image=self.cancellation, compound="right", width=50, font=ctk.CTkFont(size=13, weight="bold"), command=self.reset_search).grid(row=0, column=3, padx=pad)

    def open_help(self):
        os.system(r"D:\python\pythonProject1\html\main.html")

    def info_n(self):
        info()
        self.withdraw()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def search_in_table(self, table, search_terms, start_item=None):
        table.selection_remove(table.selection())  # Сброс предыдущего выделения

        items = table.get_children('')
        start_index = items.index(start_item) + 1 if start_item else 0

        for item in items[start_index:]:
            values = table.item(item, 'values')
            for term in search_terms:
                if any(term.lower() in str(value).lower() for value in values):
                    table.selection_add(item)
                    table.focus(item)
                    table.see(item)
                    return item  # Возвращаем найденный элемент

    def reset_search(self):
        if self.last_headers:
            self.table.selection_remove(self.table.selection())
        self.search_entry.delete(0, 'end')

    def search(self):
        if self.last_headers:
            self.current_item = self.search_in_table(self.table, self.search_entry.get().split(','))

    def search_next(self):
        if self.last_headers:
            if self.current_item:
                self.current_item = self.search_in_table(self.table, self.search_entry.get().split(','),
                                                         start_item=self.current_item)

    def to_xlsx(self):
        if self.last_headers == author:
            sql_query = "SELECT * FROM author"
            table_name = "author"
        elif self.last_headers == mesto_izdaniya:
            sql_query = "SELECT * FROM mesto_izdaniya"
            table_name = "mesto_izdaniya"
        elif self.last_headers == genre:
            sql_query = "SELECT * FROM genre"
            table_name = "genre"
        elif self.last_headers == izdatelstvo:
            sql_query = "SELECT * FROM izdatelstvo"
            table_name = "izdatelstvo"
        elif self.last_headers == vidacha:
            sql_query = "SELECT * FROM vidacha"
            table_name = "vidacha"
        elif self.last_headers == vozvrat:
            sql_query = "SELECT * FROM vozvrat"
            table_name = "vozvrat"
        elif self.last_headers == book:
            sql_query = '''
                SELECT book.id_book, book.name, book.year_publishing, book.kolvo_stranic, book.price,
                    mesto_izdaniya.mesto_izdaniya, izdatelstvo.name, genre.name_genre, author.name_author
                FROM book
                JOIN mesto_izdaniya ON book.id_mesto_izdaniya = mesto_izdaniya.id_mesto_izdaniya
                JOIN izdatelstvo ON book.id_izdatelstvo = izdatelstvo.id_izdatelstvo
                JOIN genre ON book.ID = genre.ID
                JOIN author ON book.id_uniquel = author.id_uniquel
            '''
            table_name = "book"
        elif self.last_headers == student:
            sql_query = '''
                SELECT student.id_student, student.name_student, student."group", vozvrat.data_vozvrat, vidacha.data_vidacha 
                FROM student
                JOIN vozvrat ON student.id_vozvrat = vozvrat.id_vozvrat
                JOIN vidacha ON student.id_vidacha = vidacha.id_vidacha
            '''
            table_name = "student"
        else:
            return

        dir = sys.path[0] + "\\export"
        os.makedirs(dir, exist_ok=True)
        path = dir + f"\\{table_name}.xlsx"

        # Подключение к базе данных SQLite
        conn = sqlite3.connect("book_bd.db")
        cursor = conn.cursor()
        # Получите данные из базы данных
        cursor.execute(sql_query)
        data = cursor.fetchall()
        # Создайте DataFrame из данных
        df = pd.DataFrame(data, columns=self.last_headers)
        # Создайте объект writer для записи данных в Excel
        writer = pd.ExcelWriter(path, engine='xlsxwriter')
        # Запишите DataFrame в файл Excel
        df.to_excel(writer, 'Лист 1', index=False)
        # Сохраните результат
        writer.close()

        showinfo(title="Успешно", message=f"Данные экспортированы в {path}")

    def add(self):
        if self.last_headers == author:
            WindowDirectory("add", ("Автор", "author", "id_uniquel", "name_author"))
        elif self.last_headers == genre:
            WindowDirectory("add", ("Жанр", "genre", "ID", "name_genre"))
        elif self.last_headers == izdatelstvo:
            WindowDirectory("add", ("Издательство", "izdatelstvo", "id_izdatelstvo", "name"))
        elif self.last_headers == mesto_izdaniya:
            WindowDirectory("add", ("Место издания", "mesto_izdaniya", "id_mesto_izdaniya", "mesto_izdaniya"))
        elif self.last_headers == vidacha:
            WindowDirectory("add", ("Выдача", "vidacha", "id_vidacha", "data_vidacha"))
        elif self.last_headers == vozvrat:
            WindowDirectory("add", ("Возврат", "vozvrat", "id_vozvrat", "data_vozvrat"))
        elif self.last_headers == book:
            WindowBook("add")
        elif self.last_headers == student:
            WindowStudent("add")
        else:
            return

        self.withdraw()

    def delete(self):
        if self.last_headers:
            select_item = self.table.selection()
            if select_item:
                item_data = self.table.item(select_item[0])["values"]
            else:
                showerror(title="Ошибка", message="He выбранна запись")
                return
        else:
            return

        if self.last_headers == author:
            WindowDirectory("delete", ("Автор", "author", "id_uniquel", "name_author"), item_data)
        elif self.last_headers == genre:
            WindowDirectory("delete", ("Жанр", "genre", "ID", "name_genre"), item_data)
        elif self.last_headers == izdatelstvo:
            WindowDirectory("delete", ("Издательство", "izdatelstvo", "id_izdatelstvo", "name"), item_data)
        elif self.last_headers == mesto_izdaniya:
            WindowDirectory("delete", ("Место издания", "mesto_izdaniya", "id_mesto_izdaniya", "mesto_izdaniya"), item_data)
        elif self.last_headers == vidacha:
            WindowDirectory("delete", ("Выдача", "vidacha", "id_vidacha", "data_vidacha"), item_data)
        elif self.last_headers == vozvrat:
            WindowDirectory("delete", ("Возврат", "vozvrat", "id_vozvrat", "data_vozvrat"), item_data)
        elif self.last_headers == book:
            WindowBook("delete", item_data)
        elif self.last_headers == student:
            WindowStudent("delete", item_data)
        else:
            return

        self.withdraw()

    def change(self):
        if self.last_headers:
            select_item = self.table.selection()
            if select_item:
                item_data = self.table.item(select_item[0])["values"]
            else:
                showerror(title="Ошибка", message="He выбранна запись")
                return
        else:
            return

        if self.last_headers == author:
            WindowDirectory("change", ("Автор", "author", "id_uniquel", "name_author"), item_data)
        elif self.last_headers == genre:
            WindowDirectory("change", ("Жанр", "genre", "ID", "name_genre"), item_data)
        elif self.last_headers == izdatelstvo:
            WindowDirectory("change", ("Издательство", "izdatelstvo", "id_izdatelstvo", "name"), item_data)
        elif self.last_headers == mesto_izdaniya:
            WindowDirectory("change", ("Место издания", "mesto_izdaniya", "id_mesto_izdaniya", "mesto_izdaniya"), item_data)
        elif self.last_headers == vidacha:
            WindowDirectory("change", ("Выдача", "vidacha", "id_vidacha", "data_vidacha"), item_data)
        elif self.last_headers == vozvrat:
            WindowDirectory("change", ("Возврат", "vozvrat", "id_vozvrat", "data_vozvrat"), item_data)
        elif self.last_headers == book:
            WindowBook("change", item_data)
        elif self.last_headers == student:
            WindowStudent("change", item_data)
        else:
            return

        self.withdraw()

    def show_table(self, sql_query, headers=None):
        # Очистка фрейма перед отображением новых данных
        for widget in self.table_frame.winfo_children(): widget.destroy()

        # Подключение к базе данных SQLite
        conn = sqlite3.connect("book_bd.db")
        cursor = conn.cursor()

        # Выполнение SQL-запроса
        cursor.execute(sql_query)
        self.last_sql_query = sql_query

        # Получение заголовков таблицы и данных
        if headers == None:  # если заголовки не были переданы используем те что в БД
            table_headers = [description[0] for description in cursor.description]
        else:  # иначе используем те что передали
            table_headers = headers
            self.last_headers = headers
        table_data = cursor.fetchall()

        # Закрытие соединения с базой данных
        conn.close()

        canvas = ctk.CTkCanvas(self.table_frame, width=865, height=480)
        canvas.pack(fill="both", expand=True)

        x_scrollbar = ttk.Scrollbar(self.table_frame, orient="horizontal", command=canvas.xview)
        x_scrollbar.pack(side="bottom", fill="x")

        canvas.configure(xscrollcommand=x_scrollbar.set)

        self.table = ttk.Treeview(self.table_frame, columns=table_headers, show="headings", height=23)
        for header in table_headers:
            self.table.heading(header, text=header)
            self.table.column(header,
                              width=len(header) * 10 + 15)  # установка ширины столбца исходя длины его заголовка
        for row in table_data: self.table.insert("", "end", values=row)

        canvas.create_window((0, 0), window=self.table, anchor="nw")

        self.table.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def update_table(self):
        self.show_table(self.last_sql_query, self.last_headers)


class WindowDirectory(ctk.CTkToplevel):
    def __init__(self, operation: str, table_info: tuple[str, str, str, str], data=None):

        super().__init__()


        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())
        if data:
            self.id = data[0]  # id в таблице спрвочнике
            self.value = data[1]  # значение по id

        self.table_name_user = table_info[0]
        self.table_name_db = table_info[1]
        self.field_id = table_info[2]
        self.field_name = table_info[3]

        if operation == "add":
            self.title(f"Добавление записи в таблицу '{self.table_name_user}'")
            ctk.CTkLabel(self, text="Наименование: ").grid(row=0, column=0, pady=5, padx=5)
            self.add_enty = ctk.CTkEntry(self, width=200)
            self.add_enty.grid(row=0, column=1, pady=5, padx=5)
            ctk.CTkButton(self, text="Отмена", font=ctk.CTkFont(size=15, weight="bold"), width=200, command=self.quit_win).grid(row=1, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Добавить", font=ctk.CTkFont(size=15, weight="bold"), width=200, command=self.add).grid(row=1, column=1, pady=5, padx=5)

        elif operation == "delete":
            self.title(f"Удаление записи из таблицы '{self.table_name_user}'")
            ctk.CTkLabel(self, text=f"Вы действиельно хотите удалить запись\nИз таблицы '{self.table_name_user}'?",
                         width=125).grid(row=0, column=0, columnspan=2, pady=5, padx=5)
            ctk.CTkLabel(self, text=f"Значение: {self.value}", width=125).grid(row=1, column=0,
                                                                               columnspan=2, pady=5, padx=5)
            ctk.CTkButton(self, text="Да", command=self.delete, width=125, font=ctk.CTkFont(size=15, weight="bold")).grid(row=2, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Нет", command=self.quit_win, width=125,  font=ctk.CTkFont(size=15, weight="bold")).grid(row=2, column=1, pady=5, padx=5)

        elif operation == "change":
            self.title(f"Изменение записи в таблице '{self.table_name_user}'")
            ctk.CTkLabel(self, text="текущее значение").grid(row=0, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text="Новое значение").grid(row=0, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text=f"{self.value}").grid(row=1, column=0, pady=5, padx=5)
            self.change_entry = ctk.CTkEntry(self, width=200)
            self.change_entry.grid(row=1, column=1, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=200, command=self.quit_win, font=ctk.CTkFont(size=15, weight="bold")).grid(row=2, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Сохранить", width=200, command=self.change, font=ctk.CTkFont(size=15, weight="bold")).grid(row=2, column=1, pady=5, padx=5)

    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()

    def add(self):
        new_value = self.add_enty.get()
        if new_value:
            try:
                conn = sqlite3.connect("book_bd.db")
                cursor = conn.cursor()
                cursor.execute(f"INSERT INTO {self.table_name_db} ({self.field_name}) VALUES (?)", (new_value,))
                conn.commit()
                conn.close()
                self.quit_win()
            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")

    def delete(self):
        try:
            conn = sqlite3.connect("book_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self.table_name_db} WHERE {self.field_id} = ?", (self.id,))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        new_value = self.change_entry.get()
        if new_value:
            try:
                conn = sqlite3.connect("book_bd.db")
                cursor = conn.cursor()
                cursor.execute(f"UPDATE {self.table_name_db} SET {self.field_name} = ? WHERE {self.field_id} = ?",
                               (new_value, self.id))
                conn.commit()
                conn.close()
                self.quit_win()
            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")


class WindowBook(ctk.CTkToplevel):
    def __init__(self, operation, select_row=None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())

        conn = sqlite3.connect("book_bd.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM mesto_izdaniya")
        mesto_izdaniya = []
        for item in cursor.fetchall():
            mesto_izdaniya.append(f"{item[0]}. {item[1]}")

        cursor.execute("SELECT * FROM izdatelstvo")
        izdatelstvo = []
        for item in cursor.fetchall():
            izdatelstvo.append(f"{item[0]}. {item[1]}")

        cursor.execute("SELECT * FROM genre")
        genre = []
        for item in cursor.fetchall():
            genre.append(f"{item[0]}. {item[1]}")

        cursor.execute("SELECT * FROM author")
        author = []
        for item in cursor.fetchall():
            author.append(f"{item[0]}. {item[1]}")

        conn.close

        if select_row:
            self.select_row = select_row

        if operation == "add":
            self.title("Добавление в таблицу 'Книги'")

            ctk.CTkLabel(self, text="Название книги").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.name_entry = ctk.CTkEntry(self, width=300)
            self.name_entry.grid(row=0, column=1)

            ctk.CTkLabel(self, text="Дата публикации").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.year_publishing_entry = ctk.CTkEntry(self, width=300)
            self.year_publishing_entry.grid(row=1, column=1)

            ctk.CTkLabel(self, text="Кол-во страниц").grid(row=2, column=0, padx=5, pady=5, sticky="w")
            self.kolvo_stranic_entry = ctk.CTkEntry(self, width=300)
            self.kolvo_stranic_entry.grid(row=2, column=1)

            ctk.CTkLabel(self, text="Цена").grid(row=3, column=0, padx=5, pady=5, sticky="w")
            self.price_entry = ctk.CTkEntry(self, width=300)
            self.price_entry.grid(row=3, column=1)

            '''=================================================================================='''
            ctk.CTkLabel(self, text="Место издания").grid(row=6, column=0, padx=5, pady=5, sticky="w")
            self.mesto_izdaniya_cb = ctk.CTkComboBox(self, width=300, values=mesto_izdaniya)
            self.mesto_izdaniya_cb.grid(row=6, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Издательство").grid(row=7, column=0, padx=5, pady=5, sticky="w")
            self.izdatelstvo_cb = ctk.CTkComboBox(self, width=300, values=izdatelstvo)
            self.izdatelstvo_cb.grid(row=7, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Жанр").grid(row=8, column=0, padx=5, pady=5, sticky="w")
            self.genre_cb = ctk.CTkComboBox(self, width=300, values=genre)
            self.genre_cb.grid(row=8, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Автор").grid(row=9, column=0, padx=5, pady=5, sticky="w")
            self.author_cb = ctk.CTkComboBox(self, width=300, values=author)
            self.author_cb.grid(row=9, column=1, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", command=self.quit_win, width=150, font=ctk.CTkFont(size=15, weight="bold")).grid(row=12, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkButton(self, text="Добавить", command=self.add, width=150, font=ctk.CTkFont(size=15, weight="bold")).grid(row=12, column=1, padx=5, pady=5, sticky="e")

        elif operation == "delete":
            self.title("Удаление из таблицы 'Книги'")

            ctk.CTkLabel(self, text="Вы действитель хотите удалить запись\nИз таблицы книги?"
                         ).grid(row=0, column=0, padx=5, pady=5, columnspan=2)
            ctk.CTkLabel(self, text=f"{self.select_row[0]}. {self.select_row[1]}"
                         ).grid(row=1, column=0, padx=5, pady=5, columnspan=2)

            ctk.CTkButton(self, text="Нет", width=100, command=self.quit_win, font=ctk.CTkFont(size=15, weight="bold")).grid(row=2, column=0, pady=5, padx=5, sticky="w")
            ctk.CTkButton(self, text="Да", width=100, command=self.delete, font=ctk.CTkFont(size=15, weight="bold")).grid(row=2, column=1, pady=5, padx=5, sticky="e")

        elif operation == "change":
            self.title("Изменение в таблице 'Книги'")

            ctk.CTkLabel(self, text="Имя поля").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self, text="Текущее значение").grid(row=0, column=1, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self, text="Новое занчение").grid(row=0, column=2, padx=5, pady=5, sticky="w")

            ctk.CTkLabel(self, text="Название").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self, text=self.select_row[1]).grid(row=1, column=1, padx=5, pady=5, sticky="w")
            self.name_entry = ctk.CTkEntry(self, width=300)
            self.name_entry.grid(row=1, column=2)

            ctk.CTkLabel(self, text="год публикации").grid(row=2, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self, text=self.select_row[2]).grid(row=2, column=1, padx=5, pady=5, sticky="w")
            self.year_publishing_entry = ctk.CTkEntry(self, width=300)
            self.year_publishing_entry.grid(row=2, column=2)

            ctk.CTkLabel(self, text="Кол-во страниц").grid(row=3, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self, text=self.select_row[3]).grid(row=3, column=1, padx=5, pady=5, sticky="w")
            self.kolvo_stranic_entry = ctk.CTkEntry(self, width=300)
            self.kolvo_stranic_entry.grid(row=3, column=2)

            ctk.CTkLabel(self, text="Цена").grid(row=4, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self, text=self.select_row[4]).grid(row=4, column=1, padx=5, pady=5, sticky="w")
            self.price_entry = ctk.CTkEntry(self, width=300)
            self.price_entry.grid(row=4, column=2)

            '''=================================================================================='''
            ctk.CTkLabel(self, text="Место издательства").grid(row=7, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self, text=self.select_row[5]).grid(row=7, column=1, padx=5, pady=5, sticky="w")
            self.mesto_izdaniya_cb = ctk.CTkComboBox(self, width=300, values=mesto_izdaniya)
            self.mesto_izdaniya_cb.grid(row=7, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Издательство").grid(row=8, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self, text=self.select_row[6]).grid(row=8, column=1, padx=5, pady=5, sticky="w")
            self.izdatelstvo_cb = ctk.CTkComboBox(self, width=300, values=izdatelstvo)
            self.izdatelstvo_cb.grid(row=8, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Жанр").grid(row=9, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self, text=self.select_row[7]).grid(row=9, column=1, padx=5, pady=5, sticky="w")
            self.genre_cb = ctk.CTkComboBox(self, width=300, values=genre)
            self.genre_cb.grid(row=9, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Автор").grid(row=10, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self, text=self.select_row[8]).grid(row=10, column=1, padx=5, pady=5, sticky="w")
            self.author_cb = ctk.CTkComboBox(self, width=300, values=author)
            self.author_cb.grid(row=10, column=2, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", command=self.quit_win, width=150, font=ctk.CTkFont(size=15, weight="bold")).grid(row=13, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkButton(self, text="Сохранить", command=self.change, width=150, font=ctk.CTkFont(size=15, weight="bold")).grid(row=13, column=2, padx=5, pady=5, sticky="e")

    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()

    def add(self):
        new_name = self.name_entry.get()
        new_year_publishing = self.year_publishing_entry.get()
        new_kolvo_stranic = self.kolvo_stranic_entry.get()
        new_price = self.price_entry.get()
        id_mesto_izdaniya = self.mesto_izdaniya_cb.get().split(".")[0]
        id_izdatelstvo = self.izdatelstvo_cb.get().split(".")[0]
        id_ID = self.genre_cb.get().split(".")[0]
        id_uniquel = self.author_cb.get().split(".")[0]

        if "" not in (new_name, new_year_publishing, new_kolvo_stranic, new_price):
            try:
                conn = sqlite3.connect("book_bd.db")
                cursor = conn.cursor()
                cursor.execute(
                    f"""INSERT INTO book (name, year_publishing, kolvo_stranic, price,
                    id_mesto_izdaniya, id_izdatelstvo, ID, id_uniquel) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (new_name, new_year_publishing, new_kolvo_stranic, new_price,
                     id_mesto_izdaniya, id_izdatelstvo, id_ID, id_uniquel))
                conn.commit()
                conn.close()
                self.quit_win()
            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")

    def delete(self):
        try:
            conn = sqlite3.connect("book_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM book WHERE id_book = ?", (self.select_row[0],))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        new_name = self.name_entry.get() or self.select_row[1]
        new_year_publishing = self.year_publishing_entry.get() or self.select_row[2]
        new_kolvo_stranic = self.kolvo_stranic_entry.get() or self.select_row[3]
        new_price = self.price_entry.get() or self.select_row[4]
        id_mesto_izdaniya = self.mesto_izdaniya_cb.get().split(".")[0]
        id_izdatelstvo = self.izdatelstvo_cb.get().split(".")[0]
        id_ID = self.genre_cb.get().split(".")[0]
        id_uniquel = self.author_cb.get().split(".")[0]

        try:
            conn = sqlite3.connect("book_bd.db")
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE book SET (name, year_publishing, kolvo_stranic, price,
                id_mesto_izdaniya, id_izdatelstvo, ID, id_uniquel) = (?, ?, ?, ?, ?, ?, ?, ?) 
                WHERE id_book = {self.select_row[0]}
            ''', (new_name, new_year_publishing, new_kolvo_stranic, new_price,
                  id_mesto_izdaniya, id_izdatelstvo, id_ID, id_uniquel))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))


class WindowStudent(ctk.CTkToplevel):
    def __init__(self, operation, select_row=None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())

        conn = sqlite3.connect("book_bd.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM vozvrat")
        vozvrat = []
        for item in cursor.fetchall():
            vozvrat.append(f"{item[0]}. {item[1]}")

        cursor.execute("SELECT * FROM vidacha")
        vidacha = []
        for item in cursor.fetchall():
            vidacha.append(f"{item[0]}. {item[1]}")

        conn.close

        if select_row:
            self.select_id_student = select_row[0]
            self.select_name_student = select_row[1]
            self.select_group = select_row[2]
            self.select_id_vozvrat = select_row[3]
            self.select_id_vidacha = select_row[4]

        if operation == "add":
            self.title("Добаление")
            ctk.CTkLabel(self, text="Добаление в таблицу 'Стеденты'").grid(row=0, column=0, pady=5, padx=5,
                                                                           columnspan=2)
            ctk.CTkLabel(self, text="ФИО студента").grid(row=1, column=0, pady=5, padx=5)
            self.name_student = ctk.CTkEntry(self, width=300)
            self.name_student.grid(row=1, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Группа студента").grid(row=2, column=0, pady=5, padx=5)
            self.group = ctk.CTkEntry(self, width=300)
            self.group.grid(row=2, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Выдача").grid(row=3, column=0, pady=5, padx=5)
            self.vidacha_s = ctk.CTkComboBox(self, width=300, values=vidacha)
            self.vidacha_s.grid(row=3, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Возврат").grid(row=4, column=0, pady=5, padx=5)
            self.vozvrat_s = ctk.CTkComboBox(self, width=300, values=vozvrat)
            self.vozvrat_s.grid(row=4, column=1, pady=5, padx=5)


            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win, font=ctk.CTkFont(size=15, weight="bold")).grid(row=5, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Добавить", width=100, command=self.add, font=ctk.CTkFont(size=15, weight="bold")).grid(row=5, column=1, pady=5, padx=5, sticky="e")

        elif operation == "delete":
            self.title("Удаление")
            ctk.CTkLabel(self, text="Вы действиельно хотите\n удалить запись из таблицы 'Родители'?"
                         ).grid(row=0, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkLabel(self, text=f"{self.select_id_student}. {self.select_name_student}"
                         ).grid(row=1, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkButton(self, text="Нет", width=100, command=self.quit_win, font=ctk.CTkFont(size=15, weight="bold")).grid(row=2, column=0, pady=5, padx=5, sticky="w")
            ctk.CTkButton(self, text="Да", width=100, command=self.delete, font=ctk.CTkFont(size=15, weight="bold")).grid(row=2, column=1, pady=5, padx=5, sticky="e")

        elif operation == "change":
            self.title("Изменение в таблице 'Студенты'")
            ctk.CTkLabel(self, text="Назввание поля").grid(row=0, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text="Текущее значение").grid(row=0, column=1, pady=5, padx=5)
            ctk.CTkLabel(self, text="Новое занчение").grid(row=0, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="ФИО студента").grid(row=1, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_name_student).grid(row=1, column=1, pady=5, padx=5)
            self.name_student = ctk.CTkEntry(self, width=300)
            self.name_student.grid(row=1, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Группа студента").grid(row=2, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_group).grid(row=2, column=1, pady=5, padx=5)
            self.group = ctk.CTkEntry(self, width=300)
            self.group.grid(row=2, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Выдача").grid(row=3, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_id_vidacha).grid(row=3, column=1, pady=5, padx=5)
            self.vidacha_s = ctk.CTkComboBox(self, width=300, values=vidacha)
            self.vidacha_s.grid(row=3, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Возврат").grid(row=4, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_id_vozvrat).grid(row=4, column=1, pady=5, padx=5)
            self.vozvrat_s = ctk.CTkComboBox(self, width=300, values=vozvrat)
            self.vozvrat_s.grid(row=4, column=2, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win, font=ctk.CTkFont(size=15, weight="bold")).grid(row=5, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Сохранить", width=100, command=self.change, font=ctk.CTkFont(size=15, weight="bold")).grid(row=5, column=2, pady=5, padx=5,
                                                                                       sticky="e")

    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()

    def add(self):
        new_FIO_s = self.name_student.get()
        new_group_nomber = self.group.get()
        id_vidacha = self.vidacha_s.get().split(".")[0]
        id_vozvrat = self.vozvrat_s.get().split(".")[0]

        if new_FIO_s != "" and new_group_nomber != "":
            try:
                conn = sqlite3.connect("book_bd.db")
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO student (name_student, \"group\", id_vidacha, id_vozvrat) VALUES (?, ?, ?, ?)",
                    (new_FIO_s, new_group_nomber, id_vidacha, id_vozvrat))
                conn.commit()
                conn.close()
                self.quit_win()
            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")

    def delete(self):
        try:
            conn = sqlite3.connect("book_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM student WHERE id_student = ?", (self.select_id_student,))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        new_FIO_s = self.name_student.get() or self.select_name_student
        new_group_nomber = self.group.get() or self.select_group
        id_vidacha = self.vidacha_s.get().split(".")[0]
        id_vozvrat = self.vozvrat_s.get().split(".")[0]

        try:
            conn = sqlite3.connect("book_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"""
                        UPDATE student SET (name_student, "group", id_vidacha, id_vozvrat) = (?, ?, ?, ?) WHERE id_student = {self.select_id_student}
                    """, (new_FIO_s, new_group_nomber, id_vidacha, id_vozvrat))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

class info (ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())
        self.title('О программе')

        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "image\\image")
        self.logo_image = ctk.CTkImage(Image.open(os.path.join(image_path, "5606108.png")), size=(26, 26))

        self.image_frame = ctk.CTkFrame(self, width=250, height=500)
        self.image_frame.grid(row=0, column=0, padx=5, pady=5)

        self.textbox = ctk.CTkFrame(self, width=600)
        self.textbox.grid(row=0, column=1, padx=(20), pady=(5), sticky="nsew")
        self.navigation_frame_label = ctk.CTkLabel(self.textbox, text="О программе", image=self.logo_image, compound="right", font=ctk.CTkFont(size=18, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.info_frame = ctk.CTkLabel(self.textbox, text='Программное средтсво "Городская библиотека"\n'
                                                          ' \nВерсия: 0.2.5 \n'
                                                          ' \nРазработал: Тихонов Данила Сергеевич\n'
                                                          ' \nГод выпуска: 2023\n'
                                                          ' \nПрограммное средство "Городская библиотека" разработанно с целью\n'
                                                          ' автоматизации процесса введение отчетности в городской библиотеке', font=ctk.CTkFont(size=14, weight="bold"))
        self.info_frame.grid(row=1, column=0, padx=20, pady=20)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=3, column=1, sticky="e", pady=5, padx=20)

        ctk.CTkButton(btn_frame, text="ОК", width=100, command=self.quit_win, compound="right",
                      font=ctk.CTkFont(size=15)).grid(row=3, column=0, sticky="w")
        # Загрузка фона
        bg = ctk.CTkImage(Image.open("image\\image\\info.jpg"), size=(250, 500))
        lbl = ctk.CTkLabel(self.image_frame, image=bg, text=' ', font=("Calibri", 40))
        lbl.place(relwidth=1, relheight=1)


    def quit_win(self):
        win.deiconify()
        self.destroy()


if __name__ == "__main__":
    db = DB()
    win = WindowMain()
    win.mainloop()