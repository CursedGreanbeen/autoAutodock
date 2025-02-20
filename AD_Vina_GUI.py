import tkinter as tk
import real_auto_dock
import list_files

# # Список ярлыков полей.
# labels = [
#     "Имя:",
#     "Фамилия:",
#     "Адрес 1:",
#     "Адрес 2:",
#     "Город:",
#     "Регион:",
#     "Почтовый индекс:",
#     "Страна:",
# ]
#
# # Цикл для списка ярлыков полей.
# for idx, text in enumerate(labels):
#     # Создает ярлык с текстом из списка ярлыков.
#     label = tk.Label(master=frm_form, text=text)
#     # Создает текстовое поле которая соответствует ярлыку.
#     entry = tk.Entry(master=frm_form, width=50)
#     # Использует менеджер геометрии grid для размещения ярлыков и
#     # текстовых полей в строку, чей индекс равен idx.
#     label.grid(row=idx, column=0, sticky="e")
#     entry.grid(row=idx, column=1)


def main():
    proteins = ['7txt', '8dpf', '8hff', '8v6u', '9cbl']
    ligands = ['sulfon', 'tietan']
    path = r'C:\Users\Nadezhda\OneDrive\Рабочий стол\Dock'


    window = tk.Tk()
    greet = tk.Label(text='Enter prots and ligs')
    greet.pack()

    prots_label = tk.Label(text='prots')
    prots = tk.Entry()
    ligs_label = tk.Label(text='ligs')
    ligs = tk.Entry()
    prots_label.pack()
    prots.pack()
    ligs_label.pack()
    ligs.pack()

    auto_list = tk.Label(text='or gather names automatically:')
    auto_list.pack()
    butt_names = tk.Button(text='Make a list of names', command=list_files.list_names(path))
    butt_names.pack()

    butt_dock = tk.Button(text='Dock!', command=real_auto_dock.auto_autodock(proteins, ligands))
    butt_dock.pack()
    window.mainloop()


if __name__ == "__main__":
    main()