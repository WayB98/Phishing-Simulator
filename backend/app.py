from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # change in production

# --------------------
# Database Config
# --------------------
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "instance", "clicks.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --------------------
# Database Model
# --------------------
class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --------------------
# Helper
# --------------------
def get_chart_data(clicks):
    df = pd.DataFrame([{"email": c.email, "timestamp": c.timestamp} for c in clicks])
    if df.empty:
        return [], []
    df["date"] = df["timestamp"].dt.strftime("%Y-%m-%d")
    grouped = df.groupby("date").size()
    labels = list(grouped.index)
    # numpy.int64 -> Python int for JSON serialization
    data = [int(x) for x in grouped.values]
    return labels, data

# --------------------
# Routes
# --------------------
@app.route("/")
def index():
    return redirect(url_for("dashboard"))

# Public Dashboard
@app.route("/dashboard")
def dashboard():
    clicks = Click.query.order_by(Click.timestamp.desc()).all()
    labels, data = get_chart_data(clicks)

    # Simple metrics for tiles (keeps templates clean)
    unique_count = len({c.email for c in clicks})
    cutoff = datetime.utcnow() - timedelta(days=7)
    last7_count = sum(1 for c in clicks if c.timestamp and c.timestamp >= cutoff)

    return render_template(
        "dashboard.html",
        clicks=clicks,
        labels=labels,
        data=data,
        unique_count=unique_count,
        last7_count=last7_count,
    )

# Admin Panel (with optional filters)
@app.route("/admin")
def admin():
    query = Click.query

    email = request.args.get("email")
    start = request.args.get("start")
    end = request.args.get("end")

    if email:
        query = query.filter(Click.email.ilike(f"%{email}%"))
    if start:
        query = query.filter(Click.timestamp >= datetime.strptime(start, "%Y-%m-%d"))
    if end:
        # add 1 day to include end-of-day timestamps
        query = query.filter(Click.timestamp < datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1))

    clicks = query.order_by(Click.timestamp.desc()).all()
    labels, data = get_chart_data(clicks)

    return render_template("admin.html", clicks=clicks, labels=labels, data=data)

# Export clicks to Excel
@app.route("/export/clicks.xlsx")
def export_clicks():
    clicks = Click.query.order_by(Click.timestamp.desc()).all()
    df = pd.DataFrame([{"email": c.email, "timestamp": c.timestamp} for c in clicks])
    export_path = os.path.join(basedir, "instance", "clicks.xlsx")
    df.to_excel(export_path, index=False)
    return send_file(export_path, as_attachment=True)

# Fake login/logout for now (expand later)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        pw = request.form.get("password")
        if user == "admin" and pw == "password":  # change later
            session["admin"] = True
            return redirect(url_for("admin"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("dashboard"))

# --------------------
# Run
# --------------------
if __name__ == "__main__":
    os.makedirs(os.path.join(basedir, "instance"), exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
