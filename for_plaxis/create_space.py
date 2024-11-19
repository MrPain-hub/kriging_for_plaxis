from pandas import read_excel
from pykrige.uk import UniversalKriging
from numpy import linspace, meshgrid
from matplotlib import pyplot as plt
from os import startfile
from tkinter import filedialog, Tk, Button, Entry, StringVar, Label, Frame


def run_UK():
    print(str(entry_0_text.get()))
    df = read_excel(str(file_path_var.get()))

    col_0 = str(entry_0_text.get())
    col_1 = str(entry_1_text.get())
    col_2 = str(entry_2_text.get())

    x_train = df.loc[:, [col_0, col_1]].to_numpy()
    target_train = df.loc[:, [col_2]].to_numpy().reshape(-1)

    x = x_train[:, 0]
    y = x_train[:, 1]
    E = target_train

    UK = UniversalKriging(x,
                          y,
                          E,
                          variogram_model='exponential'
                          )

    # # Создаем сетку данных
    x = linspace(df[col_0].min(), df[col_0].max(), 200)
    y = linspace(df[col_1].min(), df[col_1].max(), 200)
    X, Y = meshgrid(x, y)  # Создаем сетку координат

    Z, ss = UK.execute("grid", x, y)

    plt.figure(figsize=(8, 6))
    contour = plt.contourf(X, Y, Z, levels=20, cmap='terrain')  # 20 уровней изолиний
    plt.clabel(contour, inline=True, fontsize=8)  # Добавляем метки к изолиниям
    # # Добавляем заголовок и метки осей
    plt.title('Изополе')
    plt.xlabel(col_0)
    plt.ylabel(col_1)
    # Показываем график
    plt.colorbar(label=f'Значение {col_2}')  # Добавляем цветовую шкалу
    plt.grid()
    #plt.show()

    image_path = 'UK_plot.png'
    plt.savefig(image_path)

    # Закрываем график
    plt.close()

    # Открываем изображение с помощью стандартного приложения
    # Для Windows
    startfile(image_path)


def browse_file():
    # Открываем диалоговое окно для выбора файла
    filename = filedialog.askopenfilename()
    if filename:
        # Отображаем выбранный файл в текстовом поле
        file_path_var.set(filename)

# Создаем главное окно
root = Tk()
root.title("Выбор файла")


# Создаем переменную для хранения пути к файлу
file_path_var = StringVar()

# Создаем кнопку для выбора файла
browse_button = Button(root, text="Обзор файла", command=browse_file)
browse_button.pack(fill='both')

# Создаем текстовое поле для отображения пути к файлу
file_path_entry = Entry(root, textvariable=file_path_var, width=50)
file_path_entry.pack(fill='both')

Label(root, text="Введите название столбцов").pack(fill='both')
frame1 = Frame(root, bd=10)
frame1.pack(fill='both')

entry_0_text = StringVar()
entry_0_text.set("x")
entry_0 = Entry(frame1, textvariable=entry_0_text)
entry_0.grid(row=0, column=0)
entry_1_text = StringVar()
entry_1_text.set("y")
entry_1 = Entry(frame1, textvariable=entry_1_text)
entry_1.grid(row=0, column=1)
entry_2_text = StringVar()
entry_2_text.set("value")
entry_2 = Entry(frame1, textvariable=entry_2_text)
entry_2.grid(row=0, column=2)

start = Button(root, text="Кригинг", command=run_UK)
start.pack(fill='both')

# Запускаем главный цикл приложения
root.mainloop()
