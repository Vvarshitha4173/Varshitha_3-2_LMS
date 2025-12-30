from flask import Flask, render_template, request, redirect, url_for, session
import requests
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
load_dotenv()
import os

apikey = os.getenv("APIKEY")

con = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_DATABASE")
)

cursor = con.cursor()

url = "https://api.api-ninjas.com/v1/quotes"
headers = {'X-Api-Key': apikey}

def get_quote():
    response = requests.get(url, headers=headers)
    data = response.json()

    if isinstance(data, list) and len(data) > 0:
        return data[0]['quote'], data[0]['author'], data[0]['category']
    else:
        return "No quote found", "Unknown", "General"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# ---------------- HOME PAGE ----------------
@app.route('/')
def homepage():
    return render_template('home.html')

# ---------------- REGISTRATION ----------------
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == "POST":
        user = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirmPassword = request.form["confirmPassword"]

        if password != confirmPassword:
            return "Passwords do not match"

        try:
            cursor.execute(
                'INSERT INTO registration (username, email, password) VALUES (%s, %s, %s)',
                (user, email, password)
            )
            con.commit()
            return redirect(url_for('login'))

        except Error as e:
            if "Duplicate entry" in str(e):
                return "Email already registered. Please login."
            else:
                return str(e)

    return render_template('registration.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM registration WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        if user:
            session['user'] = email
            return redirect(url_for('ai_quotes'))
        else:
            return "Invalid login credentials"

    return render_template('login.html')

# ---------------- AI QUOTES ----------------
@app.route('/ai_quotes')
def ai_quotes():
    if 'user' not in session:
        return redirect(url_for('login'))

    quote, author, category = get_quote()
    return render_template(
        'ai_quotes.html',
        quote1=quote,
        author1=author,
        category1=category
    )

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('homepage'))

if __name__ == "__main__":
    app.run(debug=True)
