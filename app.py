from flask import Flask, request, jsonify
import mysql.connector
import os

SSL_CERT_PATH = os.path.abspath("azure-ca.pem")  # Make sure this cert is present

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", ""),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", ""),
    "ssl_ca": SSL_CERT_PATH,  # Enable SSL
    "ssl_verify_cert": True
}

@app.route("/debug-cert")
def debug_cert():
    return "Exists!" if os.path.exists(SSL_CERT_PATH) else "Not found", 200

@app.route("/")
def home():
    return "MySQL passthrough API is running"

@app.route("/run_sql", methods=["POST"])
def run_sql():
    data = request.json
    query = data.get("query", "")

    if not query.lower().strip().startswith("select"):
        return jsonify({"error": "Only SELECT queries allowed"}), 400

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"result": [dict(zip(columns, row)) for row in rows]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
