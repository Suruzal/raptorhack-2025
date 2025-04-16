import sqlite3

def connect_db(db_name='user_data.db'):
    connection = sqlite3.connect(db_name)
    connection.row_factory = sqlite3.Row
    return connection

def close_db(connection):
    if connection:
        connection.close()