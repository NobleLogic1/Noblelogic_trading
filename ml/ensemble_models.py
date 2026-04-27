"""
Ensemble Models for NobleLogic Trading System

Implements a voting ensemble of different model types to improve prediction
accuracy and robustness through model diversity.
"""

import numpy as np
import tensorflow as tf
from typing import Dict, List, Tuple, Any, Optional
import joblib
import os
import time

class EnsembleModel:
    """
    Ensemble of multiple model types:
    - Deep Neural Network (TensorFlow)
    - Gradient Boosting (XGBoost)
    - Random Forest (sklearn)
    - Support Vector Machine (sklearn)
    
    Uses a weighted voting mechanism to combine predictions.
    """
    
    def __init__(self, base_path: str = None):
        """
        Initialize the ensemble model
        
        Args:
            base_path: Base path for model storage
        """
        self.models = {}
        self.model_weights = {
            'dnn': 0.4,
            'xgboost': 0.3,
            'random_forest': 0.2,
            'svm': 0.1
        }
        self.base_path = base_path or os.path.join(os.path.dirname(__file__), 'models', 'ensemble')
        os.makedirs(self.base_path, exist_ok=True)
        
        # Dynamic performance tracking
        self.performance_history = []
        self.model_performance = {model_type: 0.5 for model_type in self.model_weights.keys()}
        
        # Load models if they exist
        self.load_models()
        
    def load_models(self):
        """Load all ensemble models from disk"""
        print(f"[ML] Loading ensemble models from {self.base_path}")
        
        # Load TensorFlow DNN
        try:
            tf_path = os.path.join(self.base_path, 'dnn')
            if os.path.exists(tf_path):
                self.models['dnn'] = tf.keras.models.load_model(tf_path)
                print(f"[ML] Loaded TensorFlow DNN model")
        except Exception as e:
            print(f"[ML] Error loading TensorFlow model: {e}")
            
        # Load other models using joblib
        for model_type in ['xgboost', 'random_forest', 'svm']:
            try:
                model_path = os.path.join(self.base_path, f"{model_type}.joblib")
                if os.path.exists(model_path):
                    self.models[model_type] = joblib.load(model_path)
                    print(f"[ML] Loaded {model_type} model")
            except Exception as e:
                print(f"[ML] Error loading {model_type} model: {e}")
    
    def create_default_models(self, input_shape: Tuple = (10,)):
        """
        Create default models if they don't exist
        
        Args:
            input_shape: Input shape for models
        """
        # Create DNN if not loaded
        if 'dnn' not in self.models:
            try:
                import tensorflow as tf
                
                dnn = tf.keras.Sequential([
                    tf.keras.layers.Dense(128, activation='relu', input_shape=input_shape),
                    tf.keras.layers.Dropout(0.2),
                    tf.keras.layers.Dense(64, activation='relu'),
                    tf.keras.layers.Dropout(0.1),
                    tf.keras.layers.Dense(32, activation='relu'),
                    tf.keras.layers.Dense(3, activation='softmax')  # Hold, Buy, Sell
                ])
                
                dnn.compile(
                    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                    loss='sparse_categorical_crossentropy',
                    metrics=['accuracy']
                )
                
                self.models['dnn'] = dnn
                print("[ML] Created default TensorFlow DNN model")
            except Exception as e:
                print(f"[ML] Error creating TensorFlow model: {e}")
        
        # Create XGBoost model if not loaded
        if 'xgboost' not in self.models:
            try:
                import xgboost as xgb
                xgb_model = xgb.XGBClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=5,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    objective='multi:softprob',
                    num_class=3
                )
                self.models['xgboost'] = xgb_model
                print("[ML] Created default XGBoost model")
            except Exception as e:
                print(f"[ML] Could not create XGBoost model: {e}")
        
        # Create Random Forest model if not loaded
        if 'random_forest' not in self.models:
            try:
                from sklearn.ensemble import RandomForestClassifier
                rf_model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                self.models['random_forest'] = rf_model
                print("[ML] Created default Random Forest model")
            except Exception as e:
                print(f"[ML] Could not create Random Forest model: {e}")
        
        # Create SVM model if not loaded
        if 'svm' not in self.models:
            try:
                from sklearn.svm import SVC
                svm_model = SVC(
                    probability=True,
                    kernel='rbf',
                    C=1.0,
                    random_state=42
                )
                self.models['svm'] = svm_model
                print("[ML] Created default SVM model")
            except Exception as e:
                print(f"[ML] Could not create SVM model: {e}")
    
    def predict(self, features: np.ndarray) -> Dict[str, Any]:
        """
        Make predictions using all available models and combine results
        
        Args:
            features: Input features (batch_size, feature_count)
            
        Returns:
            Dictionary with prediction results
        """
        start_time = time.time()
        
        # Ensure we have models to use
        if not self.models:
            self.create_default_models()
            
        # If still no models, return default prediction
        if not self.models:
            return {
                'action': 0,  # Default to HOLD
                'confidence': 0.6,
                'ensemble_used': False,
                'reasoning': "No models available - using default prediction"
            }
        
        # Initialize arrays for predictions and confidence
        predictions = []
        confidences = []
        model_details = {}
        
        # Predict with TensorFlow DNN
        if 'dnn' in self.models:
            try:
                # Ensure features are properly shaped for TF
                tf_features = features.reshape(-1, features.shape[-1]) if len(features.shape) == 1 else features
                
                # Get prediction probabilities
                tf_prediction = self.models['dnn'].predict(tf_features, verbose=0)
                
                # Get class and confidence
                dnn_class = int(np.argmax(tf_prediction[0]))
                dnn_confidence = float(tf_prediction[0][dnn_class])
                
                # Store for ensemble
                predictions.append(dnn_class)
                confidences.append(dnn_confidence)
                
                # Store details
                model_details['dnn'] = {
                    'prediction': dnn_class,
                    'confidence': dnn_confidence,
                    'probabilities': tf_prediction[0].tolist()
                }
            except Exception as e:
                print(f"[ML] DNN prediction error: {e}")
        
        # Predict with other models
        for model_type in ['xgboost', 'random_forest', 'svm']:
            if model_type in self.models:
                try:
                    # Ensure features are properly shaped for sklearn
                    sk_features = features.reshape(1, -1) if len(features.shape) == 1 else features
                    
                    # Get prediction probabilities
                    sk_probabilities = self.models[model_type].predict_proba(sk_features)
                    
                    # Get class and confidence
                    sk_class = int(np.argmax(sk_probabilities[0]))
                    sk_confidence = float(sk_probabilities[0][sk_class])
                    
                    # Store for ensemble
                    predictions.append(sk_class)
                    confidences.append(sk_confidence)
                    
                    # Store details
                    model_details[model_type] = {
                        'prediction': sk_class,
                        'confidence': sk_confidence,
                        'probabilities': sk_probabilities[0].tolist()
                    }
                except Exception as e:
                    print(f"[ML] {model_type} prediction error: {e}")
        
        # If no predictions were successful, return default
        if not predictions:
            return {
                'action': 0,  # Default to HOLD
                'confidence': 0.6,
                'ensemble_used': False,
                'reasoning': "All model predictions failed - using default prediction"
            }
        
        # Compute weighted ensemble prediction
        ensemble_probabilities = np.zeros(3)  # Hold, Buy, Sell
        
        total_weight = 0
        for model_type, details in model_details.items():
            if model_type in self.model_weights:
                weight = self.model_weights[model_type] * self.model_performance.get(model_type, 1.0)
                probabilities = np.array(details['probabilities'])
                ensemble_probabilities += probabilities * weight
                total_weight += weight
        
        if total_weight > 0:
            ensemble_probabilities /= total_weight
        
        # Get ensemble prediction and confidence
        ensemble_class = int(np.argmax(ensemble_probabilities))
        ensemble_confidence = float(ensemble_probabilities[ensemble_class])
        
        # Create reasoning from individual model predictions
        action_names = {0: "HOLD", 1: "BUY", 2: "SELL"}
        reasoning_parts = []
        
        # Add model-specific reasoning
        for model_type, details in model_details.items():
            action = action_names.get(details['prediction'], "UNKNOWN")
            confidence = details['confidence']
            reasoning_parts.append(f"{model_type.upper()}: {action} ({confidence:.1%})")
        
        # Add final ensemble decision
        reasoning = "Ensemble prediction based on: " + ", ".join(reasoning_parts)
        
        prediction_time = (time.time() - start_time) * 1000  # in milliseconds
        
        return {
            'action': ensemble_class,
            'confidence': ensemble_confidence,
            'action_probabilities': ensemble_probabilities.tolist(),
            'ensemble_used': True,
            'model_predictions': model_details,
            'reasoning': reasoning,
            'prediction_time_ms': prediction_time
        }
    
    def update_model_weights(self, feedback: Dict[str, bool]):
        """
        Update model weights based on prediction accuracy feedback
        
        Args:
            feedback: Dictionary mapping model type to success boolean
        """
        # Update individual model performance
        for model_type, success in feedback.items():
            if model_type in self.model_performance:
                # Exponential moving average of model performance
                current = self.model_performance[model_type]
                # Update with 10% learning rate
                self.model_performance[model_type] = current * 0.9 + (1.0 if success else 0.0) * 0.1
        
        # Normalize weights to sum to 1
        total = sum(self.model_weights[m] * self.model_performance.get(m, 1.0) for m in self.model_weights)
        if total > 0:
            normalized_weights = {}
            for model_type in self.model_weights:
                normalized_weights[model_type] = (self.model_weights[model_type] * 
                                                self.model_performance.get(model_type, 1.0)) / total
            
            # Only update if we have reasonable distribution
            if max(normalized_weights.values()) < 0.9:  # Prevent single model dominance
                self.model_weights = normalized_weights
    
    def save_models(self):
        """Save all ensemble models to disk"""
        print(f"[ML] Saving ensemble models to {self.base_path}")
        
        # Save TensorFlow DNN
        if 'dnn' in self.models:
            try:
                tf_path = os.path.join(self.base_path, 'dnn')
                self.models['dnn'].save(tf_path)
                print(f"[ML] Saved TensorFlow DNN model")
            except Exception as e:
                print(f"[ML] Error saving TensorFlow model: {e}")
        
        # Save other models using joblib
        for model_type in ['xgboost', 'random_forest', 'svm']:
            if model_type in self.models:
                try:
                    model_path = os.path.join(self.base_path, f"{model_type}.joblib")
                    joblib.dump(self.models[model_type], model_path)
                    print(f"[ML] Saved {model_type} model")
                except Exception as e:
                    print(f"[ML] Error saving {model_type} model: {e}")
        
        # Save weights and performance metrics
        try:
            metadata = {
                'model_weights': self.model_weights,
                'model_performance': self.model_performance,
                'last_updated': time.time()
            }
            meta_path = os.path.join(self.base_path, 'ensemble_metadata.joblib')
            joblib.dump(metadata, meta_path)
        except Exception as e:
            print(f"[ML] Error saving ensemble metadata: {e}")
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, validation_data: Optional[Tuple] = None):
        """
        Train all models in the ensemble
        
        Args:
            X_train: Training features
            y_train: Training labels
            validation_data: Optional validation data (X_val, y_val)
        """
        # Ensure we have models to train
        if not self.models:
            self.create_default_models(input_shape=(X_train.shape[1],))
        
        training_results = {}
        
        # Train TensorFlow DNN
        if 'dnn' in self.models:
            try:
                history = self.models['dnn'].fit(
                    X_train, y_train,
                    epochs=10,
                    batch_size=32,
                    validation_data=validation_data,
                    verbose=0
                )
                
                # Extract metrics
                val_acc = history.history.get('val_accuracy', [0])[-1] if validation_data else None
                training_results['dnn'] = {
                    'train_accuracy': history.history.get('accuracy', [0])[-1],
                    'val_accuracy': val_acc
                }
                print(f"[ML] Trained DNN - Accuracy: {history.history.get('accuracy', [0])[-1]:.4f}")
            except Exception as e:
                print(f"[ML] Error training TensorFlow model: {e}")
        
        # Train other models
        for model_type in ['xgboost', 'random_forest', 'svm']:
            if model_type in self.models:
                try:
                    self.models[model_type].fit(X_train, y_train)
                    
                    # Get training accuracy
                    train_acc = self.models[model_type].score(X_train, y_train)
                    val_acc = None
                    if validation_data:
                        X_val, y_val = validation_data
                        val_acc = self.models[model_type].score(X_val, y_val)
                    
                    training_results[model_type] = {
                        'train_accuracy': train_acc,
                        'val_accuracy': val_acc
                    }
                    print(f"[ML] Trained {model_type} - Accuracy: {train_acc:.4f}")
                except Exception as e:
                    print(f"[ML] Error training {model_type} model: {e}")
        
        # Save updated models
        self.save_models()
        
        return training_results