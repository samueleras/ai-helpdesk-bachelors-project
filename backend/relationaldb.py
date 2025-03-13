import logging
import json
import os
from typing import List
import mysql.connector
from mysql.connector import errorcode
from custom_types import AppConfig, Technician, Ticket, TicketList, TicketMessage
from ai_system.vectordb import (
    remove_ticket_milvus,
    retrieve_similar_tickets_milvus,
    store_ticket_milvus,
)
from backend.pydantic_models import NewTicketMessage, TicketAssignee, TicketFilter, User

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

    if not cnx:
        logger.error(
            "Database connection failed",
            exc_info=True,
        )
        raise RuntimeError("Database connection failed") from e

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

    if not cnx:
        logger.error(
            "Database connection failed",
            exc_info=True,
        )
        raise RuntimeError("Database connection failed") from e

    try:
        cursor = cnx.cursor(dictionary=True)

        query = "SELECT m.message, u.user_name as author_name, u.user_group as `group`, m.created_at FROM ticket_messages m INNER JOIN azure_users u ON m.author_id = u.user_id WHERE ticket_id = %s ORDER BY created_at ASC"
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

    if not cnx:
        logger.error(
            "Database connection failed",
            exc_info=True,
        )
        raise RuntimeError("Database connection failed") from e

    try:
        cursor = cnx.cursor(dictionary=True)

        query = "SELECT ticket_id, title, content, summary_vector, creation_date, closed_date, u.user_name as author_name, a.user_name as assignee_name FROM tickets t INNER JOIN azure_users u ON t.author_id = u.user_ID LEFT JOIN azure_users a on t.assignee_id = a.user_id WHERE ticket_id = %s"
        cursor.execute(query, (ticket_id,))
        ticket = cursor.fetchone()

        ticket["similar_tickets"] = []
        if "summary_vector" in ticket and user.group == "technicians":
            # Convert JSON string back to vector list
            summary_vector = json.loads(ticket["summary_vector"])
            similar_tickets = retrieve_similar_tickets_milvus(
                summary_vector, ticket["ticket_id"]
            )
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


