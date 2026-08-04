# -----------------
# database.py
import sqlite3

DATABASE_NAME = "course_sniper.db"


def create_database():
    # Open the SQLite database file.
    # If it doesn't exist yet, SQLite will automatically create it.
    connection = sqlite3.connect(DATABASE_NAME)

    # Create a cursor so Python can send SQL commands to SQLite.
    cursor = connection.cursor()

    # Tell SQLite to create a table called "subscriptions"
    # if it does not already exist.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            section_index TEXT NOT NULL,
            notified_sections TEXT NOT NULL
        )
        """
    )

    # Save any changes made to the database.
    connection.commit()

    # Close the database since we're done using it.
    connection.close()


# Only create the database when this file is run directly.
# (Not when another Python file imports it.)
if __name__ == "__main__":
    create_database()


def get_subscriptions():
    try:
        # Open the SQLite database.
        connection = sqlite3.connect(DATABASE_NAME)

        # Create a cursor so we can send SQL commands.
        cursor = connection.cursor()

        # Go to the table named subscriptions and return the id, email, and section_index columns for every row.
        cursor.execute(
            """
            SELECT id, email, section_index, notified_sections
            FROM subscriptions
            """
        )

        # Fetch every row returned by the SQL query and
        # store them as a Python list.
        # Cursor remembers the last thing it fetched. This goes and saves it to a variable
        subscriptions = cursor.fetchall()

        # Close the database since we're finished reading from it.
        connection.close()

        # Return the list of subscriptions to whatever function called us.
        return subscriptions
    except Exception as error:
        print(f"On get_subscriptions() there was an error accessing the SQL Database: {error}")
        return None

def add_subscription(email, section_index, notified_sections=""):
    try:
        connection = sqlite3.connect(DATABASE_NAME)
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
            (email, section_index, notified_sections)
        )

        connection.commit()
        connection.close()

        print(f"{email} added!")
    except Exception as error:
        print(f"On add_subscription() there was an error accessing the SQL Database: {error}")
        return None

def edit_subscription(email, section_index, notified_sections):
    try:
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()

        cursor.execute("""
        UPDATE subscriptions
        SET section_index = ?,
            notified_sections = ?
            WHERE email = ?
        """, (section_index, notified_sections, email)
        )

        connection.commit()
        connection.close()
    except Exception as error:
        print(f"On edit_subscription() there was an error accessing the SQL Database: {error}")
        return None




