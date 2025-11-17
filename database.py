import sqlite3

def init_db():
    conn = sqlite3.connect("honeypot.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            topic TEXT,
            payload TEXT,
            ip_address TEXT,
            attack_type TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_attack(timestamp, topic, payload, ip, attack_type):
    conn = sqlite3.connect("honeypot.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO attacks (timestamp, topic, payload, ip_address, attack_type)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, topic, payload, ip, attack_type))

    conn.commit()
    conn.close()
