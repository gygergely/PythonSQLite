import sqlite3
from sqlite3 import Error


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


def insert_values_to_table(table_name):
    """
    Create a table if it is not existing and insert a new record into the table
    :param table_name: table name in the database to insert the data into
    :return: None
    """

    c.execute('CREATE TABLE IF NOT EXISTS ' + table_name + '(fName TEXT, lName TEXT, title TEXT, age INT)')

    values_to_insert = ('Some First Name', 'Some Last Name', 'Very good Title', 42)

    sql_query = 'INSERT INTO sample_table(fName, lName, title, age) VALUES (?,?,?,?)'

    c.execute(sql_query, values_to_insert)
    conn.commit()


if __name__ == '__main__':
    db_file_path = 'sampleSQLite.db'

    conn = connect_to_db(db_file_path)

    if conn is not None:
        c = conn.cursor()
        insert_values_to_table('sample_table')
        conn.close()
    else:
        print('Connection to database failed')
