# -----------------
# coursesniper5.py

import os
os.system('cls')

import requests
import time
import random
from datetime import datetime
from pathlib import Path
from database import create_database, get_subscriptions, edit_subscription
from email_services import send_course_open_email


def print_divider():
    print(f"---------------------------------------------")

def print_intro(subscriptions):
    os.system('cls')  # Clear the console for a clean start of the monitoring process
    print_divider()

    file_name = os.path.basename(__file__)

    print(f"[SYSTEM]: Starting {file_name}...\n")
    print(f"Number of accounts: {len(subscriptions)}")
    
    print_divider()    
    time.sleep(2)

def get_all_open_sections(session, api_ping_count, params):
    response_status = None
    response_time = 0
    api_ping_count += 1
    try:
        api_start_time = time.perf_counter()

        # The URL from your curlconverter output
        response = session.post('https://classes.rutgers.edu/soc/api/openSections.json', params=params) # takes around 0.4s
        response_status = response.status_code

        api_end_time = time.perf_counter()
        response_time = api_end_time - api_start_time


        if False:  # Set to True if you want to print the server status for debugging
            print(f"Server returned status: {response_status}")

        if response_status == 200:
            all_open_sections_data = response.json()
            response.close()
            return all_open_sections_data, api_ping_count, response_status, response_time
        else:
            api_end_time = time.perf_counter()
            response_time = api_end_time - api_start_time
            return None, api_ping_count, response_status, response_time
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None, api_ping_count, response_status, response_time  # Exit the function on exception to avoid further processing


def check_sections_for_accounts(all_open_sections_data, subscriptions):
    start_time = time.perf_counter()

    # Rutgers API values should be strings for easy comparison
    all_open_sections = {
        str(section)
        for section in all_open_sections_data
    }

    for account in subscriptions:
        email = account[1]

        # Convert database strings into Python lists
        sections_entered = [
            section.strip()
            for section in account[2].split(",")
            if section.strip()
        ]

        already_notified_sections = [
            section.strip()
            for section in account[3].split(",")
            if section.strip()
        ]

        print(f"EMAIL: {email}")
        print(f"SECTIONS ENTERED: {sections_entered}")
        print(f"SECTIONS NOTIFIED: {already_notified_sections}")

        # Sections waiting for an alert that are open now
        newly_open_sections = [
            section
            for section in sections_entered
            if section in all_open_sections
        ]

        # Sections already notified that have now closed
        newly_closed_sections = [
            section
            for section in already_notified_sections
            if section not in all_open_sections
        ]

        # Move newly opened sections into notified_sections
        for section in newly_open_sections:
            print(f"OPEN SECTION: {section}")
            print(f"Notifying {email}!")

            try:
                sections_entered.remove(section)
                already_notified_sections.append(section)
                send_course_open_email(email, section)
                print(f"Email sent for section {section}.")
            except Exception as error:
                print(
                    f"Failed to email {email} "
                    f"about section {section}: {error}"
                )

        # Move newly closed sections back into sections_entered
        for section in newly_closed_sections:
            already_notified_sections.remove(section)

            if section not in sections_entered:
                sections_entered.append(section)

            print(f"Section {section} closed again. Alert reset.")


        # Only update the database if a section actually opened or closed
        if newly_open_sections or newly_closed_sections:

            sections_entered_text = ", ".join(
                sections_entered
            )

            notified_sections_text = ", ".join(
                already_notified_sections
            )

            edit_subscription(
                email,
                sections_entered_text,
                notified_sections_text,
                )

        if not newly_open_sections:
            print("OPEN SECTIONS: None")

        print_divider()

    end_time = time.perf_counter()
    return end_time - start_time

def get_and_check_accounts(accounts_entered):
    
    for user in accounts_entered:
        sections = user.sections
        
        valid_sections = []
        for user_input in sections:
            user_input = str(user_input)
            user_input = user_input.strip()  # Remove leading/trailing whitespace
            user_input = user_input.replace("(", "").replace(")", "").replace(" ", "").replace('"', "")  # Remove parentheses, spaces, and quotes

            # Checks to make sure what you entered is valid
            if len(user_input) == 5 and user_input.isdigit():
                valid_sections.append(user_input)
            else:
                print(f"Skipping invalid input '{user_input}' for user {user.username}")
        
        user.sections = valid_sections

    return accounts_entered


def calculate_wait_time(default_sleep):
    current_hour = datetime.now().hour
    random_jitter = random.uniform(0, 0.25)

    if 2 <= current_hour < 6:
        multiplier = 1.5 + random_jitter
    elif 6 <= current_hour < 10:
        multiplier = 1.25 + random_jitter
    elif 10 <= current_hour < 22:
        multiplier = 1 + random_jitter
    else:
        multiplier = 1.25 + random_jitter


    return (default_sleep * multiplier)  # Return the total wait time

def log_event(title, message): # Logs crashes in a text file
    file_name = os.path.basename(__file__)
    base_dir = Path(__file__).resolve().parent
    log_file = base_dir / "LOGS.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # lowkey confused wth this is
    
    with open(log_file, "a") as file:
        file.write(f"AUTOMATIC LOG: {title} \nSOURCE: {file_name} \n[{timestamp}]: {message}\n\n")

def sleep_crash_delay():
    retry_time = random.uniform(60, 90)
    print(f"Retrying in {retry_time:.2f} seconds.")
    time.sleep(retry_time)


def start_course_sniper():
    
    #region Random Variables
    params = {
        'year': '2026',
        'term': '9',
        'campus': 'NB',}

    api_ping_count = 0
    response_time = 0
    default_sleep = 5.5  # seconds
    play_sound = False
    run_main_loop = True
    #endregion

    ###############################
    
    session = requests.Session()

    # accounts_entered = get_and_check_accounts(accounts_entered)

    # Run the monitor
    # print_intro(accounts_entered)

    # LOAD DATABASE
    create_database()
    subscriptions = get_subscriptions()

    print_intro(subscriptions)


    while run_main_loop:
        date_time = datetime.now()

        if date_time.hour == 5 and date_time.minute == 30:
            print("Possible Rutgers maintenance window. Waiting until 5:31.")
            time.sleep(60)
            continue

        try:
            subscriptions = get_subscriptions()

            (all_open_sections_data,
                api_ping_count,
                response_status,
                api_response_time,
            ) = get_all_open_sections(session, api_ping_count, params)

        except Exception as error:
            message = f"Unexpected monitor error: {error}"
            print(message)
            log_event("Script Error", message)
            sleep_crash_delay()
            continue

        if response_status != 200:
            crash_message = (
                f"Server returned status {response_status}. "
                "Most likely an API issue."
            )

            log_event("Script Crash", crash_message)
            sleep_crash_delay()
            continue

        check_and_display_time = check_sections_for_accounts(
            all_open_sections_data,
            subscriptions,
        )

        print(f"Total times checked: {api_ping_count}")
        print(f"API request finished in {api_response_time:.6f} seconds.")
        print(f"Accounts checked and displayed in {check_and_display_time:.6f} seconds.")

        wait_time = calculate_wait_time(default_sleep)
        print(f"Waiting for {wait_time:.2f} seconds before the next check.")
        print_divider()
        time.sleep(wait_time)

if __name__ == "__main__":
    start_course_sniper()




