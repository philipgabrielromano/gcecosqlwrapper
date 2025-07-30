
from flask import Flask, request, jsonify
import pymysql
import os

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", ""),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", ""),
    "ssl": {
        "ca": os.path.abspath("azure-ca.pem")
    }
}


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
        conn = pymysql.connect(**DB_CONFIG)
        with conn.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
        return jsonify({"result": [dict(zip(columns, row)) for row in rows]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
