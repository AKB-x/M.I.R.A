import pandas as pd
from pathlib import Path
import numpy as np

DATA_DIR = Path("data/processed")

instruments = ["SPY", "GLD"]

for symbol in instruments:
    print(f"\nCalculating returns for {symbol}...")

    df = pd.read_csv(
        DATA_DIR / f"{symbol}.csv",
        index_col="Date",
        parse_dates=True
    )

    # Calculate daily returns
    df["daily_return"] = df["adj_close"].pct_change() * 100

    # Calculate log returns
    df["log_return"] = np.log(
    df["adj_close"] / df["adj_close"].shift(1)) * 100
    
    # Calculate rolling volatility over a 20-day window
    df["rolling_volatility_20d"] = (df["daily_return"].rolling(window=20).std())

    # Calculate annualized volatility
    df["annualized_volatility_20d"] = (df["rolling_volatility_20d"] * np.sqrt(252))

    # Calculate SMA over a 20-day window
    df["sma_20"] = df["adj_close"].rolling(window=20).mean()

    # Calculate EMA over a 20-day window
    df["ema_20"] = (df["adj_close"].ewm(span=20, adjust=False).mean())

    # Calculate RSI
    delta=df["adj_close"].diff()
    gain=delta.clip(lower=0)
    loss=-delta.clip(upper=0)
    period = 14

    initial_avg_gain = gain.iloc[1:period + 1].mean()
    initial_avg_loss = loss.iloc[1:period + 1].mean()

    print(f"\nInitial RSI averages for {symbol}:")
    print(f"Average gain: {initial_avg_gain:.6f}")
    print(f"Average loss: {initial_avg_loss:.6f}")

    # Wilder's smoothing method for RSI
    avg_gain = pd.Series(np.nan, index=df.index)
    avg_loss = pd.Series(np.nan, index=df.index)

    # Initials at the end of the first period
    avg_gain.iloc[period] = initial_avg_gain
    avg_loss.iloc[period] = initial_avg_loss

    for i in range(period + 1, len(df)):
        avg_gain.iloc[i] = (
            (avg_gain.iloc[i - 1] * (period - 1) + gain.iloc[i])
            / period
        )

        avg_loss.iloc[i] = (
            (avg_loss.iloc[i - 1] * (period - 1) + loss.iloc[i])
            / period
        )

    # Calculate RSI(14) from Wilder's smoothed averages
    total_movement = avg_gain + avg_loss

    df["rsi_14"] = 100 * avg_gain / total_movement

    # Handle periods with no price movement
    df.loc[(total_movement == 0) & total_movement.notna(),"rsi_14"] = 50

    print(f"\nWilder smoothing inspection: {symbol}")

    print(
            pd.DataFrame({
            "gain": gain,
            "loss": loss,
            "avg_gain": avg_gain,
            "avg_loss": avg_loss
        }).iloc[13:18].to_string()
    )

    print(f"\nRSI(14) verification: {symbol}")

    print(
        df[["adj_close", "rsi_14"]]
        .tail(5)
        .to_string()
    )

    print("RSI minimum:", df["rsi_14"].min())
    print("RSI maximum:", df["rsi_14"].max())
    print("RSI missing values:", df["rsi_14"].isna().sum())

    # Save the results to new CSV files
    output_path = DATA_DIR / f"{symbol}_returns.csv"
    df.to_csv(output_path)

    print(f"Saved: {output_path}")
    print("Dataset shape:", df.shape)
    print(df[["adj_close", "daily_return", "log_return", "rolling_volatility_20d", "annualized_volatility_20d", "sma_20", "ema_20"]].tail(21))

    print(f"\nRSI gain/loss inspection: {symbol}")

    print(
    pd.DataFrame({
        "adj_close": df["adj_close"],
        "delta": delta,
        "gain": gain,
        "loss": loss
    }).tail(5))

    

