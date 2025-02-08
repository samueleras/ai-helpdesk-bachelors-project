import mysql.connector
from mysql.connector import errorcode


def connect_to_mysql():
    try:
        cnx = mysql.connector.connect(
            user="ai_helpdesk",
            password="test1234",
            host="127.0.0.1",
            database="db_ai_helpdeskai_helpdesk",
        )
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None
