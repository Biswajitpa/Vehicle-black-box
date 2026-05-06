from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import time

app = Flask(__name__)

DB_CFG = {
    "host": "localhost",
    "user": "bbuser",          # change if needed
    "password": "bbpass123",   # change if needed
    "database": "vehicle_blackbox",
    "autocommit": True
}

conn = None
cur = None

def db_connect():
    global conn, cur
    while True:
        try:
            conn = mysql.connector.connect(**DB_CFG)
            cur = conn.cursor()
            print("✅ MySQL connected")
            return
        except Error as e:
            print("❌ MySQL connect failed:", e)
            time.sleep(2)

def ensure_table():
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sensor_logs (
      id BIGINT AUTO_INCREMENT PRIMARY KEY,
      ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      temperature FLOAT,
      humidity FLOAT,
      gas INT,
      alcohol INT,
      mic INT,
      latitude DOUBLE,
      longitude DOUBLE,
      speed FLOAT,
      device_id VARCHAR(50)
    )
    """)

@app.route("/api/health", methods=["GET"])
def health():
    return "OK", 200

@app.route("/api/data", methods=["POST"])
def api_data():
    global conn, cur

    try:
        d = request.get_json(force=True)

        # Pull values (safe)
        device_id = str(d.get("device_id", "esp32-01"))
        temperature = d.get("temperature", None)
        humidity = d.get("humidity", None)
        gas = d.get("gas", None)
        alcohol = d.get("alcohol", None)
        mic = d.get("mic", None)
        latitude = d.get("latitude", None)
        longitude = d.get("longitude", None)
        speed = d.get("speed", None)

        # Insert
        sql = """
        INSERT INTO sensor_logs
        (temperature, humidity, gas, alcohol, mic, latitude, longitude, speed, device_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cur.execute(sql, (temperature, humidity, gas, alcohol, mic, latitude, longitude, speed, device_id))

        return jsonify({"status": "ok"})

    except Exception as e:
        # If DB disconnected, reconnect
        try:
            conn.ping(reconnect=True, attempts=3, delay=2)
        except:
            db_connect()
            ensure_table()

        return jsonify({"status": "error", "msg": str(e)}), 400

if __name__ == "__main__":
    db_connect()
    ensure_table()
    # Listen for ESP32 on LAN
    app.run(host="0.0.0.0", port=5000, debug=False)