def insert_ticket_message(
    new_ticket_message: NewTicketMessage, user: User, config: AppConfig
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
        query = "INSERT INTO ticket_messages (ticket_id, author_id, message, created_at) VALUES (%s, %s, %s, %s)"
        values = (
            new_ticket_message.ticket_id,
            user.user_id,
            new_ticket_message.message,
            new_ticket_message.created_at,
        )
        cursor.execute(query, values)
        cnx.commit()
        logger.info(
            f"Ticket {new_ticket_message.ticket_id}: Added new Ticket Message of user {user.user_name} into database",
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


def close_ticket(ticket_id: int, config: AppConfig) -> None:
    cnx = connect_to_mysql(config)

    if not cnx:
        logger.error(
            "Database connection failed",
            exc_info=True,
        )
        raise RuntimeError("Database connection failed") from e

    cursor = cnx.cursor(dictionary=True)

    try:
        query = "UPDATE tickets SET closed_date = NOW() WHERE ticket_id = (%s);"
        cursor.execute(query, (ticket_id,))
        cnx.commit()
        logger.info(
            f"Ticket {ticket_id}: Closed.",
        )

        query = "SELECT ticket_id, title, summary_vector FROM tickets t INNER JOIN azure_users u ON t.author_id = u.user_ID LEFT JOIN azure_users a on t.assignee_id = a.user_id WHERE ticket_id = %s"
        cursor.execute(query, (ticket_id,))
        ticket = cursor.fetchone()

        if "summary_vector" in ticket:
            summary_vector = json.loads(ticket["summary_vector"])
            store_ticket_milvus(ticket["ticket_id"], summary_vector, ticket["title"])

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


def reopen_ticket(ticket_id: int, config: AppConfig) -> None:
    cnx = connect_to_mysql(config)

    if not cnx:
        logger.error(
            "Database connection failed",
            exc_info=True,
        )
        raise RuntimeError("Database connection failed") from e

    cursor = cnx.cursor()

    try:
        query = "UPDATE tickets SET closed_date = NULL WHERE ticket_id = (%s);"
        values = (ticket_id,)
        cursor.execute(query, values)
        cnx.commit()
        logger.info(
            f"Ticket {ticket_id}: Reopened.",
        )
        remove_ticket_milvus(ticket_id=ticket_id)

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


def get_filtered_tickets(filter_data: TicketFilter, config: AppConfig) -> TicketList:
    cnx = connect_to_mysql(config)

    if not cnx:
        logger.error(
            "Database connection failed",
            exc_info=True,
        )
        raise RuntimeError("Database connection failed") from e

    try:
        cursor = cnx.cursor(dictionary=True)

        query = "SELECT ticket_id, title, content, creation_date, closed_date, u.user_name as author_name, a.user_name as assignee_name FROM tickets t INNER JOIN azure_users u ON t.author_id = u.user_ID LEFT JOIN azure_users a on t.assignee_id = a.user_id WHERE 1=1"

        params = ()

        if filter_data.search is not None:
            query += " AND (title LIKE %s)"
            search_term = f"%{filter_data.search}%"
            params += (search_term,)
        else:
            if filter_data.assignee_id is not None:
                if filter_data.assignee_id == "unassigned":
                    query += " AND (assignee_id is NULL)"
                else:
                    query += " AND (assignee_id = %s)"
                    params += (filter_data.assignee_id,)

            if filter_data.closed is not None:
                if filter_data.closed == True:
                    query += " AND (closed_date is not NULL)"
                if filter_data.closed == False:
                    query += " AND (closed_date is NULL)"

        if filter_data.order is not None:
            if filter_data.closed == "asc":
                query += " ORDER BY creation_date ASC"
        else:
            query += " ORDER BY creation_date DESC"

        if filter_data.page_size is not None and filter_data.page is not None:
            query += " LIMIT %s"
            params += (filter_data.page_size,)
            query += " OFFSET %s"
            params += ((filter_data.page - 1) * filter_data.page_size,)

        cursor.execute(query, params)
        tickets = cursor.fetchall()

        for ticket in tickets:
            ticket["similar_tickets"] = []
            ticket["ticket_messages"] = []

        query = "SELECT COUNT(t.ticket_id) as count FROM tickets t INNER JOIN azure_users u ON t.author_id = u.user_ID LEFT JOIN azure_users a on t.assignee_id = a.user_id WHERE 1=1"

        params = ()
        if filter_data.search is not None:
            query += " AND (title LIKE %s)"
            search_term = f"%{filter_data.search}%"
            params += (search_term,)
        else:
            if filter_data.assignee_id is not None:
                if filter_data.assignee_id == "unassigned":
                    query += " AND (assignee_id is NULL)"
                else:
                    query += " AND (assignee_id = %s)"
                    params += (filter_data.assignee_id,)

            if filter_data.closed is not None:
                if filter_data.closed == True:
                    query += " AND (closed_date is not NULL)"
                if filter_data.closed == False:
                    query += " AND (closed_date is NULL)"

        if filter_data.order is not None:
            if filter_data.closed == "asc":
                query += " ORDER BY creation_date ASC"
        else:
            query += " ORDER BY creation_date DESC"

        cursor.execute(query, params)
        ticketcount = cursor.fetchone()

        return {"count": ticketcount["count"], "tickets": tickets}

    except Exception as e:
        logger.error(
            f"Database error: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Database error: {e}") from e

    finally:
        cursor.close()
        cnx.close()


def get_user_tickets(
    user: User, filter_data: TicketFilter, config: AppConfig
) -> TicketList:
    cnx = connect_to_mysql(config)

    if not cnx:
        logger.error(
            "Database connection failed",
            exc_info=True,
        )
        raise RuntimeError("Database connection failed") from e

    try:
        cursor = cnx.cursor(dictionary=True)

        query = "SELECT ticket_id, title, content, creation_date, closed_date, u.user_name as author_name, a.user_name as assignee_name FROM tickets t INNER JOIN azure_users u ON t.author_id = u.user_ID LEFT JOIN azure_users a on t.assignee_id = a.user_id WHERE t.author_id = %s ORDER BY creation_date DESC"
        params = (user.user_id,)

        if filter_data.page_size is not None and filter_data.page is not None:
            query += " LIMIT %s"
            params += (filter_data.page_size,)
            query += " OFFSET %s"
            params += ((filter_data.page - 1) * filter_data.page_size,)

        cursor.execute(query, params)
        tickets = cursor.fetchall()

        for ticket in tickets:
            ticket["similar_tickets"] = []
            ticket["ticket_messages"] = []

        query = "SELECT COUNT(t.ticket_id) as count FROM tickets t INNER JOIN azure_users u ON t.author_id = u.user_ID LEFT JOIN azure_users a on t.assignee_id = a.user_id WHERE t.author_id = %s"

        cursor.execute(query, (user.user_id,))
        ticketcount = cursor.fetchone()

        return {"count": ticketcount["count"], "tickets": tickets}

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

    if not cnx:
        logger.error(
            "Database connection failed",
            exc_info=True,
        )
        raise RuntimeError("Database connection failed") from e

    try:
        cursor = cnx.cursor(dictionary=True)

        query = "SELECT user_id, user_name FROM azure_users WHERE user_group = 'technicians'"
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


def assign_ticket(ticket: TicketAssignee, config: AppConfig) -> None:
    cnx = connect_to_mysql(config)

    if not cnx:
        logger.error(
            "Database connection failed",
            exc_info=True,
        )
        raise RuntimeError("Database connection failed") from e

    cursor = cnx.cursor()

    try:
        print(ticket.assignee_id, ticket.ticket_id)
        if ticket.assignee_id == "Unassigned":
            ticket.assignee_id = None
        query = "UPDATE tickets SET assignee_id = (%s) WHERE ticket_id = (%s);"
        cursor.execute(query, (ticket.assignee_id, ticket.ticket_id))
        cnx.commit()
        logger.info(
            f"Ticket {ticket.ticket_id}: Assigned to {ticket.assignee_id}.",
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
        logger.error(
            "Database connection failed",
            exc_info=True,
        )
        raise RuntimeError("Database connection failed") from e

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
