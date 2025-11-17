from flask import Flask, render_template, jsonify
import sqlite3

DB_PATH = "../honeypot.db"

app = Flask(__name__)

def fetch_data(query):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return rows

@app.route("/")
def index():
    # Summary stats
    total = fetch_data("SELECT COUNT(*) FROM attacks")[0][0]
    suspicious = fetch_data("SELECT COUNT(*) FROM attacks WHERE attack_type='suspicious'")[0][0]
    normal = fetch_data("SELECT COUNT(*) FROM attacks WHERE attack_type='normal'")[0][0]

    return render_template(
        "index.html",
        total=total,
        suspicious=suspicious,
        normal=normal
    )

@app.route("/attacks")
def attacks():
    logs = fetch_data("SELECT timestamp, topic, payload, ip_address, attack_type FROM attacks ORDER BY id DESC")
    return render_template("attacks.html", logs=logs)

@app.route("/api/attack_trends")
def attack_trends():
    rows = fetch_data("""
        SELECT DATE(timestamp), COUNT(*)
        FROM attacks
        GROUP BY DATE(timestamp)
        ORDER BY DATE(timestamp)
    """)
    dates = [r[0] for r in rows]
    counts = [r[1] for r in rows]
    return jsonify({"dates": dates, "counts": counts})

@app.route("/api/attack_types")
def attack_types():
    rows = fetch_data("""
        SELECT attack_type, COUNT(*) 
        FROM attacks
        GROUP BY attack_type
    """)
    types = [r[0] for r in rows]
    counts = [r[1] for r in rows]
    return jsonify({"types": types, "counts": counts})

if __name__ == "__main__":
    app.run(debug=True)
