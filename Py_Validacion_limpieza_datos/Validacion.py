import os


# -------------------------------------------------/ Fixed variables developement /-----------------------------------------

Project_name = 'Project_001'
date = '20160811'


# -------------------------------------------------/ Definitions /-----------------------------------------
def get_files():
    if os.path.isfile('C:/Users/Carlos/Programming/Python/Csv_Manager/Csv_test.csv'):
        input_handler = open('C:/Users/Carlos/Programming/Python/Csv_Manager/Csv_test.csv', 'r', encoding="utf-8")
        output_handler = open(input_handler.name[:-4] + '_transformed.csv', 'w')
        manage_file(input_handler, output_handler)
    elif os.path.isdir('C:/Users/Carlos/Programming/Python/Csv_Manager/Csv_test.csv'):
        for csv in os.listdir('C:/Users/Carlos/Programming/Python/Csv_Manager/Csv_test.csv'):
            if csv[-4:] != '.csv' or csv[-16:] == '_transformed.csv':
                continue
            input_handler = open(csv, 'r', encoding="utf-8")
            output_handler = open(input_handler.name[:-4] + '_transformed.csv', 'w')
            manage_file(input_handler, output_handler)