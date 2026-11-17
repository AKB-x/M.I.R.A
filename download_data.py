import yfinance as yf
from pathlib import Path

# Define the directory for storing raw market data
DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Financial instruments
instruments = ["SPY", "GLD"]

# Download the historical data for each instrument 
for symbol in instruments:

    print(f"Downloading {symbol}...")

    df = yf.download(
        symbol,
        period="5y",
        interval="1d",
        auto_adjust=False,
        progress=False,
        multi_level_index=False
    )

    if df.empty:
        raise ValueError(f"No data received for {symbol}")

    df.index.name = "Date"

    # Save data as CSV
    output_path = DATA_DIR / f"{symbol}.csv"
    df.to_csv(output_path)

    print(f"Saved: {output_path}")
    print(f"Rows downloaded: {len(df)}")
    print(df.head())
