#!/usr/bin/python3.5

import timing
import os
import re

# ---------------------------------------/ Fixed variables developement /-----------------------------------------

Project_name = 'Project_20160811_001'
date = '20160811'

# -----------------------------------------/ Variable definitions  /----------------------------------------------

path_Definitions = os.path.join(os.getcwd(), Project_name, 'Definitions')
path_Input = os.path.join(os.getcwd(), Project_name, 'Input')
path_Output = os.path.join(os.getcwd(), Project_name, 'Output')
path_Intermediate = os.path.join(os.getcwd(), Project_name, 'Intermediate')
path_Filtered = os.path.join(os.getcwd(), Project_name, 'Filtered_out')

# -----------------------------------------/ function definitions  /----------------------------------------------


def detect_delimiter(sample_line, name):
    delimiter = None
    greater = 1
    if len(sample_line.split('\t')) > greater:
        delimiter = '\t'
    if len(sample_line.split(';')) > greater:
        delimiter = ';'
    if len(sample_line.split(',')) > greater:
        delimiter = ','
    if delimiter is None:
        raise SyntaxError('File %s: Delimiter wasn\'t detected as one of these values: \\t, ; or ,' % name)
    return delimiter


def delete_files(folderpath):
    for the_file in os.listdir(folderpath):
        file_path = os.path.join(folderpath, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
                # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
        print('Files in %s deleted.' % folderpath)

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
        self.quote = '"'

    def refresh_handler(self):
        self.handler = open(self.handler.name, 'r', encoding="utf-8")


class DefFile(File):
    def __init__(self, path):
        File.__init__(self, path, True)
        self.columns = {}
        self.delimiter = '\t'
        self.dateRegex = None
        self.dateName = None

        number_of_dates = 0
        first_line = True

        for line in self.handler:
            if first_line:
                first_line = False
                continue
            line = line.split(self.delimiter)
            if len(line) != 3:
                raise ValueError('%s definition file has incorrect number of columns' % self.name)
            if line[1] not in ['character', 'integer', 'numeric', 'bool', 'date', 'percentage']:
                raise ValueError('Invalid type for column %s in %s file' % (line[0], self.name))
            self.columns[line[0]] = ['__' + line[2].rstrip('\n') + '__', line[1]]
        # noinspection PyShadowingNames
        for index, column in enumerate(self.columns):
            if self.columns[column][1] == 'date':
                self.dateRegex = self.columns[column][0]
                self.dateName = column
                number_of_dates += 1
        if number_of_dates > 1:
            raise ValueError(
                'There are %i dates defined. Only one if supported per file at the moment.' % number_of_dates)


class InputFile(File):
    def __init__(self, path):
        File.__init__(self, path, True)
        self.delimiter = detect_delimiter(self.first_line, self.name)
        self.dateindex = None


class FilterOutFile(File):
    def __init__(self, name):
        File.__init__(self, os.path.join(path_Filtered, name), False)
        self.troubles = set()
        self.n_errors = 0

    def writeline(self, text):
        self.handler.write(file.delimiter.join(line.args + [' && '.join(line.trouble)]) + '\n')


class OutputFilePrev(File):
    def __init__(self, name):
        File.__init__(self, os.path.join(path_Output, name), False)
        # self.datepos = None
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
                              than two digits. Either column is not date or the format is inconsistent.' % self.name)
        if checks == 0:
            raise ValueError('None of the positions of date column in file %s contains four digits. Year must be \
                              written in four digits format. Please fix this.' % self.name)
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
            posibilities = [0, 2, 3]
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
        if self.yearpos > 0:
            self.yearpos += 1
        if self.monthpos > 0:
            self.monthpos += 1
        if self.daypos > 0:
            self.daypos += 1


class Line(object):
    def __init__(self, text, delimiter, quote='"'):
        self.args = text.rstrip('\n').split(delimiter)
        self.q = quote
        self.d = delimiter
        self.trouble = []
        self.args = self.detect_complex_args()

    def detect_complex_args(self):
        processed_args = []
        complex_arg = ''
        for arg in self.args:
            if arg[-1] == self.q:
                complex_arg = (complex_arg + self.d + arg).lstrip(self.d)
                processed_args.append(complex_arg)
                complex_arg = ''
            elif complex_arg != '' or arg[0] == self.q:
                complex_arg = (complex_arg + self.d + arg).lstrip(self.d)
            else:
                processed_args.append(arg)
        if complex_arg != '':
            self.trouble = ['wrong quoting']
        return processed_args


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
delete_files(path_Output)

for file in Input:
    file = Input[file]

    regex = {}
    for i, v in enumerate(file.first_line.rstrip('\n').split(file.delimiter)):
        regex[i] = v
        if definitions[file.name].dateName == v:
            file.dateindex = i

    output = OutputFilePrev(file.name)
    output.handler.write('\t'.join(file.first_line.split(file.delimiter)))
    filtered = FilterOutFile(file.name)
    filtered.handler.write(file.delimiter.join(file.first_line.rstrip('\n').split(file.delimiter) +
                                               ['Troublesome column(s)']) + '\n')
    file.handler.readline()

    same = [0, 0, 0, 0]
    fourdigits = [False, False, False, False]
    lastdate = [0, 0, 0, 0]
    more_than_twelve = [False, False, False, False]

    # first reading to determine date format
    if definitions[file.name].dateName is not None:
        for line in file.handler:
            line = Line(line, file.delimiter, file.quote)
            match = re.match(definitions[file.name].dateRegex,
                             '__' + line.args[file.dateindex].strip(line.q) + '__')
            if match is not None:
                for i in [0, 2, 3]:
                    if len(match.groups()[i]) >= 3:
                        fourdigits[i] = True
                        more_than_twelve[i] = True
                        lastdate[i] = match.groups()[i]
                        continue
                    if match.groups()[i] == lastdate[i]:
                        same[i] += 1
                    lastdate[i] = match.groups()[i]
                    if int(match.groups()[i]) > 12:
                        more_than_twelve[i] = True
        output.set_pos(same, fourdigits, lastdate, more_than_twelve)

    # second reading to rewrite and validate output
    file.refresh_handler()
    file.handler.readline()
    for line in file.handler:
        line = Line(line, file.delimiter, file.quote)
        for index, field in enumerate(line.args):
            # ---------
            # pre-processing exceptions for specific data types
            if definitions[file.name].columns[regex[index]][1] == 'numeric':
                field = field.replace(',', '.')
            # Regex validation
            match = re.match(definitions[file.name].columns[regex[index]][0], '__' + field.strip(line.q) + '__')
            # post-processing exceptions
            if definitions[file.name].columns[regex[index]][1] == 'date' and match is not None:
                year = match.groups()[output.yearpos]
                month = match.groups()[output.monthpos]
                day = match.groups()[output.daypos]
                line.args[index] = '-'.join((year, month, day))
            # ---------
            if match is None:
                if len(line.trouble) == 0:
                    filtered.n_errors += 1
                line.trouble.append(regex[index])
                filtered.troubles.add(regex[index])

            if index == len(line.args) - 1:
                if len(line.trouble) > 0:
                    filtered.writeline(file.delimiter.join(line.args + [' && '.join(line.trouble)]) + '\n')
                else:
                    output.handler.write('\t'.join(line.args) + '\n')

    # noinspection PyUnboundLocalVariable
    if filtered.n_errors > 0:
        print('File %s encountered %i rows with some column(s) not passing validation and therefore filtered out.'
              'You should check the \"Filtered out\" files to decide if this is a problem' % (file.name, filtered.n_errors) )
print('Process completed. Check errors in case they exist and confirm to launch the whole study process or'
      'fix your files and upload them again')

