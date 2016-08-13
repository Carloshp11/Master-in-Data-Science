import os
import re

# -------------------------------------------------/ Fixed variables developement /-----------------------------------------

Project_name = 'Project_20160811_001'
date = '20160811'

# -------------------------------------------------/ Variable definitions  /----------------------------------------

path_Definitions = os.path.join(os.getcwd(), Project_name, 'Definitions')
path_Input = os.path.join(os.getcwd(), Project_name, 'Definitions')
path_Output = os.path.join(os.getcwd(), Project_name, 'Definitions')
path_Filtered = os.path.join(os.getcwd(), Project_name, 'Definitions')

# -------------------------------------------------/ Class definitions  /----------------------------------------


class File(object):
    def __init__(self, path, input_mode = True):
        if input_mode:
            self.handler = open(path, 'r', encoding="utf-8")
        else:
            self.handler = open(path, 'w', encoding="utf-8")
        self.name = os.path.basename(path)


class DefFile(File):
    def __init__(self, path, input_mode = True):
        File.__init__(self, path, input_mode)
        self.columns = {}
        self.delimiter = '\t'

        first_line = True
        for line in self.handler:
            if first_line:
                first_line = False
                continue
            line = line.split(self.delimiter)
            if len(line) != 3:
                raise ValueError('%s delimiter file has incorrect number of columns' % self.name)
            if line[1] not in ['character', 'integer', 'numeric', 'bool']:
                raise ValueError('Invalid type for column %s in %s file' % (line[0], self.name))
            self.columns[line[0]] = line[2]


# -------------------------------------------------/ Definitions /-----------------------------------------
definitions = {}
for file in os.listdir(path_Definitions):
    if not file.endswith('.csv'):
        continue
    element = DefFile(os.path.join(path_Definitions, file))
    definitions[element.name] = element
element = None

if len(definitions) == 0:
    raise FileNotFoundError('Definition files missing')

# -------------------------------------------------/ Input /-----------------------------------------
if len(os.listdir(path_Input)) == 0 or len(os.listdir(path_Input)) != len(definitions):
    raise FileNotFoundError('Input files missing or more than definitions')

Input = []
for file in os.listdir(path_Input):
    Input.append(File(os.path.join(path_Input, file)))









def get_files():
    if os.path.isfile('C:/Users/Carlos/Programming/Python/Csv_Manager/Csv_test.csv'):
        input_handler = open('C:/Users/Carlos/Programming/Python/Csv_Manager/Csv_test.csv', 'r', encoding="utf-8")
        output_handler = open(input_handler.name[:-4] + '_transformed.csv', 'w')
        # manage_file(input_handler, output_handler)
    elif os.path.isdir('C:/Users/Carlos/Programming/Python/Csv_Manager/Csv_test.csv'):
        for csv in os.listdir('C:/Users/Carlos/Programming/Python/Csv_Manager/Csv_test.csv'):
            if csv[-4:] != '.csv' or csv[-16:] == '_transformed.csv':
                continue
            input_handler = open(csv, 'r', encoding="utf-8")
            output_handler = open(input_handler.name[:-4] + '_transformed.csv', 'w')
            # manage_file(input_handler, output_handler)

