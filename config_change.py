import os


def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()


proteins = ['7txt', '8dpf', '8hff', '8v6u', '9cbl']
ligands = ['sulfon', 'tietan']

path = r'C:\Users\Nadezhda\OneDrive\Рабочий стол\Dock'
list_dir = os.listdir(path)
for file in list_dir:
    if 'config' in file:
        pass

