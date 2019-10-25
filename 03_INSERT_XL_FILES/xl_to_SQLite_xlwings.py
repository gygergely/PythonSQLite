import sqlite3
from sqlite3 import Error
import xlwings as xw

DB_FILE_PATH = 'sampleSQLite.db'
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


def open_xl_file(src_xl_file):
    """
    Open and read data from a csv file without headers (skipping the first row)
    :param src_xl_file: path of the csv file to process
    :return: a list with the csv content
    """
    # Start Excel - set visible keyword parameter to True to make the Excel app visible
    xl_app = xw.App(visible=False, add_book=False)

    # Open the source file
    wb = xl_app.books.open(src_xl_file)

    # Get the data sheet by index ref
    ws = wb.sheets(1)

    # Load data range to a list - 1st  row considered as a header
    data_range = ws.range(2, 1).expand()
    data = list(data_range.raw_value)

    # Close workbook, close Excel app
    wb.close()
    xl_app.quit()

    return data


def insert_values_to_table(table_name, xl_file):
    """
    Open a csv file with pandas, store its content in a pandas data frame, change the data frame headers to the table
    column names and insert the data to the table
    :param table_name: table name in the database to insert the data into
    :param xl_file: path of the xl file to process
    :return: None
    """

    conn = connect_to_db(DB_FILE_PATH)

    if conn is not None:
        c = conn.cursor()

        # Create table if it is not exist
        c.execute('CREATE TABLE IF NOT EXISTS ' + table_name +
                  '(rank        INTEGER,'
                  'title        VARCHAR,'
                  'genre        VARCHAR,'
                  'description  VARCHAR,'
                  'director     VARCHAR,'
                  'actors       VARCHAR,'
                  'year_release INTEGER,'
                  'runTime      INTEGER,'
                  'rating       DECIMAL,'
                  'votes        INTEGER,'
                  'revenue      DECIMAL,'
                  'metascore    INTEGER)')

        values_to_insert = open_xl_file(xl_file)

        # Insert to table
        if len(values_to_insert) > 0:
            column_names, column_numbers = get_column_names_from_db_table(c, table_name)

            values_str = '?,' * column_numbers
            values_str = values_str[:-1]

            sql_query = 'INSERT INTO ' + table_name + '(' + column_names + ') VALUES (' + values_str + ')'

            c.executemany(sql_query, values_to_insert)
            conn.commit()

            print('SQL insert process finished')
        else:
            print('Nothing to insert')

        conn.close()

    else:
        print('Connection to database failed')


def get_column_names_from_db_table(sql_cursor, table_name):
    """
    Scrape the column names from a database table to a list and convert to a comma separated string, count the number
    of columns in a database table
    :param sql_cursor: sqlite cursor
    :param table_name: table name to get the column names from
    :return: a comma separated string with column names, an integer with number of columns
    """

    table_column_names = 'PRAGMA table_info(' + table_name + ');'
    sql_cursor.execute(table_column_names)
    table_column_names = sql_cursor.fetchall()

    column_count = len(table_column_names)

    column_names = list()

    for name in table_column_names:
        column_names.append(name[1])

    return ', '.join(column_names), column_count


if __name__ == '__main__':
    insert_values_to_table('imdb_temp', XL_FILE_PATH)