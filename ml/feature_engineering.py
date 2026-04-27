import pandas as pd
import ta

def add_indicators(df):
    df["sma"] = ta.trend.sma_indicator(df["price"], window=14)
    df["ema"] = ta.trend.ema_indicator(df["price"], window=14)
    df["rsi"] = ta.momentum.rsi(df["price"], window=14)
    bb = ta.volatility.BollingerBands(df["price"], window=14)
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_lower"] = bb.bollinger_lband()
    df["momentum"] = ta.momentum.roc(df["price"], window=5)
    df.fillna(method="bfill", inplace=True)
    return df