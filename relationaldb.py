import mysql.connector
from mysql.connector import errorcode


def connect_to_mysql() -> None:
    try:
        cnx = mysql.connector.connect(
            user="ai_helpdesk",
            password="test1234",
            host="127.0.0.1",
            database="db_ai_helpdesk",
        )
        return cnx
    except mysql.connector.Error as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(e)
        return None


def insert_ticket(title: str, content: str, summary: str, author_id: str) -> int:
    cnx = connect_to_mysql()
    if not cnx:
        print("Database connection failed")
        raise RuntimeError("Database connection failed") from e

    cursor = cnx.cursor()

    try:
        query = "INSERT INTO tickets (title, content, summary, author_id) VALUES (%s, %s, %s)"
        values = (title, content, summary, author_id)
        cursor.execute(query, values)
        cnx.commit()
        ticket_id = cursor.lastrowid  # Get auto-generated ticket_id

        return ticket_id

    except Exception as e:
        print(f"Database error: {e}")
        raise RuntimeError(f"Database error: {e}") from e

    finally:
        cursor.close()
        cnx.close()


def insert_azure_user(user_id: str, user_name: str, user_group: str) -> None:
    cnx = connect_to_mysql()
    if not cnx:
        print("Database connection failed")
        raise RuntimeError("Database connection failed") from e

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
        print("insert successful")

    except Exception as e:
        print(f"Database error: {e}")
        raise RuntimeError(f"Database error: {e}") from e

    finally:
        cursor.close()
        cnx.close()

    return None


def is_azure_user_in_db(user_id: str) -> bool:
    cnx = connect_to_mysql()
    if not cnx:
        return {"error": "Database connection failed"}

    cursor = cnx.cursor()
    print("checking for user")
    try:
        query = "SELECT user_id FROM azure_users WHERE user_id = %s"
        values = (user_id,)
        cursor.execute(query, values)

        result = cursor.fetchone()
        print(result)
        return result is not None

    except Exception as e:
        print(f"Database error: {e}")
        raise RuntimeError(f"Database error: {e}") from e

    finally:
        cursor.close()
        cnx.close()
