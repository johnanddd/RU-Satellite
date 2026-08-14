import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Thread

from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from coursesniper5 import start_course_sniper
from database import (
    DATABASE_NAME,
    add_subscription,
    create_database,
    edit_subscription,
    get_subscriptions,
)

# python -m uvicorn app2:app --reload

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

COURSE_DATABASE = BASE_DIR / "course_data.db"
SUBSCRIPTION_DATABASE = DATABASE_NAME

MAX_WATCHED_SECTIONS = 10


# ---------------------------------------------------------
# Application startup
# ---------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()

    Thread(
        target=start_course_sniper,
        daemon=True,
        name="ru-satellite-monitor",
    ).start()

    yield


app = FastAPI(
    title="RU Satellite",
    lifespan=lifespan,
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def normalize_email(email: str) -> str:
    return email.strip().lower()


def parse_section_text(value: str | None) -> list[str]:
    if not value:
        return []

    return list(
        dict.fromkeys(
            section.strip()
            for section in value.split(",")
            if section.strip()
        )
    )


def valid_section_index(section_index: str) -> bool:
    return (
        len(section_index) == 5
        and section_index.isdigit()
    )


def get_account(email: str) -> dict:
    """
    Build one logical RU Satellite account from the current
    subscriptions table.

    Older versions of the project allowed duplicate email rows,
    so this combines them when loading.
    """
    subscriptions = get_subscriptions() or []

    matching_rows = [
        row
        for row in subscriptions
        if normalize_email(row[1]) == email
    ]

    waiting = []
    notified = []

    for row in matching_rows:
        waiting.extend(
            parse_section_text(row[2])
        )
        notified.extend(
            parse_section_text(row[3])
        )

    waiting = list(dict.fromkeys(waiting))
    notified = list(dict.fromkeys(notified))

    # If a legacy row contains the same section in both lists,
    # keep the notified state so the user is not emailed twice.
    waiting = [
        section
        for section in waiting
        if section not in notified
    ]

    all_sections = list(
        dict.fromkeys(waiting + notified)
    )

    return {
        "exists": bool(matching_rows),
        "email": email,
        "waiting": waiting,
        "notified": notified,
        "sections": all_sections,
    }


def collapse_duplicate_email_rows(email: str) -> None:
    """
    Keep only the oldest row for an email.

    The next database.py refactor will move this responsibility
    out of app2.py and enforce unique emails at the database layer.
    """
    with sqlite3.connect(
        SUBSCRIPTION_DATABASE
    ) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM subscriptions
            WHERE lower(email) = ?
            ORDER BY id ASC
            """,
            (email,),
        )

        ids = [
            row[0]
            for row in cursor.fetchall()
        ]

        if len(ids) <= 1:
            return

        duplicate_ids = ids[1:]

        placeholders = ",".join(
            "?"
            for _ in duplicate_ids
        )

        cursor.execute(
            f"""
            DELETE FROM subscriptions
            WHERE id IN ({placeholders})
            """,
            duplicate_ids,
        )

        connection.commit()


def save_watchlist(
    email: str,
    desired_sections: list[str],
) -> None:
    """
    Save the user's entire watchlist.

    Sections that were already notified stay notified.
    New sections go into the waiting list.
    """
    account = get_account(email)

    previously_notified = set(
        account["notified"]
    )

    notified = [
        section
        for section in desired_sections
        if section in previously_notified
    ]

    waiting = [
        section
        for section in desired_sections
        if section not in previously_notified
    ]

    waiting_text = ", ".join(waiting)
    notified_text = ", ".join(notified)

    if account["exists"]:
        edit_subscription(
            email,
            waiting_text,
            notified_text,
        )

        collapse_duplicate_email_rows(email)

    else:
        add_subscription(
            email,
            waiting_text,
            notified_text,
        )


def get_section(section_index: str) -> dict | None:
    with sqlite3.connect(
        COURSE_DATABASE
    ) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                registration_index,
                course_code,
                course_title,
                instructors
            FROM course_sections
            WHERE registration_index = ?
            """,
            (section_index,),
        )

        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "registration_index":
            str(row["registration_index"]),
        "course_code":
            row["course_code"] or "",
        "course_title":
            row["course_title"] or "",
        "instructors":
            row["instructors"]
            or "Instructor not listed",
    }


def get_sections(
    section_indexes: list[str],
) -> list[dict]:
    if not section_indexes:
        return []

    sections = []

    for section_index in section_indexes:
        section = get_section(section_index)

        if section is None:
            section = {
                "registration_index":
                    section_index,
                "course_code":
                    "",
                "course_title":
                    "Rutgers section",
                "instructors":
                    "Course information unavailable",
            }

        sections.append(section)

    return sections


