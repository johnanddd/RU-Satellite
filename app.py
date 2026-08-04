# -----------------
# app.py
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from database import add_subscription, create_database

# TO START
# python -m uvicorn app:app --reload

app = FastAPI()
create_database()


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>Rutgers Course Sniper</title>

        <!-- 
        below is some CSS to make stuff pretty 
        -->

        <style>
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            body {
                min-height: 100vh;
                font-family: Arial, Helvetica, sans-serif;
                background: #f4f5f7;
                color: #202124;
            }

            header {
                background: #cc0033;
                color: white;
                padding: 18px 24px;
            }

            .header-content {
                max-width: 1000px;
                margin: 0 auto;
            }

            .logo {
                font-size: 24px;
                font-weight: bold;
            }

            main {
                min-height: calc(100vh - 70px);
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 40px 20px;
            }

            .container {
                width: 100%;
                max-width: 520px;
            }

            .card {
                background: white;
                border-radius: 14px;
                padding: 36px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
            }

            h1 {
                font-size: 32px;
                margin-bottom: 12px;
            }

            .subtitle {
                color: #5f6368;
                line-height: 1.5;
                margin-bottom: 30px;
            }

            .form-group {
                margin-bottom: 20px;
            }

            label {
                display: block;
                font-weight: bold;
                margin-bottom: 8px;
            }

            input {
                width: 100%;
                padding: 13px 14px;
                border: 1px solid #c7c9cc;
                border-radius: 8px;
                font-size: 16px;
            }

            input:focus {
                outline: none;
                border-color: #cc0033;
                box-shadow: 0 0 0 3px rgba(204, 0, 51, 0.12);
            }

            button {
                width: 100%;
                border: none;
                border-radius: 8px;
                padding: 14px;
                background: #cc0033;
                color: white;
                font-size: 17px;
                font-weight: bold;
                cursor: pointer;
                transition: background 0.2s ease;
            }

            button:hover {
                background: #a8002a;
            }

            .how-it-works {
                margin-top: 28px;
                padding-top: 24px;
                border-top: 1px solid #e2e4e7;
            }

            .how-it-works h2 {
                font-size: 18px;
                margin-bottom: 12px;
            }

            .how-it-works p {
                color: #5f6368;
                line-height: 1.6;
                margin-bottom: 8px;
            }

            .privacy-note {
                margin-top: 22px;
                font-size: 13px;
                color: #777;
                text-align: center;
                line-height: 1.5;
            }

            @media (max-width: 600px) {
                .card {
                    padding: 26px 22px;
                }

                h1 {
                    font-size: 27px;
                }
            }
        </style>
    </head>

    <body>

        <header>
            <div class="header-content">
                <div class="logo">Rutgers Course Sniper (V1)</div>
            </div>
        </header>

        <main>
            <div class="container">

                <div class="card">

                    <h1>Never miss an open section.</h1>

                    <p class="subtitle">
                        Enter your email and up to five Rutgers section indexes.
                        We'll notify you when any section opens.
                    </p>

                    <!--
                    ## The piece that sends off the email & section data to "/subscribe"
                    -->
                    
                    <form action="/subscribe" method="post">

                        <div class="form-group">
                            <label for="email">Email address</label>

                            <input
                                type="email"
                                id="email"
                                name="email"
                                placeholder="you@example.com"
                                required
                            >
                        </div>

                        <div class="form-group">
                            <label for="section_index">
                                Section indexes (maximum 5)
                            </label>

                            <input
                                type="text"
                                id="section_index"
                                name="section_index"
                                placeholder="Example: 17704, 17713, 29649"
                                required
                            >
                        </div>

                        <button type="submit">
                            Notify Me
                        </button>

                    </form>

                    <div class="how-it-works">

                        <h2>How it works</h2>

                        <p>
                            1. Enter the index numbers shown in the Rutgers
                            Schedule of Classes.
                        </p>

                        <p>
                            2. Our system continuously checks whether the
                            section is open.
                        </p>

                        <p>
                            3. You receive an email when a seat becomes
                            available.
                        </p>

                    </div>

                    <p class="privacy-note">
                        No account or password required.
                        Your email is only used for course-opening alerts.
                    </p>

                </div>

            </div>
        </main>

    </body>

    </html>
    """


@app.post("/subscribe", response_class=HTMLResponse)
def subscribe(
    email: str = Form(...),
    section_index: str = Form(...)
):
    
    # Split comma-separated indexes
    sections = [
        section.strip()
        for section in section_index.split(",")
        if section.strip()
    ]

    # Maximum of 3 sections
    if len(sections) > 5:
        return """
        <h1>Too many section indexes.</h1>
        <p>Please enter a maximum of 5 section indexes.</p>
        <a href="/">Go Back</a>
        """

    # Ensure every index is numeric
    for section in sections:
        if not section.isdigit():
            return f"""
            <h1>Invalid section index</h1>

            <p>
                "{section}" is not a valid Rutgers section index.
            </p>

            <a href="/">Go Back</a>
            """

    formatted_sections = ", ".join(sections)
    email = email.strip().lower()

    add_subscription(email, formatted_sections)

    return f"""
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <title>Subscription Created</title>

        <style>

            body {{
                min-height: 100vh;
                margin: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: Arial, Helvetica, sans-serif;
                background: #f4f5f7;
                color: #202124;
            }}

            .card {{
                width: 90%;
                max-width: 500px;
                background: white;
                padding: 36px;
                border-radius: 14px;
                text-align: center;
                box-shadow: 0 8px 30px rgba(0,0,0,0.08);
            }}

            h1 {{
                color: #cc0033;
            }}

            p {{
                line-height: 1.6;
                color: #5f6368;
            }}

            a {{
                display: inline-block;
                margin-top: 20px;
                color: #cc0033;
                font-weight: bold;
                text-decoration: none;
            }}

        </style>

    </head>

    <body>

        <div class="card">

            <h1>You're on the watchlist.</h1>

            <p>

                We will notify

                <strong>{email}</strong>

                when any of these sections open:

            </p>

            <p>

                <strong>{formatted_sections}</strong>

            </p>

            <a href="/">Watch more sections</a>

        </div>

    </body>

    </html>
    """



