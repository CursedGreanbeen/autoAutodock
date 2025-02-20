import tkinter as tk
import real_auto_dock
import list_files


def main():
    window = tk.Tk()
    greet = tk.Label(text='Enter proteins and ligands')
    greet.pack()

    prots_label = tk.Label(text='proteins')
    prots_entry = tk.Entry()
    ligs_label = tk.Label(text='ligands')
    ligs_entry = tk.Entry()
    prots_label.pack()
    prots_entry.pack()
    proteins = prots_entry.get()
    ligs_label.pack()
    ligs_entry.pack()
    ligands = ligs_entry.get()

    auto_list = tk.Label(text='or gather names automatically:')
    auto_list.pack()

    def names():
        proteins = list_files.list_names()[0]
        ligands = list_files.list_names()[1]
        list_of_prots = tk.Label(text=proteins)
        list_of_ligs = tk.Label(text=ligands)
        list_of_prots.pack()
        list_of_ligs.pack()

    butt_names = tk.Button(text='Make a list of names', command=names)
    butt_names.pack()

    dock = real_auto_dock.auto_autodock
    butt_dock = tk.Button(text='Dock!', command=dock)
    butt_dock.pack()
    
    window.mainloop()


if __name__ == "__main__":
    main()
