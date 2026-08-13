
import sqlite3

COURSE_DATABASE = "course_data.db"

def find_section(section_index: str):

    section_index = section_index.strip()

    try:
        with sqlite3.connect(
            COURSE_DATABASE
        ) as connection:

            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    registration_index,
                    course_code,
                    course_title,
                    instructors
                FROM course_sections
                WHERE registration_index = ?
            """, (
                section_index,
            ))

            section = cursor.fetchone()

            return {
                "course_code": section[1],
                "course_title": section[2],
                "instructors": section[3]
                }

    except sqlite3.Error:
        print(f"Error accessing the database: {sqlite3.Error}")
        return {
            "course_code": "None",
            "course_title": "None",
            "instructors": "None"
        }


