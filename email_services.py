# -----------------
# email_services.py
import resend
import os
RESEND_API_KEY = os.getenv("RESEND_API_KEY")


def send_course_open_email(email: str, section_index: str):

    resend.api_key = RESEND_API_KEY

    if not resend.api_key:
        raise RuntimeError("RESEND_API_KEY is not configured.")

    resend.Emails.send({
    "from": "Rutgers Course Sniper <onboarding@resend.dev>",
    "to": [email],
    "subject": f"Section {section_index} is open!",
    "html": f"""
        <h2>A Rutgers section just opened</h2>
        <p>Section <strong>{section_index}</strong> is currently open.</p>
        <p>Register quickly before the seat is taken.</p>
    """,
    })



if __name__ == "__main__": # test script
    send_course_open_email("johnanddd2007@gmail.com", "08841")
    print("Email sent!")



