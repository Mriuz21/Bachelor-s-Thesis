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
        return jsonify({
            'message': 'Login successful!',
            'user_id': user[0]
        })
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
        model_key = data.get('model', 'RoBERTa')  
        user_id = data.get('user_id')  
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        article_data = scrape_article(url) 
        title = article_data.get('title')
        text = article_data.get('text')

        if not title or not text:
            return jsonify({'error': 'Scraping failed or incomplete data'}), 500

        prediction = predict_fake_news(title, text, model_key)

        if user_id:
            cursor.execute("""
                INSERT INTO detections (user_id, url, model_used, prediction)
                VALUES (%s, %s, %s, %s)
            """, (user_id, url, model_key, prediction))
            db.commit()

            
            cursor.execute("""
                DELETE FROM detections
                WHERE user_id = %s AND id NOT IN (
                    SELECT id FROM (
                        SELECT id FROM detections
                        WHERE user_id = %s
                        ORDER BY detected_at DESC
                        LIMIT 20
                    ) AS sub
                )
            """, (user_id, user_id))
            db.commit()

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
@app.route('/history', methods=['GET'])
def history():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400

    try:
        cursor.execute("""
            SELECT id, url, model_used, prediction,detected_at
            FROM detections
            WHERE user_id = %s
            ORDER BY detected_at DESC
            LIMIT 20
        """, (user_id,))
        rows = cursor.fetchall()

        history = [
            {
                'id': row[0],
                'url': row[1],
                'model_used': row[2],
                'prediction': row[3],
                'title': row[4]
            }
            for row in rows
        ]

        return jsonify(history)
    except Exception as e:
        print("Error fetching history:", e)
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
