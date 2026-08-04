## -----------------
# email_services.py


import os
import requests
import time
import sqlite3
import random


os.system("cls")


# This function pings the CSP API and returns the JSON file
# for all the classes in a specific subject.
def get_csp_info(subject_number, params, session):

    params["subject"] = subject_number

    try:
        response = session.post(
            "https://sims.rutgers.edu/csp/sectionsLookup.json",
            params=params,
            timeout=30
        )

        print(f"Server returned status: {response.status_code}")

        if response.status_code != 200:
            print(
                f"ERROR: Rutgers returned status "
                f"{response.status_code}."
            )
            return None

        try:
            return response.json()

        except ValueError:
            print("ERROR: Failed to get JSON response.")
            return None

    except requests.RequestException as error:
        print(
            f"ERROR: An error occurred while making "
            f"the request: {error}"
        )
        return None


# This function takes the messy JSON and stores
# organized information for each section.
def retrieve_section_data(
    section_info_storage,
    json_data,
    counted_sections
):

    course_offerings = json_data.get(
        "courseOfferings",
        []
    )

    for course in course_offerings:

        course_title = course.get(
            "fullTitle",
            "Unknown Course"
        )

        offering_unit = course.get(
            "offeringUnit",
            {}
        )

        course_data = course.get(
            "course",
            {}
        )

        course_school = offering_unit.get(
            "code",
            "N/A"
        )

        course_subject = course_data.get(
            "subject",
            "N/A"
        )

        course_number = course_data.get(
            "number",
            "N/A"
        )

        course_id = (
            f"{course_school}:"
            f"{course_subject}:"
            f"{course_number}"
        )

        for section in course.get("sections", []):

            section_id = section.get(
                "registrationIndex"
            )

            # Skip sections that do not have a registration index.
            if not section_id:
                continue

            counted_sections += 1

            instructors_data = section.get(
                "instructors",
                []
            )

            instructor_names = []

            for instructor in instructors_data:

                instructor_name = instructor.get(
                    "name"
                )

                if instructor_name:
                    instructor_names.append(
                        instructor_name
                    )

            if len(instructor_names) == 0:
                section_instructors = "N/A"

            elif len(instructor_names) == 1:
                section_instructors = (
                    instructor_names[0]
                )

            else:
                section_instructors = (
                    instructor_names
                )

            section_info = {
                "Course Code": course_id,
                "Course Title": course_title,
                "Instructor(s)": section_instructors
            }

            section_info_storage[
                section_id
            ] = section_info

    print(f"Counted Sections: {counted_sections}")

    return section_info_storage, counted_sections


# Deletes the old database table and creates a fresh one.
def initialize_course_database():

    with sqlite3.connect(
        "course_data.db"
    ) as connection:

        cursor = connection.cursor()

        cursor.execute("""
            DROP TABLE IF EXISTS course_sections
        """)

        cursor.execute("""
            CREATE TABLE course_sections (
                registration_index TEXT PRIMARY KEY,
                course_code TEXT NOT NULL,
                course_title TEXT NOT NULL,
                instructors TEXT NOT NULL
            )
        """)

        connection.commit()

    print("-----------------------------------")
    print("Fresh course database created.")
    print("-----------------------------------")


# Saves one subject's section data immediately.
def save_subject_data(subject_section_data):

    with sqlite3.connect(
        "course_data.db"
    ) as connection:

        cursor = connection.cursor()

        for section_id, section_info in (
            subject_section_data.items()
        ):

            instructors = section_info[
                "Instructor(s)"
            ]

            if isinstance(instructors, list):
                instructors = ", ".join(
                    instructors
                )

            cursor.execute("""
                INSERT INTO course_sections (
                    registration_index,
                    course_code,
                    course_title,
                    instructors
                )
                VALUES (?, ?, ?, ?)

                ON CONFLICT(registration_index)
                DO UPDATE SET
                    course_code = excluded.course_code,
                    course_title = excluded.course_title,
                    instructors = excluded.instructors
            """, (
                section_id,
                section_info["Course Code"],
                section_info["Course Title"],
                instructors
            ))

        connection.commit()

    print(
        f"Saved {len(subject_section_data)} "
        f"sections to course_data.db."
    )


