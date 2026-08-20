import os
import sqlite3
from pathlib import Path
from email_services import send_welcome_email

"""
How to display in Render's Shell:

sqlite3 /var/data/course_sniper.db
.headers on
.mode column
SELECT * FROM subscriptions;
"""




# ---------------------------------------------------------
# Database configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATABASE_NAME = Path(
    os.environ.get(
        "RU_SATELLITE_DB_PATH",
        str(BASE_DIR / "course_sniper.db"),
    )
)

DATABASE_NAME.parent.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# Database setup
# ---------------------------------------------------------

def create_database():
    """
    Create the subscriptions table if it does not already exist.

    Each email represents one RU Satellite account.
    section_index stores sections still waiting for an alert.
    notified_sections stores sections that already triggered an alert.
    """
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                section_index TEXT NOT NULL DEFAULT '',
                notified_sections TEXT NOT NULL DEFAULT ''
            )
            """
        )

        connection.commit()


# ---------------------------------------------------------
# Subscription helpers
# ---------------------------------------------------------

def get_subscriptions():
    """
    Return every subscription.

    The tuple format stays compatible with coursesniper5.py:

    (
        id,
        email,
        section_index,
        notified_sections
    )
    """
    try:
        with sqlite3.connect(DATABASE_NAME) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    email,
                    section_index,
                    notified_sections
                FROM subscriptions
                ORDER BY id ASC
                """
            )

            return cursor.fetchall()

    except sqlite3.Error as error:
        print(
            "Database error in get_subscriptions(): "
            f"{error}"
        )
        return []


def get_subscription_by_email(email):
    """
    Return the first subscription row matching an email.

    Email matching is case-insensitive.
    """
    email = email.strip().lower()

    try:
        with sqlite3.connect(DATABASE_NAME) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    email,
                    section_index,
                    notified_sections
                FROM subscriptions
                WHERE lower(email) = ?
                ORDER BY id ASC
                LIMIT 1
                """,
                (email,),
            )

            return cursor.fetchone()

    except sqlite3.Error as error:
        print(
            "Database error in "
            "get_subscription_by_email(): "
            f"{error}"
        )
        return None


def email_exists(email):
    """
    Check whether an RU Satellite account already exists.
    """
    return get_subscription_by_email(email) is not None


def add_subscription(
    email,
    section_index,
    notified_sections="",
):
    """
    Add a new subscription.

    If the email already exists, update the existing account
    instead of creating another duplicate row.
    """
    email = email.strip().lower()

    try:
        existing = get_subscription_by_email(email)

        if existing:
            edit_subscription(
                email,
                section_index,
                notified_sections,
            )
            return True

        with sqlite3.connect(DATABASE_NAME) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO subscriptions (
                    email,
                    section_index,
                    notified_sections
                )
                VALUES (?, ?, ?)
                """,
                (
                    email,
                    section_index,
                    notified_sections,
                ),
            )

            connection.commit()

        print(f"{email} added to RU Satellite.")
        # welcome email function here 
        send_welcome_email(email)
        return True

    except sqlite3.Error as error:
        print(
            "Database error in add_subscription(): "
            f"{error}"
        )
        return False


def edit_subscription(
    email,
    section_index,
    notified_sections,
):
    """
    Update the watched and notified sections for an email.

    This function keeps the same argument order expected by
    coursesniper5.py.
    """
    email = email.strip().lower()

    try:
        with sqlite3.connect(DATABASE_NAME) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE subscriptions
                SET
                    section_index = ?,
                    notified_sections = ?
                WHERE lower(email) = ?
                """,
                (
                    section_index,
                    notified_sections,
                    email,
                ),
            )

            connection.commit()

            return cursor.rowcount > 0

    except sqlite3.Error as error:
        print(
            "Database error in edit_subscription(): "
            f"{error}"
        )
        return False


def delete_subscription(email):
    """
    Delete an RU Satellite account completely.
    """
    email = email.strip().lower()

    try:
        with sqlite3.connect(DATABASE_NAME) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM subscriptions
                WHERE lower(email) = ?
                """,
                (email,),
            )

            connection.commit()

            return cursor.rowcount > 0

    except sqlite3.Error as error:
        print(
            "Database error in delete_subscription(): "
            f"{error}"
        )
        return False


def remove_duplicate_emails():
    """
    Clean up duplicate rows created by older versions of
    the Course Sniper website.

    Sections from duplicate rows are merged so watchlist data
    is not lost.
    """
    subscriptions = get_subscriptions()

    accounts = {}

    for subscription in subscriptions:
        subscription_id = subscription[0]
        email = subscription[1].strip().lower()

        waiting = [
            section.strip()
            for section in subscription[2].split(",")
            if section.strip()
        ]

        notified = [
            section.strip()
            for section in subscription[3].split(",")
            if section.strip()
        ]

        if email not in accounts:
            accounts[email] = {
                "primary_id": subscription_id,
                "waiting": [],
                "notified": [],
                "duplicate_ids": [],
            }
        else:
            accounts[email]["duplicate_ids"].append(
                subscription_id
            )

        accounts[email]["waiting"].extend(waiting)
        accounts[email]["notified"].extend(notified)

    try:
        with sqlite3.connect(DATABASE_NAME) as connection:
            cursor = connection.cursor()

            for email, account in accounts.items():
                waiting = list(
                    dict.fromkeys(account["waiting"])
                )

                notified = list(
                    dict.fromkeys(account["notified"])
                )

                # Notified wins if old data has a section
                # stored in both states.
                waiting = [
                    section
                    for section in waiting
                    if section not in notified
                ]

                cursor.execute(
                    """
                    UPDATE subscriptions
                    SET
                        email = ?,
                        section_index = ?,
                        notified_sections = ?
                    WHERE id = ?
                    """,
                    (
                        email,
                        ", ".join(waiting),
                        ", ".join(notified),
                        account["primary_id"],
                    ),
                )

                for duplicate_id in account[
                    "duplicate_ids"
                ]:
                    cursor.execute(
                        """
                        DELETE FROM subscriptions
                        WHERE id = ?
                        """,
                        (duplicate_id,),
                    )

            connection.commit()

        return True

    except sqlite3.Error as error:
        print(
            "Database error in "
            "remove_duplicate_emails(): "
            f"{error}"
        )
        return False


# ---------------------------------------------------------
# Run directly
# ---------------------------------------------------------

if __name__ == "__main__":
    create_database()
    remove_duplicate_emails()
    print("RU Satellite database is ready.")