def validate_watchlist(
    sections: list[str],
) -> str | None:

    if len(sections) > MAX_WATCHED_SECTIONS:
        return (
            f"You can watch a maximum of "
            f"{MAX_WATCHED_SECTIONS} sections."
        )

    for section in sections:
        if not valid_section_index(section):
            return (
                "Every section index must "
                "be exactly five digits."
            )

        if get_section(section) is None:
            return (
                f"Section {section} "
                "could not be found."
            )

    return None


def render_dashboard(
    request: Request,
    email: str,
    message: str | None = None,
    message_type: str | None = None,
    status_code: int = 200,
):
    account = get_account(email)

    watched_sections = get_sections(
        account["sections"]
    )

    notified = set(
        account["notified"]
    )

    for section in watched_sections:
        section["notification_sent"] = (
            section["registration_index"]
            in notified
        )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "email":
                email,
            "account_exists":
                account["exists"],
            "watched_sections":
                watched_sections,
            "watch_count":
                len(watched_sections),
            "max_sections":
                MAX_WATCHED_SECTIONS,
            "message":
                message,
            "message_type":
                message_type,
        },
        status_code=status_code,
    )


# ---------------------------------------------------------
# Page routes
# ---------------------------------------------------------

@app.get(
    "/",
    response_class=HTMLResponse,
)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.post(
    "/dashboard",
    response_class=HTMLResponse,
)
def dashboard(
    request: Request,
    email: str = Form(...),
    human_check: str = Form(""),
    website: str = Form(""),
):
    email = normalize_email(email)

    # Honeypot
    if website.strip():
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "email":
                    email,
                "error":
                    "Verification failed. "
                    "Please try again.",
            },
            status_code=400,
        )

    if human_check != "yes":
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "email":
                    email,
                "error":
                    "Please confirm that "
                    "you are human.",
            },
            status_code=400,
        )

    return render_dashboard(
        request,
        email,
    )


@app.get(
    "/dashboard",
    response_class=HTMLResponse,
)
def remembered_dashboard(
    request: Request,
    email: str = Query(...),
):
    """
    app.js will use this route when an email exists
    in localStorage.
    """
    email = normalize_email(email)

    if not email:
        return RedirectResponse(
            url="/",
            status_code=303,
        )

    return render_dashboard(
        request,
        email,
    )


@app.post(
    "/watchlist",
    response_class=HTMLResponse,
)
def update_watchlist(
    request: Request,
    email: str = Form(...),
    section_index: str = Form(""),
):
    email = normalize_email(email)

    sections = list(
        dict.fromkeys(
            section.strip()
            for section
            in section_index.split(",")
            if section.strip()
        )
    )

    error = validate_watchlist(
        sections
    )

    if error:
        return render_dashboard(
            request,
            email,
            message=error,
            message_type="error",
            status_code=400,
        )

    save_watchlist(
        email,
        sections,
    )

    return render_dashboard(
        request,
        email,
        message="Watchlist saved.",
        message_type="success",
    )


# ---------------------------------------------------------
# JSON API routes
# ---------------------------------------------------------

@app.get(
    "/api/section/{section_index}"
)
def section_lookup(
    section_index: str,
):
    section_index = (
        section_index.strip()
    )

    if not valid_section_index(
        section_index
    ):
        return JSONResponse(
            status_code=400,
            content={
                "error":
                    "Please enter a valid "
                    "five-digit section index."
            },
        )

    try:
        section = get_section(
            section_index
        )

    except sqlite3.Error:
        return JSONResponse(
            status_code=500,
            content={
                "error":
                    "RU Satellite could not "
                    "access the course database."
            },
        )

    if section is None:
        return JSONResponse(
            status_code=404,
            content={
                "error":
                    "That Rutgers section "
                    "was not found."
            },
        )

    return section


@app.get("/api/watchlist")
def watchlist_api(
    email: str = Query(...),
):
    email = normalize_email(email)
    account = get_account(email)

    sections = get_sections(
        account["sections"]
    )

    notified = set(
        account["notified"]
    )

    for section in sections:
        section["notification_sent"] = (
            section["registration_index"]
            in notified
        )

    return {
        "email":
            email,
        "exists":
            account["exists"],
        "sections":
            sections,
        "count":
            len(sections),
        "max_sections":
            MAX_WATCHED_SECTIONS,
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "RU Satellite",
    }
