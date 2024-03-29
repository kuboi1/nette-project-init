import mysql.connector
import os
from mysql.connector import MySQLConnection, Error as MySqlError

class SqlManager:
    connection: MySQLConnection

    def __init__(self) -> None:
        self.connection = None
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.close()
        return False

    def connect(self, host: str, user: str, password: str, db: str = None) -> bool:
        try:
            # Establish a connection
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=db
            )
            
            if self.is_connected():
                print(f'Successfully connected to MySQL Server version {self.connection.get_server_info()}')
                return True
        except MySqlError as e:
            print('There was an error while connecting to MySQL: ', e)
            return False
    
    def close(self) -> None:
        if (self.is_connected()):
            self.connection.cursor().close()
            self.connection.close()
            print("MySQL connection was successfully closed")

    def execute_query(self, query: str) -> bool:
        if not self.is_connected():
            print('CAN\'T EXECUTE QUERY -> not connected to any database')
            return False
        
        if not query.endswith(';'):
            query += ';'

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
            print(f'\tSql query "{query}" executed successfully')
            return True
        except MySqlError as e:
            print(f'There was an error while executing an sql query "{query}": {e}')
    
    def execute_script(self, script: str, name='') -> bool:
        if not self.is_connected():
            print('CAN\'T EXECUTE SCRIPT -> not connected to any database')
            return False

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(script, multi=True)
            name = '' if name == '' else f'"{name}" '
            print(f'\tSql script {name}executed successfully')
            return True
        except MySqlError as e:
            print(f'There was an error while executing an sql script: {e}')
    
    def create_database(self, name: str, charset='utf8mb4', collate='utf8mb4_unicode_520_ci') -> bool:
        return self.execute_query(f'CREATE DATABASE {name} CHARACTER SET {charset} COLLATE {collate};')
    
    def use_database(self, db: str) -> bool:
        return self.execute_query(f'USE {db};')

    def import_sql_file(self, path: str) -> bool:
        if not os.path.exists(path):
            print(f'CAN\'T IMPORT SQL FILE -> path "{path}" doesn\'t exist')
            return False
        if not self.is_connected():
            print('CAN\'T IMPORT SQL FILE -> not connected to any database')
            return False
        
        with open(path, 'r', encoding='utf-8') as sql_f:
            return self.execute_script(sql_f.read(), path.split('\\')[-1])

    def is_connected(self) -> bool:
        return self.connection is not None and self.connection.is_connected()
    
    def is_sql_comment(self, line: str) -> bool:
        if line.startswith('--'):
            return True
        
        return False