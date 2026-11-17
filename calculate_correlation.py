import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/processed")

spy = pd.read_csv(
    DATA_DIR / "SPY_returns.csv",
    index_col="Date",
    parse_dates=True
)

gld = pd.read_csv(
    DATA_DIR / "GLD_returns.csv",
    index_col="Date",
    parse_dates=True
)

print("SPY shape:", spy.shape)
print("GLD shape:", gld.shape)

print("Dates aligned:", spy.index.equals(gld.index))
# Combine daily returns from both assets
returns = pd.DataFrame({
    "SPY_return": spy["daily_return"],
    "GLD_return": gld["daily_return"]
})

print("\nCombined daily returns:")
print(returns.head(6))

print("\nCombined dataset shape:", returns.shape)
print("\nMissing values:")
print(returns.isna().sum())

# Calculate 20-trading-day rolling correlation
returns["rolling_correlation_20d"] = (
    returns["SPY_return"]
    .rolling(window=20)
    .corr(returns["GLD_return"])
)

print("\n20-day rolling correlation:")
print(returns.tail(10).to_string())

print("\nCorrelation minimum:", returns["rolling_correlation_20d"].min())
print("Correlation maximum:", returns["rolling_correlation_20d"].max())
print("Missing values:", returns["rolling_correlation_20d"].isna().sum())

# Save the rolling correlation results
output_path = DATA_DIR / "SPY_GLD_correlation_20d.csv"

returns.to_csv(output_path)

print(f"\nSaved: {output_path}")
print("Final dataset shape:", returns.shape)
print("First valid correlation date:",
    returns["rolling_correlation_20d"].first_valid_index()
)