# -----------------
# app.py

import html
import os
import sqlite3
from time import sleep

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse

from database import add_subscription, create_database

from threading import Thread
from coursesniper5 import start_course_sniper


# TO START:
# python -m uvicorn app2:app --reload



app = FastAPI()
create_database()

# makes it so app2 also runs coursesniper5.py in the background when the server starts
def startup():
    Thread(target=start_course_sniper, daemon=True).start()

startup()


COURSE_DATABASE = "course_data.db"


BASE_STYLES = """
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
        justify-content: center;
        padding: 45px 20px;
    }

    .container {
        width: 100%;
        max-width: 620px;
    }

    .card {
        background: white;
        border-radius: 16px;
        padding: 36px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    }

    h1 {
        font-size: 31px;
        margin-bottom: 12px;
    }

    h2 {
        font-size: 20px;
        margin-bottom: 12px;
    }

    .subtitle {
        color: #5f6368;
        line-height: 1.5;
        margin-bottom: 28px;
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
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: background 0.2s ease;
    }

    button:hover {
        background: #a8002a;
    }

    button:disabled {
        background: #aaa;
        cursor: not-allowed;
    }

    .secondary-button {
        background: #eceff1;
        color: #202124;
        margin-top: 10px;
    }

    .secondary-button:hover {
        background: #dfe3e6;
    }

    .checkbox-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 20px 0;
    }

    .checkbox-row input {
        width: auto;
    }

    .checkbox-row label {
        margin: 0;
        font-weight: normal;
    }

    .section-search {
        display: grid;
        grid-template-columns: 1fr 150px;
        gap: 10px;
        margin-bottom: 20px;
    }

    .section-search button {
        height: 48px;
    }

    .course-result,
    .watchlist-item {
        border: 1px solid #dedfe2;
        border-radius: 12px;
        padding: 18px;
        margin-top: 16px;
        background: #fafafa;
    }

    .course-title {
        font-size: 19px;
        font-weight: bold;
        margin-bottom: 6px;
    }

    .course-code {
        color: #cc0033;
        font-weight: bold;
        margin-bottom: 12px;
    }

    .course-detail {
        color: #5f6368;
        margin-top: 6px;
        line-height: 1.4;
    }

    .watchlist {
        margin-top: 30px;
    }

    .watchlist-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .watch-count {
        color: #5f6368;
        font-size: 14px;
    }

    .remove-button {
        width: auto;
        padding: 8px 12px;
        margin-top: 14px;
        background: #eceff1;
        color: #a8002a;
        font-size: 14px;
    }

    .remove-button:hover {
        background: #e1e4e7;
    }

    .message {
        display: none;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 16px;
        line-height: 1.4;
    }

    .error-message {
        background: #fff0f2;
        color: #9b0027;
        border: 1px solid #f0c5d0;
    }

    .success-message {
        background: #edf8f0;
        color: #236533;
        border: 1px solid #bedfc6;
    }

    .email-display {
        padding: 12px 14px;
        background: #f4f5f7;
        border-radius: 8px;
        margin-bottom: 24px;
    }

    .privacy-note {
        margin-top: 22px;
        font-size: 13px;
        color: #777;
        text-align: center;
        line-height: 1.5;
    }

    .hidden {
        display: none;
    }

    .submit-area {
        margin-top: 28px;
    }

    a {
        color: #cc0033;
        font-weight: bold;
        text-decoration: none;
    }

    @media (max-width: 600px) {
        .card {
            padding: 26px 22px;
        }

        h1 {
            font-size: 27px;
        }

        .section-search {
            grid-template-columns: 1fr;
        }
    }
</style>
"""


