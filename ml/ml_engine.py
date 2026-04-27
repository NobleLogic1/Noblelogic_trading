import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from transformers import pipeline
import requests
from datetime import datetime, timedelta
import joblib
import json
import os

class CryptoMLEngine:
    def __init__(self):
        self.model = self._build_model()
        self.sentiment_analyzer = pipeline('sentiment-analysis')
        self.scaler = MinMaxScaler()
        self.feature_columns = [
            'price', 'volume', 'rsi', 'macd', 'sentiment_score',
            'news_score', 'social_score', 'market_trend',
            'volatility', 'success_rate'
        ]
        
        # Performance tracking
        self.performance_history = []
        self.learning_rate = 0.001
        self.batch_size = 32
        self.error_threshold = 0.02  # 2% prediction error threshold
        
        # Load existing model if available
        self.model_path = 'ml/models/'
        os.makedirs(self.model_path, exist_ok=True)
        self.load_latest_model()

    def _build_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(128, return_sequences=True, input_shape=(24, 10)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.LSTM(64, return_sequences=False),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(3, activation='softmax')  # Buy, Sell, Hold
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        return model

    async def gather_features(self, symbol, timeframe='1h'):
        """Gather all features for prediction"""
        try:
            # Technical indicators
            technical = await self.get_technical_indicators(symbol, timeframe)
            
            # News and sentiment
            news_data = await self.gather_news_data(symbol)
            sentiment_data = await self.analyze_market_sentiment(symbol)
            social_data = await self.gather_social_data(symbol)
            
            # Market data
            market_data = await self.get_market_data(symbol)
            
            # Combine all features
            features = {
                **technical,
                **news_data,
                **sentiment_data,
                **market_data,
                'social_score': social_data['score']
            }
            
            return self.preprocess_features(features)
        except Exception as e:
            print(f"Error gathering features: {e}")
            return None

    async def get_technical_indicators(self, symbol, timeframe):
        """Calculate technical indicators"""
        try:
            # Get historical data
            data = await self.fetch_historical_data(symbol, timeframe)
            df = pd.DataFrame(data)
            
            return {
                'rsi': self.calculate_rsi(df['close']),
                'macd': self.calculate_macd(df['close']),
                'volatility': self.calculate_volatility(df['close']),
                'market_trend': self.detect_trend(df['close'])
            }
        except Exception as e:
            print(f"Error calculating technical indicators: {e}")
            return {}

    async def gather_news_data(self, symbol):
        """Gather and analyze news data"""
        try:
            news_articles = await self.fetch_news(symbol)
            scores = []
            
            for article in news_articles:
                # Analyze sentiment of each article
                sentiment = self.sentiment_analyzer(article['title'] + ' ' + article['description'])[0]
                scores.append(sentiment['score'] * (1 if sentiment['label'] == 'POSITIVE' else -1))
            
            return {
                'news_score': np.mean(scores) if scores else 0,
                'news_count': len(scores)
            }
        except Exception as e:
            print(f"Error gathering news data: {e}")
            return {'news_score': 0, 'news_count': 0}

    async def analyze_market_sentiment(self, symbol):
        """Analyze overall market sentiment"""
        try:
            # Combine multiple sentiment sources
            sentiment_sources = await self.gather_sentiment_sources(symbol)
            
            # Weight and combine sentiment scores
            weighted_sentiment = self.calculate_weighted_sentiment(sentiment_sources)
            
            return {
                'sentiment_score': weighted_sentiment,
                'sentiment_sources': len(sentiment_sources)
            }
        except Exception as e:
            print(f"Error analyzing market sentiment: {e}")
            return {'sentiment_score': 0, 'sentiment_sources': 0}

    def predict(self, features):
        """Make prediction based on current features"""
        try:
            # Reshape features for LSTM input
            features_reshaped = features.reshape((1, 24, 10))
            
            # Get model prediction
            prediction = self.model.predict(features_reshaped)
            
            # Get confidence scores
            confidence = np.max(prediction)
            action = np.argmax(prediction)
            
            return {
                'action': ['SELL', 'HOLD', 'BUY'][action],
                'confidence': float(confidence),
                'prediction_time': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error making prediction: {e}")
            return None

    def update_model(self, features, actual_outcome, trade_result):
        """Update model based on trade results"""
        try:
            # Prepare training data
            X = features.reshape((1, 24, 10))
            y = tf.keras.utils.to_categorical([actual_outcome], num_classes=3)
            
            # Calculate prediction error
            current_prediction = self.model.predict(X)
            prediction_error = np.abs(current_prediction - y)
            
            # Update model if error exceeds threshold
            if np.max(prediction_error) > self.error_threshold:
                self.model.fit(
                    X, y,
                    epochs=1,
                    batch_size=1,
                    verbose=0
                )
                
                # Save updated model
                self.save_model()
                
            # Update performance history
            self.performance_history.append({
                'timestamp': datetime.now().isoformat(),
                'prediction_error': float(np.max(prediction_error)),
                'trade_result': trade_result,
                'features': features.tolist()
            })
            
        except Exception as e:
            print(f"Error updating model: {e}")

    def save_model(self):
        """Save the current model state"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            model_filename = f'crypto_ml_model_{timestamp}'
            
            # Save TensorFlow model
            self.model.save(f'{self.model_path}{model_filename}.h5')
            
            # Save scaler
            joblib.dump(self.scaler, f'{self.model_path}{model_filename}_scaler.pkl')
            
            # Save performance history
            with open(f'{self.model_path}{model_filename}_history.json', 'w') as f:
                json.dump(self.performance_history[-1000:], f)  # Keep last 1000 entries
                
        except Exception as e:
            print(f"Error saving model: {e}")

    def load_latest_model(self):
        """Load the most recent model"""
        try:
            model_files = [f for f in os.listdir(self.model_path) if f.endswith('.h5')]
            if model_files:
                latest_model = max(model_files)
                self.model = tf.keras.models.load_model(f'{self.model_path}{latest_model}')
                
                # Load corresponding scaler
                scaler_file = latest_model.replace('.h5', '_scaler.pkl')
                if os.path.exists(f'{self.model_path}{scaler_file}'):
                    self.scaler = joblib.load(f'{self.model_path}{scaler_file}')
                    
                # Load performance history
                history_file = latest_model.replace('.h5', '_history.json')
                if os.path.exists(f'{self.model_path}{history_file}'):
                    with open(f'{self.model_path}{history_file}', 'r') as f:
                        self.performance_history = json.load(f)
                        
        except Exception as e:
            print(f"Error loading model: {e}")

    def preprocess_features(self, features):
        """Preprocess features for model input"""
        try:
            # Extract features in correct order
            feature_array = np.array([[
                features.get(col, 0) for col in self.feature_columns
            ]])
            
            # Scale features
            scaled_features = self.scaler.fit_transform(feature_array)
            
            return scaled_features
            
        except Exception as e:
            print(f"Error preprocessing features: {e}")
            return None