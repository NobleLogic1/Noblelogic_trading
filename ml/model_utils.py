import numpy as np
from sklearn.metrics import classification_report

def reshape_features(df):
    features = ["return", "sma", "ema", "rsi", "bb_upper", "bb_lower", "momentum"]
    X = df[features].values
    y = df["direction"].values
    return X, y

def evaluate_model(model, X, y):
    preds = model.predict(X)
    print(classification_report(y, preds))