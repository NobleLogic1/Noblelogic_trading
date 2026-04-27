import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from shared_utils import updateStrategyOutput, updateHealthStatus

# Simulated data
df = pd.DataFrame({
    'open': np.random.rand(100),
    'high': np.random.rand(100),
    'low': np.random.rand(100),
    'close': np.random.rand(100),
    'volume': np.random.randint(1000, 5000, 100),
    'target': np.random.randint(0, 2, 100)
})

X = df[['open', 'high', 'low', 'close', 'volume']]
y = df['target']

model = RandomForestClassifier()
model.fit(X, y)
preds = model.predict(X)
acc = accuracy_score(y, preds)

# Save strategy output - note the different format to match frontend expectations
strategy = {
    'strategy': 'Momentum',
    'confidence': round(acc * 100, 2),
    'active': acc > 0.7
}
updateStrategyOutput(strategy)

# Save health status
status = 'Optimal' if acc > 0.75 else 'Needs Review'
updateHealthStatus({'accuracy': round(acc * 100, 2), 'status': status})