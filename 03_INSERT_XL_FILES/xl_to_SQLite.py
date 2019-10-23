import sqlite3
from sqlite3 import Error
import csv
import win32com.client
import os

DB_FILE_PATH = 'imdb.db'
XL_FILE_PATH = '..\\Sample_files\\IMDB-Movie-Data.xlsx'


def connect_to_db(db_file):
    """
    Connect to an SQlite database, if db file does not exist it will be created
    :param db_file: absolute or relative path of db file
    :return: sqlite3 connection
    """
    sqlite3_conn = None

    try:
        sqlite3_conn = sqlite3.connect(db_file)
        return sqlite3_conn

    except Error as err:
        print(err)

        if sqlite3_conn is not None:
            sqlite3_conn.close()


def insert_values_to_table(table_name, csv_file_path):
    """
    Open a csv file, store its content in a list excluding header and insert the data from the list to db table
    :param table_name: table name in the database to insert the data into
    :param csv_file_path: path of the csv file to process
    :return: None
    """

    values_to_insert = open_csv_file(csv_file_path)

    if len(values_to_insert) > 0:
        column_names, column_numbers = get_column_names_from_db_table(table_name)

        values_str = '?,' * column_numbers
        values_str = values_str[:-1]

        c.execute('CREATE TABLE IF NOT EXISTS ' + table_name +
                  '(rank INTEGER, '
                  'title VARCHAR, '
                  'genre VARCHAR, '
                  'description VARCHAR, '
                  'director VARCHAR, '
                  'actors VARCHAR, '
                  'year_release INTEGER, '
                  'runTime INTEGER, '
                  'rating DECIMAL, '
                  'votes INTEGER, '
                  'revenue DECIMAL, '
                  'metascore INTEGER)')

        sql_query = 'INSERT INTO ' + table_name + '(' + column_names + ') VALUES (' + values_str + ')'

        c.executemany(sql_query, values_to_insert)
        conn.commit()


def open_csv_file(csv_file_path):
    """
    Open and read data from a csv file without headers (skipping the first row)
    :param csv_file_path: path of the csv file to process
    :return: a list with the csv content
    """
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)

        data = list()
        for row in reader:
            data.append(row)

        return data


def get_column_names_from_db_table(table_name):
    """
    Scrape the column names from a database table to a list and convert to a comma separated string, count the number
    of columns in a database table
    :param table_name: table name to get the column names from
    :return: a comma separated string with column names, an integer with number of columns
    """

    table_column_names = 'PRAGMA table_info(' + table_name + ');'
    c.execute(table_column_names)
    table_column_names = c.fetchall()

    column_count = len(table_column_names)

    column_names = list()

    for name in table_column_names:
        column_names.append(name[1])

    return ', '.join(column_names), column_count


def xl_file_to_csv(xl_file, sh_index):
    """
    Open a workbook, get the index of the worksheet (sh_index) and save sheet(s) as csv files
    :param xl_file: workbook path
    :param sh_index: index of the worksheet (0 - all worksheets)
    :return: generated csv file name
    """

    xl_app = win32com.client.Dispatch("Excel.Application")
    xl_app.Visible = 0
    xl_app.DisplayAlerts = 0

    work_book = xl_app.Workbooks.Open(xl_file)

    csv_file_name = xl_file

    if work_book.Worksheets.count >= sh_index:
        work_sheet = work_book.Worksheets(sh_index)
        csv_file_name = save_csv_file(work_sheet, csv_file_name)

        work_book.Close(SaveChanges=0)
        xl_app.Quit()

        return csv_file_name
    else:
        print('There is not a tab in the workbook with index: {}'.format(sh_index))


def save_csv_file(work_sheet, file_name):
    """
    Saving a worksheet to a csv file and add the csv file name to a list, naming convention applied
    :param work_sheet: worksheet to save csv (type: win32com.client.CDispatch)
    :param file_name: list holding csv file names
    :return: list of csv file names
    """

    output_csv_name = file_name + '.csv'
    work_sheet.SaveAs(output_csv_name, 6)
    file_name = output_csv_name

    return file_name


if __name__ == '__main__':

    conn = connect_to_db(DB_FILE_PATH)

    # Get the absolute path of the XL file
    XL_FILE_PATH = os.path.abspath(XL_FILE_PATH)

    csv_file = xl_file_to_csv(XL_FILE_PATH, 1)

    if conn is not None:
        c = conn.cursor()
        insert_values_to_table('imdb_temp', csv_file)
        conn.close()
    else:
        print('Connection to database failed')
