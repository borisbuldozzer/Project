import sqlite3
from tkinter import *
from tkinter import ttk

def connect_db():
    """ Создание подключения к базе данных """
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    return conn, cursor

def create_table(cursor):
    """ Создание таблицы """
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY,
                    number TEXT,
                    category TEXT,
                    name TEXT,
                    quantity INTEGER
                )''')

def view_data(category=None):
    """ Просмотр данных в таблице """
    if category and category != "All":
        cursor.execute("SELECT * FROM inventory WHERE category=?", (category,))
    else:
        cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()
    return rows

def delete_data(id):
    """ Удаление записи из таблицы """
    cursor.execute("DELETE FROM inventory WHERE id=?", (id,))
    conn.commit()

def update_data(id, number, category, name, quantity):
    """ Обновление записи в таблице """
    cursor.execute("UPDATE inventory SET number=?, category=?, name=?, quantity=? WHERE id=?",
                   (number, category, name, quantity, id))
    conn.commit()

def add_data(number, category, name, quantity):
    """ Добавление записи в таблицу """
    cursor.execute("INSERT INTO inventory (number, category, name, quantity) VALUES (?, ?, ?, ?)",
                   (number, category, name, quantity))
    conn.commit()

def get_selected_row(event):
    """ Получение выделенной строки из списка """
    try:
        global selected_row
        index = treeview.selection()[0]
        selected_row = treeview.item(index, 'values')
        entry_number.delete(0, END)
        entry_number.insert(END, selected_row[1])
        entry_category.delete(0, END)
        entry_category.insert(END, selected_row[2])
        entry_name.delete(0, END)
        entry_name.insert(END, selected_row[3])
        entry_quantity.delete(0, END)
        entry_quantity.insert(END, selected_row[4])
    except IndexError:
        pass

def delete_command():
    """ Обработчик кнопки удаления """
    try:
        selected_rows = treeview.selection()
        for selected_row in selected_rows:
            values = treeview.item(selected_row)['values']
            selected_row_id = values[0]
            delete_data(selected_row_id)
            treeview.delete(selected_row)
    except IndexError:
        pass

def update_command():
    """ Обработчик кнопки обновления """
    try:
        all_rows = treeview.get_children()
        for row in all_rows:
            values = treeview.item(row, "values")
            if values and len(values) == 5:
                row_id, number, category, name, quantity = values
                update_data(row_id, number, category, name, quantity)
        view_command()
    except Exception as e:
        print("Ошибка при обновлении базы данных:", e)

def add_command():
    """ Обработчик кнопки добавления """
    try:
        add_data(number_text.get(), category_text.get(), name_text.get(), quantity_text.get())
        view_command()
    except Exception as e:
        print("Error adding record:", e)

def view_command():
    """ Обработчик кнопки просмотра """
    treeview.delete(*treeview.get_children())
    selected_category = category_filter.get()
    for row in view_data(selected_category):
        treeview.insert('', 'end', values=row)

def populate_category_filter():
    """ Заполняет фильтр категорий уникальными значениями из базы данных """
    cursor.execute("SELECT DISTINCT category FROM inventory")
    categories = ["All"] + [row[0] for row in cursor.fetchall()]
    category_filter['values'] = categories
    category_filter.current(0)

conn, cursor = connect_db()
create_table(cursor)

# Создание графического интерфейса
window = Tk()
window.title("Inventory Management")

# Создание меток и полей ввода для данных
label_number = Label(window, text="Number")
label_number.grid(row=0, column=0)
number_text = StringVar()
entry_number = Entry(window, textvariable=number_text)
entry_number.grid(row=0, column=1)

label_category = Label(window, text="Category")
label_category.grid(row=0, column=2)
category_text = StringVar()
entry_category = Entry(window, textvariable=category_text)
entry_category.grid(row=0, column=3)

label_name = Label(window, text="Name")
label_name.grid(row=1, column=0)
name_text = StringVar()
entry_name = Entry(window, textvariable=name_text)
entry_name.grid(row=1, column=1)

label_quantity = Label(window, text="Quantity")
label_quantity.grid(row=1, column=2)
quantity_text = IntVar()
entry_quantity = Entry(window, textvariable=quantity_text)
entry_quantity.grid(row=1, column=3)

# Создание фильтра по категориям
label_filter = Label(window, text="Filter by Category")
label_filter.grid(row=2, column=0)
category_filter = ttk.Combobox(window)
category_filter.grid(row=2, column=1)
populate_category_filter()

# Создание кнопок
button_view = Button(window, text="View All", command=view_command)
button_view.grid(row=3, column=0)

button_add = Button(window, text="Add", command=add_command)
button_add.grid(row=3, column=1)

button_update = Button(window, text="Update", command=update_command)
button_update.grid(row=3, column=2)

button_delete = Button(window, text="Delete", command=delete_command)
button_delete.grid(row=3, column=3)

button_close = Button(window, text="Close", command=window.quit)
button_close.grid(row=3, column=4)

# Создание таблицы для отображения данных
treeview_frame = Frame(window)
treeview_frame.grid(row=4, column=0, columnspan=5, sticky="nsew")

treeview = ttk.Treeview(treeview_frame, columns=("ID", "Number", "Category", "Name", "Quantity"), show='headings')
treeview.heading("ID", text="ID")
treeview.column("ID", width=50)
treeview.heading("Number", text="Number")
treeview.column("Number", width=100)
treeview.heading("Category", text="Category")
treeview.column("Category", width=100)
treeview.heading("Name", text="Name")
treeview.column("Name", width=150)
treeview.heading("Quantity", text="Quantity")
treeview.column("Quantity", width=100)
treeview.grid(row=0, column=0, sticky="nsew")

# Добавление горизонтальной полосы прокрутки
treeview_scrollbar = ttk.Scrollbar(treeview_frame, orient="horizontal", command=treeview.xview)
treeview_scrollbar.grid(row=1, column=0, sticky="ew")
treeview.configure(xscrollcommand=treeview_scrollbar.set)

# Добавление полосы прокрутки к виджету Treeview
treeview_scrollbar_y = ttk.Scrollbar(treeview_frame, orient="vertical", command=treeview.yview)
treeview_scrollbar_y.grid(row=0, column=1, sticky="ns")
treeview.configure(yscrollcommand=treeview_scrollbar_y.set)

# Привязка события щелчка мыши для выбора записи в таблице
treeview.bind('<<TreeviewSelect>>', get_selected_row)

# Установка стилей текста в ячейках таблицы
style = ttk.Style()
style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
style.configure("Treeview", font=("Helvetica", 10), anchor="center")

window.mainloop()

conn.close()