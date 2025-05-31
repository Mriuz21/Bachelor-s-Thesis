# app.py
import mysql.connector
import os
import traceback
from dotenv import load_dotenv
from scraper import scrape_article
from aiModel import predict_fake_news, MODELS
from flask import Flask, request, jsonify
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
CORS(app)

# MySQL connection
db = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'fake_news_db')
)
cursor = db.cursor()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        return jsonify({'message': 'User registered successfully!'})
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()

    if user:
        return jsonify({'message': 'Login successful!'})
    else:
        return jsonify({'error': 'Invalid username or password'}), 401
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        title = data.get('title')
        text = data.get('text')

        if not title or not text:
            return jsonify({'error': 'Both title and text are required'}), 400

        prediction = predict_fake_news(title, text)
        return jsonify({'prediction': prediction})

    except Exception as e:
        print("ERROR during /predict:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/scrape_predict', methods=['POST'])
def scrape_predict():
    try:
        data = request.get_json()
        url = data.get('url')
        model_key = data.get('model', 'roberta')  # Default to roberta if not specified
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        article_data = scrape_article(url) 
        title = article_data.get('title')
        text = article_data.get('text')

        if not title or not text:
            return jsonify({'error': 'Scraping failed or incomplete data'}), 500

        prediction = predict_fake_news(title, text, model_key)

        return jsonify({
            'title': title,
            'text': text,
            'prediction': prediction,
            'model_used': MODELS[model_key]['display_name']
        })

    except Exception as e:
        print("ERROR during /scrape_predict:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
