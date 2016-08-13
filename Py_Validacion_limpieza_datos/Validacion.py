import os
import re

# ---------------------------------------/ Fixed variables developement /-----------------------------------------

Project_name = 'Project_20160811_001'
date = '20160811'

# -----------------------------------------/ Variable definitions  /----------------------------------------------

path_Definitions = os.path.join(os.getcwd(), Project_name, 'Definitions')
path_Input = os.path.join(os.getcwd(), Project_name, 'Input')
path_Output = os.path.join(os.getcwd(), Project_name, 'Output')
path_Filtered = os.path.join(os.getcwd(), Project_name, 'Filtered_out')

# -----------------------------------------/ function definitions  /----------------------------------------------


def detect_delimiter(sample_line):
    delimiter = None
    greater = 1
    if len(sample_line.split('\t')) > greater:
        delimiter = '\t'
    if len(sample_line.split(';')) > greater:
        delimiter = ';'
    if len(sample_line.split(',')) > greater:
        delimiter = ','
    if delimiter is None:
        raise SyntaxError('Delimiter wasn\'t detected as one of these values: \\t, ; or ,')
    return delimiter

# ------------------------------------------/ Class definitions  /------------------------------------------------


class File(object):
    def __init__(self, path, input_mode=True):
        if input_mode:
            self.handler = open(path, 'r', encoding="utf-8")
            self.first_line = self.handler.readline()
            self.handler = open(path, 'r', encoding="utf-8")
        else:
            self.handler = open(path, 'w', encoding="utf-8")
        self.name = os.path.basename(path)


class DefFile(File):
    def __init__(self, path):
        File.__init__(self, path, True)
        self.columns = {}
        self.delimiter = '\t'

        number_of_dates = 0
        first_line = True
        # noinspection PyShadowingNam
        for line in self.handler:
            if first_line:
                first_line = False
                continue
            line = line.split(self.delimiter)
            if len(line) != 3:
                raise ValueError('%s delimiter file has incorrect number of columns' % self.name)
            if line[1] not in ['character', 'integer', 'numeric', 'bool', 'date', 'percentage']:
                raise ValueError('Invalid type for column %s in %s file' % (line[0], self.name))
            self.columns[line[0]] = ['__' + line[2].rstrip('\n') + '__', line[1]]
        # noinspection PyShadowingNames
        for field in self.columns:
            if self.columns[field][1] == 'date':
                number_of_dates += 1
        if number_of_dates > 1:
            raise ValueError('There are %i dates defined. There can only be one.' % number_of_dates)


class InputFile(File):
    def __init__(self, path):
        File.__init__(self, path, True)
        self.delimiter = detect_delimiter(self.first_line)


class FilterOutFile(File):
    def __init__(self, name):
        File.__init__(self, os.path.join(path_Filtered, name), False)


class OutputFilePrev(File):
    def __init__(self, name):
        File.__init__(self, os.path.join(path_Output, name), False)
        self.datepos = None
        self.yearpos = None
        self.monthpos = None
        self.daypos = None

    # noinspection PyShadowingNames
    def set_pos(self, same, fourdigits, lastdate, more_than_twelve):
        checks = 0
        for check in fourdigits:
            if check is True:
                checks += 1
        if checks > 1:
            raise ValueError('Some row(s) in date column of file %s contains more than one number with more \
                              than two digits' % self.name)
        if checks == 0:
            raise ValueError('None of the positions of date column in file %s contains four digits. Year must be \
                              written in four digits format.' % self.name)
        for position, check in enumerate(fourdigits):
            if check is True:
                self.yearpos = position
        checks = 0
        for check in more_than_twelve:
            if check is True:
                checks += 1
        if checks > 2:
            raise ValueError('All three number positions of date column in file %s surpass in some column(s) the \
                              number 12. As this is impossible for months, date format is inconsistent' % self.name)
        if checks == 2:     # If checks ==2 then only one field is always 12 or less. Therefore that's the month
            for position, check in enumerate(more_than_twelve):
                if check is False:
                    self.monthpos = position
            for position in [0, 1, 2]:
                if position != self.yearpos and position != self.monthpos:
                    self.daypos = position
                    break
        else:               # In this case only the year is above 12. We must suppose what the month is by the ammount
                            # of times it is repeated consecutively, which is probably greater than for the day.
            posibilities = [0, 1, 2]
            posibilities.remove(self.yearpos)
            if same[posibilities[0]] == same[posibilities[1]]:  # Tie break: I guess what I feel more reasonable
                if self.yearpos == 2:
                    self.monthpos = 1
                    self.daypos = 0
                else:
                    self.monthpos = 1
                    self.daypos = 2
            else:                                               # No tie break
                if same[posibilities[0]] > same[posibilities[1]]:
                    self.monthpos = posibilities[0]
                    self.daypos = posibilities[1]
                else:
                    self.monthpos = posibilities[1]
                    self.daypos = posibilities[0]


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

# -------------------------------------------------/ Input /------------------------------------------------
if len(os.listdir(path_Input)) == 0 or len(os.listdir(path_Input)) != len(definitions):
    raise FileNotFoundError('Input files missing or more than definitions')

Input = {}
for file in os.listdir(path_Input):
    if not file.endswith('.csv'):
        continue
    element = InputFile(os.path.join(path_Input, file))
    Input[element.name] = element
element = None

# -------------------------------------------/ Check and write/----------------------------------------------

for file in Input:
    file = Input[file]

    regex = {}
    for i, v in enumerate(file.first_line.rstrip('\n').split(file.delimiter)):
        regex[i] = v

    output = OutputFilePrev(file.name)
    output.handler.write('\t'.join(file.first_line.split(file.delimiter)))
    filtered = FilterOutFile(file.name)
    filtered.handler.write(file.delimiter.join(file.first_line.rstrip('\n').split(file.delimiter) +
                                               ['Troublesome column(s)']) + '\n')
    # TODO pensar cómo manejar los quotes
    file.handler.readline()

    same = [0, 0, 0]
    fourdigits = [False, False, False]
    lastdate = [0, 0, 0]
    more_than_twelve = [False, False, False]

    for line in file.handler:
        trouble = []
        line = line.rstrip('\n').split(file.delimiter)
        for index, field in enumerate(line):
            match = re.match(definitions[file.name].columns[regex[index]][0], '__' + field + '__')
            if match is None:
                trouble.append(regex[index])
            if definitions[file.name].columns[regex[index]][1] == 'date' and len(trouble) == 0:
                for i in [0, 1, 2]:
                    if len(match.groups()[i]) >= 3:
                        fourdigits[i] = True
                        more_than_twelve[i] = True
                        continue
                    if match.groups()[i] == lastdate[i]:
                        same[i] += 1
                    lastdate[i] = match.groups()[i]
                    if int(match.groups()[i]) > 12:
                        more_than_twelve[i] = True

            if index == len(line) - 1:
                if len(trouble) > 0:
                    filtered.handler.write(file.delimiter.join(line + [' && '.join(trouble)]) + '\n')
                else:
                    output.handler.write('\t'.join(line) + '\n')
    output.set_pos(same, fourdigits, lastdate, more_than_twelve)

# TODO lista de errores y sus actiaciones para Evernote
# TODO emular con un fichero x ejemplo cuál es el mensaje que se daría al usuario


