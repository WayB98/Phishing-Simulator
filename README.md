# Phishing Simulator

Flask web app to simulate phishing campaigns, track clicks, and export logs.

## Features
- Real-time click logging (Flask + SQLAlchemy)
- Dashboard with Chart.js
- Admin filtering & Excel export
- .env-based secrets (no hardcoded credentials)

## Tech Stack
Flask, SQLAlchemy, Chart.js, Bootstrap (or your theme)

## Quickstart
```bash
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env  # or create your own .env
python app.py
