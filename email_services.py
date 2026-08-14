# -----------------
# email_services.py
import os
import smtplib
from datetime import datetime

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from course_data_search import find_section

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

if not SMTP_EMAIL or not SMTP_PASSWORD:
    try:
        from secret_key import SMTP_EMAIL, SMTP_PASSWORD
    except ImportError:
        raise ImportError("We had an issue loading SMTP_EMAIL and SMTP_PASSWORD from secret_key.py")

def send_course_open_email(email: str, section_index: str):

    try:
        section = find_section(section_index)

        course_code = section["course_code"]
        course_title = section["course_title"]
        instructors = section["instructors"]

        time_sent = datetime.now().strftime("%b %d, %Y at %I:%M %p")

        message = MIMEMultipart()

        message["From"] = SMTP_EMAIL
        message["To"] = email
        message["Subject"] = f"SECTION OPENING"

        html = f"""
        <h2>🚨 A section has opened! 🚨</h2>
        <p>{course_title} ({course_code})</p>
        <p>Section Index: {section_index}</p>
        <p>REGISTER HERE: https://sims.rutgers.edu/webreg/editSchedule.htm?login=cas&semesterSelection=92026&indexList={section_index} </p>
        <p>Time sent: {time_sent}</p>
        <hr>
        <p>If it closes, we'll notifiy you again when it opens.</p>
        <p>🛰️Thank you for using RU Satellite!🛰️</p>
        """

        message.attach(MIMEText(html, "html"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)

        server.sendmail(
            SMTP_EMAIL,
            email,
            message.as_string()
        )

        server.quit()


    except Exception as error:
        print(f"Failed to send email to {email}: {error}")


if __name__ == "__main__": # test script
    from secret_key import SMTP_EMAIL, SMTP_PASSWORD
    send_course_open_email("johnanddd2007@gmail.com", "17387")
    print("Email sent!")


