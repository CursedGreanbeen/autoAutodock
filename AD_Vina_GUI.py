import tkinter as tk
from tkinter import ttk
from real_auto_dock import auto_autodock
from list_files import list_names, list_prots


def main():
    proteins, ligands = [], []
    dock_type = 'simple'

    def names():
        nonlocal proteins, ligands
        proteins, ligands = list_names(proteins, ligands)
        list_of_prots = ttk.Label(text=proteins)
        list_of_ligs = ttk.Label(text=ligands)
        list_of_prots.pack()
        list_of_ligs.pack()

    def prots():
        nonlocal proteins
        proteins = list_prots()
        list_of_prots = ttk.Label(text=proteins)
        list_of_prots.pack()

    def dock():
        nonlocal proteins, ligands, dock_type
        if proteins and ligands:
            auto_autodock(proteins, ligands, dock_type)
            proteins, ligands = [], []

    window = tk.Tk()
    greet = tk.Label(text='Enter proteins and ligands')
    greet.pack()

    prots_label = ttk.Label(text='proteins')
    prots_entry = ttk.Entry()
    ligs_label = ttk.Label(text='ligands')
    ligs_entry = ttk.Entry()

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

        print("Proteins:", proteins)
        print("Ligands:", ligands)

    submit_button = ttk.Button(text='Submit', command=entries)
    submit_button.pack()

    auto_list = ttk.Label(text='or gather names automatically:')
    auto_list.pack()

    butt_names = ttk.Button(text='Make a list of all names', command=names)
    butt_names.pack()

    butt_names = ttk.Button(text='Make a list of all prots', command=prots)
    butt_names.pack()

    butt_dock = ttk.Button(text='Dock!', command=dock)
    butt_dock.pack()

    window.mainloop()


if __name__ == "__main__":
    main()

