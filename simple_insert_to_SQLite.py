import sqlite3
from sqlite3 import Error
import os


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


if __name__ == '__main__':
    db_file_path = 'pythonsqlite.db'

    conn = connect_to_db(db_file_path)

    if conn is not None:
        conn.close()
    else:
        print('Connection to database failed')
