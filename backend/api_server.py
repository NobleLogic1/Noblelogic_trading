from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import requests
from datetime import datetime, timedelta
import random
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
CRYPTOPANIC_API_URL = "https://cryptopanic.com/api/v1"
CRYPTOPANIC_API_KEY = "demo"  # Replace with your actual API key

# Proxy endpoints
@app.route('/api/news', methods=['GET'])
def get_news():
    try:
        # Proxy the request to CryptoPanic
        response = requests.get(
            f"{CRYPTOPANIC_API_URL}/posts/",
            params={
                "auth_token": CRYPTOPANIC_API_KEY,
                "public": "true"
            }
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/market-sentiment', methods=['GET'])
def get_market_sentiment():
    try:
        # Generate sample sentiment data (replace with actual sentiment analysis)
        sentiment_data = {
            "overall": random.uniform(-1, 1),
            "bitcoin": random.uniform(-1, 1),
            "ethereum": random.uniform(-1, 1),
            "trends": [
                {
                    "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                    "sentiment": random.uniform(-1, 1)
                } for i in range(24)
            ]
        }
        return jsonify(sentiment_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Data endpoints
@app.route('/api/health', methods=['GET'])
def health_check():
    data = read_json_file('health_status.json')
    return jsonify(data if data else {'status': 'error', 'message': 'Could not read health data'})

@app.route('/api/trades/active', methods=['GET'])
def active_trades():
    data = read_json_file('trade_log.json')
    return jsonify(data if data else [])

@app.route('/api/strategy/performance', methods=['GET'])
def strategy_performance():
    data = read_json_file('strategy_output.json')
    return jsonify(data if data else {})

def read_json_file(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {filename}: {str(e)}")
        return None

if __name__ == '__main__':
    print("Starting API server...")
    app.run(debug=True, port=5000)