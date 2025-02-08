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


def insert_ticket(title: str, content: str, summary: str, author_id: str) -> int:
    cnx = connect_to_mysql()
    if not cnx:
        return {"error": "Database connection failed"}

    cursor = cnx.cursor()

    try:
        query = "INSERT INTO tickets (title, content, summary, author_id) VALUES (%s, %s, %s)"
        values = (title, content, summary, author_id)
        cursor.execute(query, values)
        cnx.commit()
        ticket_id = cursor.lastrowid  # Get auto-generated ticket_id

        return ticket_id

    except mysql.connector.Error as err:
        raise RuntimeError(f"Database error: {err}")

    finally:
        cursor.close()
        cnx.close()


def insert_azure_user(user_id: str, user_name: str, user_group: str) -> None:
    cnx = connect_to_mysql()
    if not cnx:
        return {"error": "Database connection failed"}

    cursor = cnx.cursor()

    try:
        query = "INSERT INTO azure_users (user_id, user_name, user_group) VALUES (%s, %s, %s)"
        values = (
            user_id,
            user_name,
            user_group,
        )
        cursor.execute(query, values)
        cnx.commit()
        return None

    except mysql.connector.Error as err:
        return {"error": str(err)}

    finally:
        cursor.close()
        cnx.close()


def is_azure_user_in_db(user_id: str) -> bool:
    cnx = connect_to_mysql()
    if not cnx:
        return {"error": "Database connection failed"}

    cursor = cnx.cursor()

    try:
        query = "SELECT user_id FROM azure_users WHERE user_id = %s"
        values = (user_id,)
        cursor.execute(query, values)

        result = cursor.fetchone()
        return result is not None

    except mysql.connector.Error as err:
        print(f"Database error while checking Azure user: {err}")
        return False

    finally:
        cursor.close()
        cnx.close()
