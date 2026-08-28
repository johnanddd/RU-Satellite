# RU Satellite

RU Satellite is a 100% free Rutgers course monitoring website I made that alerts students when a closed section opens.

Students can currently monitor up to **20 sections per email**, and RU Satellite checks Rutgers course availability continuously and sends an email alert when one of their watched sections becomes available.
All completely for free for no payments, unlike a lot of other Rutgers snipers.

**Live site:** https://ru-satellite.onrender.com

## Features

* Monitor up to 50 Rutgers sections at once
* Fast automatic course availability checks
* Email alerts when a section opens
* Direct WebReg registration link in alerts
* Watchlist dashboard for adding and removing sections
* Tracks previously alerted sections so users can be notified again if a section closes and later reopens
* Welcome email when a new watchlist is created

## How It Works

RU Satellite periodically checks Rutgers' course availability data and compares currently open sections against each user's watchlist.

When a monitored section opens:

1. RU Satellite detects the opening
2. The section is marked as already notified
3. An email is immediately sent to the user
4. If the section later closes, the alert resets so the user can be notified the next time it opens

## Tech Stack

* Python
* FastAPI
* SQLite
* HTML / CSS / JavaScript
* Gmail SMTP
* Render
* Rutgers Schedule of Classes data

## Project Structure

* `app2.py` — FastAPI web application and routes
* `coursesniper5.py` — course monitoring system
* `database.py` — SQLite subscription and watchlist management
* `email_services.py` — email alerts and welcome emails
* `course_data_search.py` — Rutgers course lookup
* `course_data_creator.py` — course data processing
* `templates/` — HTML pages
* `static/` — JavaScript, CSS, and images

## Why I Made It

I built RU Satellite because getting into closed Rutgers sections forced me to user other snipers in the past I didn't enjoy or didn't have enough free features. 
I wanted a simple tool that could do that monitoring automatically while staying completely free.

The project also gave me experience building and deploying a full web application, working with databases, background monitoring, external course data, automated email systems, and production debugging.
