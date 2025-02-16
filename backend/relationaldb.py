import json
import os
from typing import List
import mysql.connector
from mysql.connector import errorcode
from custom_types import AppConfig, Technician, Ticket, TicketMessage
from ai_system.vectordb import retrieve_similar_tickets_milvus
from backend.pydantic_models import TicketFilter, User
import logging

logger = logging.getLogger(__name__)


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
            logger.error(
                f"Database credentials issue: {e.msg}",
                exc_info=True,
            )
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            logger.error(
                f"Database does not exist: {e.msg}",
                exc_info=True,
            )
        else:
            logger.error(
                f"Database connection failed: {e.msg}",
                exc_info=True,
            )
        raise RuntimeError("Database connection failed")
    except Exception as e:
        logger.error(
            f"Database connection failed: {e}",
            exc_info=True,
        )
        raise RuntimeError("Database connection failed") from e


def insert_ticket(
    title: str,
    content: str,
    summary_vector: List[float],
    author_id: str,
    config: AppConfig,
) -> int:
    cnx = connect_to_mysql(config)

    try:
        cursor = cnx.cursor()
        summary_json = json.dumps(summary_vector)

        query = "INSERT INTO tickets (title, content, summary_vector, author_id) VALUES (%s, %s, %s, %s)"
        values = (title, content, summary_json, author_id)
        cursor.execute(query, values)
        cnx.commit()
        ticket_id = cursor.lastrowid  # Get auto-generated ticket_id
        logger.info(
            "Successfully inserted ticket into MySQL.",
        )
        return ticket_id

    except Exception as e:
        logger.error(
            f"Database error on ticket insert: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Database error ticket insert: {e}") from e

    finally:
        cursor.close()
        cnx.close()


def get_ticket_messages(ticket_id: int, config: AppConfig) -> List[TicketMessage]:
    cnx = connect_to_mysql(config)
    try:
        cursor = cnx.cursor(dictionary=True)

        query = "SELECT m.message, u.user_name as author_name, u.user_group as group, m.created_at FROM ticket_messages m INNER JOIN azure_users u ON m.author_id = u.user_id WHERE ticket_id = %s ORDER BY created_at ASC"
        cursor.execute(query, (ticket_id,))
        messages = cursor.fetchall() or []

        return messages

    except Exception as e:
        logger.error(
            f"Database error: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Database error: {e}") from e

    finally:
        cursor.close()
        cnx.close()


def get_ticket(ticket_id: int, user: User, config: AppConfig) -> Ticket:
    cnx = connect_to_mysql(config)
    try:
        cursor = cnx.cursor()

        query = "SELECT ticket_id, title, content, summary_vector, creation_date, closed_date, u.user_name as author_name, a.user_name as assignee_name FROM tickets t INNER JOIN azure_users u ON t.author_id = u.user_ID LEFT JOIN azure_users a on t.assignee_id = a.user_id WHERE ticket_id = %s"
        cursor.execute(query, (ticket_id,))
        ticket = cursor.fetchone()

        ticket["similar_tickets"] = []
        if "summary_vector" in ticket and user.group == "technician":
            # Convert JSON string back to vector list
            summary_vector = json.loads(ticket["summary_vector"])
            similar_tickets = retrieve_similar_tickets_milvus(summary_vector)
            ticket["similar_tickets"] = similar_tickets

        if "summary_vector" in ticket:
            ticket.pop("summary_vector")  # Field not needed on frontend

        ticket["ticket_messages"] = get_ticket_messages(ticket_id, config)

        return ticket

    except Exception as e:
        logger.error(
            f"Database error: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Database error: {e}") from e

    finally:
        cursor.close()
        cnx.close()


def get_filtered_tickets(filter_data: TicketFilter, config: AppConfig) -> List[Ticket]:
    cnx = connect_to_mysql(config)
    try:
        cursor = cnx.cursor(dictionary=True)

        query = "SELECT ticket_id, title, content, creation_date, closed_date, u.user_name as author_name, a.user_name as assignee_name FROM tickets t INNER JOIN azure_users u ON t.author_id = u.user_ID LEFT JOIN azure_users a on t.assignee_id = a.user_id WHERE 1=1"

        params = ()
        if filter_data.assignee_id is not None:
            query += " AND (assignee_id = %s)"
            params += (filter_data.assignee_id,)

        query += " ORDER BY creation_date DESC"
        cursor.execute(query, params)
        tickets = cursor.fetchall()

        for ticket in tickets:
            ticket["similar_tickets"] = []
            ticket["ticket_messages"] = []

        return tickets

    except Exception as e:
        logger.error(
            f"Database error: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Database error: {e}") from e

    finally:
        cursor.close()
        cnx.close()


def get_user_tickets(user: User, config: AppConfig) -> List[Ticket]:
    cnx = connect_to_mysql(config)
    try:
        cursor = cnx.cursor(dictionary=True)

        query = "SELECT ticket_id, title, content, creation_date, closed_date, u.user_name as author_name, a.user_name as assignee_name FROM tickets t INNER JOIN azure_users u ON t.author_id = u.user_ID LEFT JOIN azure_users a on t.assignee_id = a.user_id WHERE user_id = %s ORDER BY creation_date DESC"
        cursor.execute(query, (user.user_id,))
        tickets = cursor.fetchall()

        for ticket in tickets:
            ticket["similar_tickets"] = []
            ticket["ticket_messages"] = []

        return tickets

    except Exception as e:
        logger.error(
            f"Database error: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Database error: {e}") from e

    finally:
        cursor.close()
        cnx.close()


def get_technicians(config: AppConfig) -> List[Technician]:
    cnx = connect_to_mysql(config)
    try:
        cursor = cnx.cursor(dictionary=True)

        query = "SELECT user_id, user_name FROM azure_users WHERE group = 'technician'"
        cursor.execute(query)
        technicians = cursor.fetchall()

        return technicians

    except Exception as e:
        logger.error(
            f"Database error: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Database error: {e}") from e

    finally:
        cursor.close()
        cnx.close()


def insert_azure_user(
    user_id: str, user_name: str, user_group: str, config: AppConfig
) -> None:
    cnx = connect_to_mysql(config)
    if not cnx:
        logger.error(
            "Database connection failed",
            exc_info=True,
        )
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
        logger.info(
            f"Inserted user {user_name} into database",
        )

    except Exception as e:
        logger.error(
            f"Database error: {e}",
            exc_info=True,
        )
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
        logger.error(
            f"Database error: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Database error: {e}") from e

    finally:
        cursor.close()
        cnx.close()
