import sqlite3
from sqlite3 import Error
import csv


def connect_to_db(db_file_path):
    """
    Connect to an SQlite database, if db file does not exist it will be created
    :param db_file_path: absolute or relative path of db file
    :return: sqlite3 connection
    """
    sqlite3_conn = None

    try:
        sqlite3_conn = sqlite3.connect(db_file_path)
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

    if values_to_insert is not None:
        column_names, col_numbers = get_column_names_from_db_table(table_name)

        values_str = '?,' * col_numbers
        values_str = values_str[:-1]

        sql_query = 'INSERT INTO ' + table_name + '(' + column_names + ') VALUES (' + values_str + ')'

        c.executemany(sql_query, values_to_insert)
        conn.commit()


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

    col_count = len(table_column_names)

    column_names = list()
    for name in table_column_names:
        column_names.append(name[1])
    return ', '.join(column_names), col_count


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


if __name__ == '__main__':
    db_file_path = 'sampleSQLite.db'
    csv_file_path = 'IMDB-Movie-Data.csv'

    conn = connect_to_db(db_file_path)

    if conn is not None:
        c = conn.cursor()
        insert_values_to_table('imdb_temp', csv_file_path)
        conn.close()
    else:
        print('Connection to database failed')
