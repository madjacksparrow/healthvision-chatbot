import mysql.connector as sql

class DBConnection:
    def __init__(self):
        pass
    def createConnection(self,hostname,u_name,passwd,db):
        conn = sql.connect(host = hostname,
                           user = u_name,
                           password = passwd,
                           database = db)
        return conn 
    def isConnectionSuccess(self,conn):
        return conn.is_connected()
    def create_cursor(self,conn):
        cursor  = conn.cursor()
        return cursor
