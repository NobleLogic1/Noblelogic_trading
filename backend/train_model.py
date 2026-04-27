import json
import os
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

TRADE_LOG_PATH = os.path.join(BASE_DIR, 'trade_log.json')
STRATEGY_OUTPUT_PATH = os.path.join(BASE_DIR, 'strategy_output.json')
HEALTH_STATUS_PATH = os.path.join(BASE_DIR, 'health_status.json')

def load_trades():
    if not os.path.exists(TRADE_LOG_PATH):
        return []
    try:
        with open(TRADE_LOG_PATH, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def run_model(trades):
    if not trades:
        return None, None

    # Ensure we have enough data for training
    if len(trades) < 3:
        print("Warning: Not enough trades for ML training (need at least 3)")
        return None, None

    X = []
    y = []
    le_strategy = LabelEncoder()
    le_direction = LabelEncoder()

    strategies = [t['strategy'] for t in trades]
    directions = [t['direction'] for t in trades]

    # Check if we have multiple unique values for encoding
    if len(set(strategies)) < 2 or len(set(directions)) < 2:
        print("Warning: Need at least 2 unique strategies and directions for ML training")
        return None, None

    strategy_encoded = le_strategy.fit_transform(strategies)
    direction_encoded = le_direction.fit_transform(directions)

    for i, t in enumerate(trades):
        X.append([
            t['confidence'],
            t['pnl'],
            strategy_encoded[i]
        ])
        y.append(direction_encoded[i])

    # Ensure we have enough data for train/test split
    test_size = min(0.3, (len(trades) - 1) / len(trades))
    if test_size <= 0:
        test_size = 0.3

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = round(accuracy_score(y_test, y_pred), 2)

    avg_confidence = round(sum(t['confidence'] for t in trades) / len(trades), 2)
    most_common_strategy = max(set(strategies), key=strategies.count)

    return {
        "strategy": most_common_strategy,
        "confidence": avg_confidence,
        "active": True
    }, {
        "accuracy": accuracy,
        "status": "Stable" if accuracy > 0.8 else "Needs Review"
    }

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == '__main__':
    print(f"[{datetime.now()}] Running ML model with scikit-learn...")
    trades = load_trades()
    strategy_data, health_data = run_model(trades)

    if strategy_data and health_data:
        save_json(STRATEGY_OUTPUT_PATH, strategy_data)
        save_json(HEALTH_STATUS_PATH, health_data)
        print("✅ Strategy and health data updated.")
    else:
        print("⚠️ No trades found. ML model skipped.")