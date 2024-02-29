import os
import psycopg
from flask import Flask, request, redirect, url_for, escape


def get_database_url():
    if os.environ.get("APP_ENV") == "PRODUCTION":
        password = os.environ.get("POSTGRES_PASSWORD")
        hostname = os.environ.get("POSTGRES_HOSTNAME")
        return f"postgres://postgres:{password}@{hostname}:5432/postgres"
    else:
        return "postgres://localhost:5432/postgres"

def setup_database(url):
    connection = psycopg.connect(url)

    cursor = connection.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS messages (message TEXT);")

    connection.commit()

POSTGRES_URL = get_database_url()
setup_database(POSTGRES_URL)

app = Flask(__name__)


@app.route("/")
def get_messages():
    connection = psycopg.connect(POSTGRES_URL)

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM messages;")

    rows = cursor.fetchall()

    return format_messages(rows) + generate_form()

def format_messages(messages):
    output = "<ul>"
    for message in messages:
        escaped_message = escape(message[0])
        output += f"<li>{escaped_message}</li>"
    output += "</ul>"
    return output

def generate_form():
    return """
    <form action="/" method="POST">
        <input type="text" name="message">
        <input type="submit" value="Send">
    </form>
    """

@app.route("/", methods=["POST"])
def post_message():
    message = request.form["message"]

    connection = psycopg.connect(POSTGRES_URL)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO messages (message) VALUES (%s);", (message,))
    connection.commit()

    return redirect(url_for("get_messages"))

if __name__ == '__main__':
    if os.environ.get("APP_ENV") == "PRODUCTION":
        app.run(port=5000, host='0.0.0.0')
    else:
        app.run(debug=True, port=5000, host='0.0.0.0')
