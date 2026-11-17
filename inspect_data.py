import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")

instruments = ["SPY", "GLD"]

for symbol in instruments:
    print("\n" + "=" * 50)
    print(f"DATA INSPECTION: {symbol}")
    print("=" * 50)

    file_path = DATA_DIR / f"{symbol}.csv"
    df = pd.read_csv(file_path, index_col="Date", parse_dates=True)

    # 1. Display first five records
    print("\nFirst 5 records:")
    print(df.head())

    # 2. Dataset dimensions
    print("\nDataset shape:")
    print(df.shape)

    # 3. Column names and data types
    print("\nDataset information:")
    df.info()

    # 4. Missing values
    print("\nMissing values:")
    print(df.isnull().sum())

    # 5. Duplicate dates
    print("\nDuplicate dates:")
    print(df.index.duplicated().sum())

    # 6. Date range
    print("\nDate range:")
    print("Start:", df.index.min())
    print("End:", df.index.max())

    # 7. Negative or zero values
    print("\nNon-positive values:")
    print((df.select_dtypes(include="number") <= 0).sum())

    # 8. OHLC consistency checks
    invalid_high = (
        df["High"] < df[["Open", "Close"]].max(axis=1)
    )

    invalid_low = (
        df["Low"] > df[["Open", "Close"]].min(axis=1)
    )

    invalid_ohlc = invalid_high | invalid_low

    print("\nOHLC validation:")
    print("Invalid OHLC records:", invalid_ohlc.sum())

    # 9. Negative volume check
    print("\nNegative volume records:")
    print((df["Volume"] < 0).sum())

    # 10. Chronological ordering
    print("\nDates sorted chronologically:")
    print(df.index.is_monotonic_increasing)


# Cross-instrument date alignment
spy = pd.read_csv(
    DATA_DIR / "SPY.csv",
    index_col="Date",
    parse_dates=True
)

gld = pd.read_csv(
    DATA_DIR / "GLD.csv",
    index_col="Date",
    parse_dates=True
)

print("\n" + "=" * 50)
print("CROSS-INSTRUMENT DATE ALIGNMENT")
print("=" * 50)

print("SPY dates:", len(spy.index))
print("GLD dates:", len(gld.index))

print("Are date indexes identical:",
      spy.index.equals(gld.index))

print("Dates present in SPY but missing in GLD:",
      len(spy.index.difference(gld.index)))

print("Dates present in GLD but missing in SPY:",
      len(gld.index.difference(spy.index)))