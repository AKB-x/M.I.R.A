import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

instruments = ["SPY", "GLD"]

for symbol in instruments:
    print(f"\nProcessing {symbol}...")

    file_path = RAW_DIR / f"{symbol}.csv"

    df = pd.read_csv(
        file_path,
        index_col="Date",
        parse_dates=True
    )
    df.columns = (df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    print("\nStandardized columns:")
    print(df.columns.tolist())
    output_path = PROCESSED_DIR / f"{symbol}.csv"

    df.to_csv(output_path)

    print(f"Saved processed data: {output_path}")
    print("Final shape:", df.shape)
    print("Loaded successfully:", df.shape)
    print(df.head(3))