# Lets you test section lookups using the SQLite database.
def display_section_info(section_entered):

    with sqlite3.connect(
        "course_data.db"
    ) as connection:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                course_code,
                course_title,
                instructors
            FROM course_sections
            WHERE registration_index = ?
        """, (
            section_entered,
        ))

        section = cursor.fetchone()

    if section is None:
        print("That section was not found.")
        return

    course_code, course_title, instructors = section

    print(f"Course Code: {course_code}")
    print(f"Course Title: {course_title}")
    print(f"Instructor(s): {instructors}")


def main():

    cookies = {
        "JSESSIONID":
            "6CC886CAF822C780290965CB79B5BBB9.jvm1-tc8",
        "_ga_M6FS8HG1PG":
            "GS2.1.s1757883469$o3$g0$t1757883469$j60$l0$h0",
        "fpestid":
            "OC6tK_zDxxEZIdtYl-8oeVMqSdk4BZQdThYT5669FOV8efFVSuPRAhnaNDw4J4kgvWKL8Q",
        "_cc_id":
            "958a5c11523365b95ebbb93f248d528a",
        "_gcl_au":
            "1.1.1265539514.1779414837",
        "_ga_287D0ZK0WR":
            "GS2.2.s1780851491$o1$g1$t1780853707$j60$l0$h0",
        "_ga":
            "GA1.1.722274748.1755291756",
        "_clck":
            "gfq8ue%5E2%5Eg7t%5E0%5E2333",
        "_ga_36BMR3ZE98":
            "GS2.1.s1784322840$o3$g1$t1784323047$j60$l0$h0",
        "_ga_EVHZ2DN4EF":
            "GS2.1.s1784322840$o3$g1$t1784323047$j60$l0$h0",
        "EssUserTrk":
            "24c3332b.656ecbe45673d",
        "sims-webreg":
            "1156324780.20480.0000",
        "_ga_VGJS06GBF3":
            "GS2.1.s1784508504$o1$g0$t1784508504$j60$l0$h0",
        "sims-csp":
            "1156324780.20480.0000",
    }

    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type":
            "application/x-www-form-urlencoded",

        "Origin":
            "https://sims.rutgers.edu",

        "Referer": (
            "https://sims.rutgers.edu/csp/"
            "builder.htm?semester=92026"
        ),

        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",

        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),

        "X-Requested-With":
            "XMLHttpRequest",

        "sec-ch-ua-mobile":
            "?0",

        "sec-ch-ua-platform":
            "\"Windows\"",
    }

    params = {
        "semester": "92026",
        "campus": "NB",
        "levelOfStudy": "U",
        "subject": "",
    }

    subject_numbers = [
        "010", "011", "013", "014", "015",
        "016", "019", "020", "035", "047",
        "050", "067", "070", "074", "078",
        "080", "081", "082", "090", "098",
        "115", "117", "119", "122", "125",
        "126", "136", "140", "146", "155",
        "158", "160", "165", "170", "175",
        "180", "185", "190", "192", "193",
        "195", "198", "202", "203", "206",
        "207", "216", "219", "220", "300",
        "351", "354", "355", "356", "358",
        "359", "364", "370", "373", "374",
        "375", "377", "381", "382", "390",
        "400", "420", "440", "447", "450",
        "460", "470", "489", "490", "501",
        "505", "506", "508", "510", "512",
        "522", "533", "540", "547", "550",
        "554", "556", "557", "558", "560",
        "563", "565", "567", "574", "575",
        "580", "590", "595", "607", "615",
        "620", "624", "628", "630", "635",
        "640", "650", "652", "660", "667",
        "670", "680", "685", "691", "694",
        "700", "701", "705", "709", "713",
        "715", "718", "720", "721", "723",
        "725", "730", "745", "750", "775",
        "776", "787", "790", "810", "830",
        "832", "833", "840", "843", "851",
        "860", "888", "902", "904", "910",
        "920", "940", "955", "959", "960",
        "965", "966", "971", "973", "988",
        "991"
    ]

    session = requests.Session()
    session.headers.update(headers)
    session.cookies.update(cookies)

    counted_sections = 0

    # Reset the database once before downloading subjects.
    initialize_course_database()

    for position, subject_number in enumerate(
        subject_numbers
    ):

        print("-----------------------------------")
        print(
            f"Loading subject {subject_number} "
            f"({position + 1}/{len(subject_numbers)})"
        )

        json_data = get_csp_info(
            subject_number,
            params,
            session
        )

        if json_data is not None:

            # This dictionary contains only the
            # current subject's sections.
            subject_section_data = {}

            (
                subject_section_data,
                counted_sections
            ) = retrieve_section_data(
                subject_section_data,
                json_data,
                counted_sections
            )

            # Save this subject immediately.
            save_subject_data(
                subject_section_data
            )

            print(
                f"Subject {subject_number} "
                f"successfully saved."
            )

        else:
            print(
                f"Subject {subject_number} failed."
            )

        if position < len(subject_numbers) - 1:
            sleep_time = random.uniform(9,11)
            print(f"Waiting {sleep_time} seconds...")
            time.sleep(sleep_time)

    session.close()

    print("-----------------------------------")
    print(
        f"Finished downloading "
        f"{counted_sections} sections."
    )
    print("-----------------------------------")

    # Optional database testing loop.
    while True:

        section_entered = input(
            "Enter a section index, or type end: "
        ).strip()

        if section_entered.lower() == "end":
            break

        display_section_info(
            section_entered
        )


if __name__ == "__main__":
    main()