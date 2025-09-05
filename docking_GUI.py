import tkinter as tk
from docking_controller import collect_res, list_names


def main():
    proteins = []
    ligands = []

    def names():
        nonlocal proteins, ligands
        proteins, ligands = list_names(proteins, ligands)
        list_of_prots = tk.Label(text=proteins)
        list_of_ligs = tk.Label(text=ligands)
        list_of_prots.pack()
        list_of_ligs.pack()

    def dock():
        nonlocal proteins, ligands
        if proteins and ligands:
            collect_res(proteins, ligands)
            proteins, ligands = [], []

    window = tk.Tk()
    greet = tk.Label(text='Enter proteins and ligands')
    greet.pack()

    prots_label = tk.Label(text='proteins')
    prots_entry = tk.Entry()
    ligs_label = tk.Label(text='ligands')
    ligs_entry = tk.Entry()

    prots_label.pack()
    prots_entry.pack()
    ligs_label.pack()
    ligs_entry.pack()

    def entries():
        nonlocal proteins, ligands

        for p in prots_entry.get().split():
            proteins.append(p)
        for l in ligs_entry.get().split():
            ligands.append(l)

        prots_entry.delete(0, tk.END)
        ligs_entry.delete(0, tk.END)

        # Для проверки вы можете вывести текущие значения в консоль
        print("Proteins:", proteins)
        print("Ligands:", ligands)

    # Кнопка для добавления введенных данных
    submit_button = tk.Button(text='Submit', command=entries)
    submit_button.pack()

    auto_list = tk.Label(text='or gather names automatically:')
    auto_list.pack()

    butt_names = tk.Button(text='Make a list of names', command=names)
    butt_names.pack()

    butt_dock = tk.Button(text='Dock!', command=dock)
    butt_dock.pack()

    window.mainloop()


if __name__ == "__main__":
    main()

