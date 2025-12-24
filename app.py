from flask import Flask, render_template
import requests
from dotenv import load_dotenv
import os

load_dotenv()

apikey = os.getenv("APIKEY")
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

@app.route('/')
def home():
    quote, author, category = get_quote()
    return render_template(
        'ai_quotes.html',
        quote1=quote,
        author1=author,
        category1=category
    )

@app.route('/registration')
def registration():
    return render_template('registration.html')

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/home')
def homepage():
    return render_template('home.html')
app.run(debug=True)