def page_template(content: str, title: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>{html.escape(title)}</title>

        {BASE_STYLES}
    </head>

    <body>

        <header>
            <div class="header-content">
                <div class="logo">
                    Rutgers Course Sniper
                </div>
            </div>
        </header>

        <main>
            <div class="container">
                {content}
            </div>
        </main>

    </body>

    </html>
    """


@app.get("/", response_class=HTMLResponse)
def home():

    content = """
    <div class="card">

        <h1>Never miss an open section.</h1>

        <p class="subtitle">
            Enter your email to begin tracking Rutgers course sections.
            We'll notify you when a seat becomes available.
        </p>

        <form action="/courses" method="post">

            <div class="form-group">
                <label for="email">
                    Email address
                </label>

                <input
                    type="email"
                    id="email"
                    name="email"
                    placeholder="you@example.com"
                    required
                >
            </div>

            <!-- Hidden honeypot field for simple bots -->
            <div class="hidden">
                <label for="website">
                    Website
                </label>

                <input
                    type="text"
                    id="website"
                    name="website"
                    autocomplete="off"
                    tabindex="-1"
                >
            </div>

            <div class="checkbox-row">
                <input
                    type="checkbox"
                    id="human_check"
                    name="human_check"
                    value="yes"
                    required
                >

                <label for="human_check">
                    I am a human and not an automated bot.
                </label>
            </div>

            <button type="submit">
                Continue
            </button>

        </form>

        <p class="privacy-note">
            No account or password required.
            Your email is only used for course-opening alerts.
        </p>

    </div>
    """

    return page_template(
        content,
        "Rutgers Course Sniper"
    )


@app.post("/courses", response_class=HTMLResponse)
def courses_page(
    email: str = Form(...),
    human_check: str = Form(...),
    website: str = Form("")
):

    # A basic honeypot check.
    if website.strip():
        return page_template(
            """
            <div class="card">
                <h1>Verification failed.</h1>

                <p class="subtitle">
                    Please return to the homepage and try again.
                </p>

                <a href="/">Go back</a>
            </div>
            """,
            "Verification Failed"
        )

    if human_check != "yes":
        return page_template(
            """
            <div class="card">
                <h1>Verification required.</h1>

                <p class="subtitle">
                    Please complete the human verification.
                </p>

                <a href="/">Go back</a>
            </div>
            """,
            "Verification Required"
        )

    email = email.strip().lower()
    safe_email = html.escape(email)

    content = f"""
    <div class="card">

        <h1>Add your sections.</h1>

        <p class="subtitle">
            Enter one five-digit Rutgers section index at a time.
            Confirm the course information before adding it.
        </p>

        <div class="email-display">
            Alerts will be sent to:
            <strong>{safe_email}</strong>

            <br>

            <a href="/">
                Change email
            </a>
        </div>

        <div
            id="message"
            class="message"
            aria-live="polite"
        ></div>

        <label for="section-search-input">
            Section index
        </label>

        <div class="section-search">

            <input
                type="text"
                id="section-search-input"
                maxlength="5"
                inputmode="numeric"
                placeholder="Example: 17704"
            >

            <button
                type="button"
                id="find-section-button"
            >
                Find Section
            </button>

        </div>

        <div id="course-result"></div>

        <div class="watchlist">

            <div class="watchlist-header">

                <h2>Your Watchlist</h2>

                <span
                    id="watch-count"
                    class="watch-count"
                >
                    0 / 5 sections
                </span>

            </div>

            <div id="watchlist-items">
                <p
                    id="empty-watchlist"
                    class="course-detail"
                >
                    You have not added any sections yet.
                </p>
            </div>

        </div>

        <form
            action="/subscribe"
            method="post"
            id="subscription-form"
            class="submit-area"
        >

            <input
                type="hidden"
                name="email"
                value="{safe_email}"
            >

            <input
                type="hidden"
                name="section_index"
                id="section-indexes"
                value=""
            >

            <button
                type="submit"
                id="submit-watchlist"
                disabled
            >
                Start Monitoring
            </button>

        </form>

    </div>

    <script>

        const sectionInput =
            document.getElementById(
                "section-search-input"
            );

        const findButton =
            document.getElementById(
                "find-section-button"
            );

        const courseResult =
            document.getElementById(
                "course-result"
            );

        const watchlistItems =
            document.getElementById(
                "watchlist-items"
            );

        const emptyWatchlist =
            document.getElementById(
                "empty-watchlist"
            );

        const watchCount =
            document.getElementById(
                "watch-count"
            );

        const sectionIndexesInput =
            document.getElementById(
                "section-indexes"
            );

        const submitButton =
            document.getElementById(
                "submit-watchlist"
            );

        const messageBox =
            document.getElementById(
                "message"
            );

        const watchlist = [];


        function showMessage(text, type) {{

            messageBox.textContent = text;

            messageBox.className =
                "message " +
                (
                    type === "error"
                    ? "error-message"
                    : "success-message"
                );

            messageBox.style.display = "block";
        }}


        function hideMessage() {{
            messageBox.style.display = "none";
        }}


        function escapeHtml(value) {{

            const element =
                document.createElement("div");

            element.textContent = value;

            return element.innerHTML;
        }}


        function updateWatchlist() {{

            watchlistItems.innerHTML = "";

            if (watchlist.length === 0) {{

                const emptyMessage =
                    document.createElement("p");

                emptyMessage.className =
                    "course-detail";

                emptyMessage.textContent =
                    "You have not added any sections yet.";

                watchlistItems.appendChild(
                    emptyMessage
                );
            }}

            for (const section of watchlist) {{

                const item =
                    document.createElement("div");

                item.className =
                    "watchlist-item";

                item.innerHTML = `
                    <div class="course-title">
                        ${{escapeHtml(section.course_title)}}
                    </div>

                    <div class="course-code">
                        ${{escapeHtml(section.course_code)}}
                    </div>

                    <div class="course-detail">
                        <strong>Instructor:</strong>
                        ${{escapeHtml(section.instructors)}}
                    </div>

                    <div class="course-detail">
                        <strong>Section index:</strong>
                        ${{escapeHtml(
                            section.registration_index
                        )}}
                    </div>
                `;

                const removeButton =
                    document.createElement("button");

                removeButton.type = "button";
                removeButton.className =
                    "remove-button";

                removeButton.textContent =
                    "Remove";

                removeButton.addEventListener(
                    "click",
                    function () {{

                        const position =
                            watchlist.findIndex(
                                item =>
                                    item.registration_index ===
                                    section.registration_index
                            );

                        if (position !== -1) {{
                            watchlist.splice(
                                position,
                                1
                            );
                        }}

                        updateWatchlist();
                    }}
                );

                item.appendChild(removeButton);
                watchlistItems.appendChild(item);
            }}

            watchCount.textContent =
                `${{watchlist.length}} / 5 sections`;

            sectionIndexesInput.value =
                watchlist
                    .map(
                        section =>
                            section.registration_index
                    )
                    .join(",");

            submitButton.disabled =
                watchlist.length === 0;
        }}


        function displayCourse(section) {{

            courseResult.innerHTML = "";

            const resultCard =
                document.createElement("div");

            resultCard.className =
                "course-result";

            resultCard.innerHTML = `
                <div class="course-title">
                    ${{escapeHtml(section.course_title)}}
                </div>

                <div class="course-code">
                    ${{escapeHtml(section.course_code)}}
                </div>

                <div class="course-detail">
                    <strong>Instructor:</strong>
                    ${{escapeHtml(section.instructors)}}
                </div>

                <div class="course-detail">
                    <strong>Section index:</strong>
                    ${{escapeHtml(
                        section.registration_index
                    )}}
                </div>
            `;

            const addButton =
                document.createElement("button");

            addButton.type = "button";
            addButton.textContent =
                "Add to Watchlist";

            addButton.style.marginTop = "16px";

            addButton.addEventListener(
                "click",
                function () {{

                    hideMessage();

                    if (watchlist.length >= 5) {{
                        showMessage(
                            "You can watch a maximum of five sections.",
                            "error"
                        );

                        return;
                    }}

                    const alreadyAdded =
                        watchlist.some(
                            item =>
                                item.registration_index ===
                                section.registration_index
                        );

                    if (alreadyAdded) {{
                        showMessage(
                            "That section is already in your watchlist.",
                            "error"
                        );

                        return;
                    }}

                    watchlist.push(section);
                    updateWatchlist();

                    courseResult.innerHTML = "";
                    sectionInput.value = "";

                    showMessage(
                        "Section added to your watchlist.",
                        "success"
                    );

                    sectionInput.focus();
                }}
            );

            resultCard.appendChild(addButton);
            courseResult.appendChild(resultCard);
        }}


        async function findSection() {{

            hideMessage();
            courseResult.innerHTML = "";

            const sectionIndex =
                sectionInput.value.trim();

            if (
                sectionIndex.length !== 5 ||
                !/^\\d{{5}}$/.test(sectionIndex)
            ) {{
                showMessage(
                    "Please enter a valid five-digit section index.",
                    "error"
                );

                return;
            }}

            findButton.disabled = true;
            findButton.textContent = "Searching...";

            try {{

                const response =
                    await fetch(
                        `/api/section/${{sectionIndex}}`
                    );

                const data =
                    await response.json();

                if (!response.ok) {{
                    showMessage(
                        data.error ||
                        "That section could not be found.",
                        "error"
                    );

                    return;
                }}

                displayCourse(data);

            }} catch (error) {{

                showMessage(
                    "Something went wrong while searching.",
                    "error"
                );

            }} finally {{

                findButton.disabled = false;
                findButton.textContent =
                    "Find Section";
            }}
        }}


        findButton.addEventListener(
            "click",
            findSection
        );


        sectionInput.addEventListener(
            "keydown",
            function (event) {{

                if (event.key === "Enter") {{
                    event.preventDefault();
                    findSection();
                }}
            }}
        );

    </script>
    """

    return page_template(
        content,
        "Add Sections"
    )


@app.get("/api/section/{section_index}")
def find_section(section_index: str):

    section_index = section_index.strip()

    if (
        len(section_index) != 5
        or not section_index.isdigit()
    ):
        return JSONResponse(
            status_code=400,
            content={
                "error":
                    "Please enter a valid five-digit section index."
            }
        )

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

    except sqlite3.Error:
        return JSONResponse(
            status_code=500,
            content={
                "error":
                    "The course database could not be accessed."
            }
        )

    if section is None:
        return JSONResponse(
            status_code=404,
            content={
                "error":
                    "That section was not found."
            }
        )

    return {
        "registration_index": section[0],
        "course_code": section[1],
        "course_title": section[2],
        "instructors": section[3]
    }


@app.post("/subscribe", response_class=HTMLResponse)
def subscribe(
    email: str = Form(...),
    section_index: str = Form(...)
):

    email = email.strip().lower()

    sections = [
        section.strip()
        for section in section_index.split(",")
        if section.strip()
    ]

    # Remove duplicates while preserving order.
    sections = list(dict.fromkeys(sections))

    if not sections:
        return page_template(
            """
            <div class="card">

                <h1>No sections selected.</h1>

                <p class="subtitle">
                    Please return and add at least one section.
                </p>

                <a href="/">
                    Return home
                </a>

            </div>
            """,
            "No Sections Selected"
        )

    if len(sections) > 5:
        return page_template(
            """
            <div class="card">

                <h1>Too many sections.</h1>

                <p class="subtitle">
                    You may watch a maximum of five sections.
                </p>

                <a href="/">
                    Return home
                </a>

            </div>
            """,
            "Too Many Sections"
        )

    for section in sections:

        if (
            len(section) != 5
            or not section.isdigit()
        ):
            return page_template(
                """
                <div class="card">

                    <h1>Invalid section.</h1>

                    <p class="subtitle">
                        One of the submitted section indexes
                        was not valid.
                    </p>

                    <a href="/">
                        Return home
                    </a>

                </div>
                """,
                "Invalid Section"
            )

    # Verify each submitted section exists.
    try:
        with sqlite3.connect(
            COURSE_DATABASE
        ) as connection:

            cursor = connection.cursor()

            placeholders = ",".join(
                "?"
                for _ in sections
            )

            cursor.execute(
                f"""
                SELECT registration_index
                FROM course_sections
                WHERE registration_index IN (
                    {placeholders}
                )
                """,
                sections
            )

            found_sections = {
                row[0]
                for row in cursor.fetchall()
            }

    except sqlite3.Error:
        return page_template(
            """
            <div class="card">

                <h1>Database error.</h1>

                <p class="subtitle">
                    We could not verify your sections.
                    Please try again.
                </p>

                <a href="/">
                    Return home
                </a>

            </div>
            """,
            "Database Error"
        )

    missing_sections = [
        section
        for section in sections
        if section not in found_sections
    ]

    if missing_sections:
        missing_text = html.escape(
            ", ".join(missing_sections)
        )

        return page_template(
            f"""
            <div class="card">

                <h1>Section not found.</h1>

                <p class="subtitle">
                    These sections could not be verified:
                    <strong>{missing_text}</strong>
                </p>

                <a href="/">
                    Return home
                </a>

            </div>
            """,
            "Section Not Found"
        )

    formatted_sections = ", ".join(sections)

    add_subscription(
        email,
        formatted_sections
    )

    safe_email = html.escape(email)
    safe_sections = html.escape(
        formatted_sections
    )

    content = f"""
    <div class="card">

        <h1>You're on the watchlist.</h1>

        <p class="subtitle">
            We will notify
            <strong>{safe_email}</strong>
            when any of these sections open:
        </p>

        <div class="course-result">
            <strong>{safe_sections}</strong>
        </div>

        <a href="/">
            Watch more sections
        </a>

    </div>
    """

    return page_template(
        content,
        "Subscription Created"
    )


