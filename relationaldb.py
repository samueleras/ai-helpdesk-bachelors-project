import os
import mysql.connector
from mysql.connector import errorcode
from custom_types import AppConfig


def connect_to_mysql(config: AppConfig) -> None:
    try:
        mysql_password = os.getenv("MYSQL_PASSWORD")
        cnx = mysql.connector.connect(
            user=config["mysql"]["user"],
            password=mysql_password,
            host=config["mysql"]["host"],
            database=config["mysql"]["database"],
        )
        return cnx
    except mysql.connector.Error as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print(f"Something is wrong with your user name or password: {e.msg}")
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"Database does not exist: {e.msg}")
        else:
            print(f"Database connection failed: {e.msg}")
        raise RuntimeError("Database connection failed")
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise RuntimeError("Database connection failed") from e


def insert_ticket(
    title: str, content: str, summary: str, author_id: str, config: AppConfig
) -> int:
    cnx = connect_to_mysql(config)

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


def insert_azure_user(
    user_id: str, user_name: str, user_group: str, config: AppConfig
) -> None:
    cnx = connect_to_mysql(config)
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
        print(f"Inserted user {user_name} into database")

    except Exception as e:
        print(f"Database error: {e}")
        raise RuntimeError(f"Database error: {e}") from e

    finally:
        cursor.close()
        cnx.close()

    return None


def is_azure_user_in_db(user_id: str, config: AppConfig) -> bool:
    cnx = connect_to_mysql(config)
    if not cnx:
        return {"error": "Database connection failed"}

    cursor = cnx.cursor()
    try:
        query = "SELECT user_id FROM azure_users WHERE user_id = %s"
        values = (user_id,)
        cursor.execute(query, values)

        result = cursor.fetchone()
        return result is not None

    except Exception as e:
        print(f"Database error: {e}")
        raise RuntimeError(f"Database error: {e}") from e

    finally:
        cursor.close()
        cnx.close()
