import sqlite3
from sqlite3 import Error
import csv

DB_FILE_PATH = 'sampleSQLite.db'
CSV_FILE_PATH = '..\\Sample_files\\IMDB-Movie-Data.csv'


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

        # Read CSV file content
        values_to_insert = open_csv_file(csv_file_path)

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
    insert_values_to_table('imdb_temp', CSV_FILE_PATH)
