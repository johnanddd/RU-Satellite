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

def send_welcome_email(email: str):

    try:
        message = MIMEMultipart()

        message["From"] = f"RU Satellite <{SMTP_EMAIL}>"
        message["To"] = email
        message["Subject"] = "Welcome to RU Satellite! 🛰️"

        html = """
            <h2>Your watchlist is now active! 🛰️</h2>

            <p>Your email has been added to RU Satellite.</p>

            <p>
                Your watchlist is now active in our database, and you'll receive an email here
                whenever one of your monitored sections opens.
            </p>

            <p>
                <a href="https://ru-satellite.onrender.com">
                    Manage your watchlist
                </a>
            </p>

            <p style="font-size: 12px; color: #666;">
                You're receiving this because this email was used to create an RU Satellite watchlist.
            </p>
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

        print(f"Welcome email sent to {email}")

        server.quit()

    except Exception as error:
        print(f"Failed to send thank you email to {email}: {error}")


def send_course_open_email(email: str, section_index: str):

    try:
        section = find_section(section_index)

        course_code = section["course_code"]
        course_title = section["course_title"]
        instructors = section["instructors"]

        time_sent = datetime.now().strftime("%b %d, %Y at %I:%M %p")

        message = MIMEMultipart()

        message["From"] = f"RU Satellite <{SMTP_EMAIL}>"
        message["To"] = email
        message["Subject"] = f"SECTION OPENING: {section_index}"

        html = f"""
            <h2>🚨 Section {section_index} has opened! 🚨</h2>

            <p><strong>{course_title} ({course_code})</strong></p>

            <p>
                <strong>REGISTER HERE:</strong><br>
                <a href="https://sims.rutgers.edu/webreg/editSchedule.htm?login=cas&semesterSelection=92026&indexList={section_index}" target="_blank">
                    https://sims.rutgers.edu/webreg/editSchedule.htm?login=cas&semesterSelection=92026&indexList={section_index}
                </a>

                <br><br>

                <span style="font-size: 12px;">
                    Then click "ADD COURSES."
                </span>
            </p>

            <br><br>

            <div style="font-size: 12px; color: #666;">
                <p>Time sent: {time_sent}</p>

                <p>If the section closes, we'll notify you again when it opens.</p>

                <p>
                    Want to change or remove your monitored sections?<br>
                    <a href="https://ru-satellite.onrender.com">
                        Manage your RU Satellite watchlist
                    </a>
                </p>

                <hr>

                <p>🛰️ Thanks for using RU Satellite! 🛰️</p>
            </div>
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
    target = "johnanddd2007@gmail.com"
    from secret_key import SMTP_EMAIL, SMTP_PASSWORD

    send_welcome_email(target)
    send_course_open_email(target, "17479")
    print("Emails sent!")
    

