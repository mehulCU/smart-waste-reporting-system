from flask import Flask, render_template, request, redirect
import sqlite3
import webbrowser
import urllib.parse

app = Flask(__name__)

def get_db():
    return sqlite3.connect("database.db")

# Create table
conn = get_db()
conn.execute('''
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT,
    lat REAL,
    lng REAL,
    status TEXT
)
''')
conn.close()

# 🤖 AI Risk Calculation
def calculate_risk(lat, lng):
    conn = get_db()
    reports = conn.execute("SELECT lat, lng FROM reports").fetchall()
    conn.close()

    count = 0
    for r in reports:
        if abs(r[0] - float(lat)) < 0.01 and abs(r[1] - float(lng)) < 0.01:
            count += 1

    if count > 5:
        return "High"
    elif count > 2:
        return "Medium"
    else:
        return "Low"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        location = request.form["location"]
        lat = request.form["lat"]
        lng = request.form["lng"]

        risk = calculate_risk(lat, lng)

        conn = get_db()
        conn.execute(
            "INSERT INTO reports (location, lat, lng, status) VALUES (?, ?, ?, ?)",
            (location + f" (Risk: {risk})", lat, lng, "pending")
        )
        conn.commit()
        conn.close()

        # 📱 WhatsApp Message
        phone = "9983120054"   # 🔴 replace with your number

        maps_link = f"https://www.google.com/maps?q={lat},{lng}"

        msg = f"""🚨 Waste Reported!
📍 Location: {location}
🧠 Risk Level: {risk}
🗺️ Map: {maps_link}
"""

        message = urllib.parse.quote(msg)

        url = f"https://wa.me/{phone}?text={message}"
        return redirect(url)

        

    return render_template("index.html")

@app.route("/admin")
def admin():
    conn = get_db()
    reports = conn.execute("SELECT * FROM reports").fetchall()
    conn.close()

    return render_template("admin.html", reports=reports)

@app.route("/update/<int:id>")
def update(id):
    conn = get_db()
    conn.execute("UPDATE reports SET status='cleaned' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)