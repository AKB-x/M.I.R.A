import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/processed")
instruments = ["SPY", "GLD"]

RETURN_THRESHOLD = 3.0

for symbol in instruments:
    df = pd.read_csv(
        DATA_DIR / f"{symbol}_returns.csv",
        index_col="Date",
        parse_dates=True
    )

    print(f"\nRisk analysis for {symbol}")
    print("Dataset shape:", df.shape)

    print("\nAvailable columns:")
    print(df.columns.tolist())

    # Detect large daily price movements
    df["large_move_alert"] = (
        df["daily_return"].abs() >= RETURN_THRESHOLD
    )

    print(f"\nLarge price movements for {symbol}:")

    large_moves = df[df["large_move_alert"]]
    print(
        large_moves[["daily_return", "large_move_alert"]]
        .tail(10)
        .to_string()
    )
    print("\nTotal large-move alerts:", len(large_moves))
    # Rule 2: Detect movements relative to recent volatility
    VOLATILITY_MULTIPLIER = 2.0

    df["volatility_threshold"] = (
        VOLATILITY_MULTIPLIER
        * df["rolling_volatility_20d"].shift(1)
    )

    df["volatility_adjusted_alert"] = (
        df["daily_return"].abs() >= df["volatility_threshold"]
    )

    volatility_alerts = df[df["volatility_adjusted_alert"]]

    print(f"\nVolatility-adjusted alerts for {symbol}:")

    print(
        volatility_alerts[
            [
                "daily_return",
                "volatility_threshold",
                "volatility_adjusted_alert"
        ]
    ].tail(10).to_string()
    )

    print(
        "\nTotal volatility-adjusted alerts:",
        len(volatility_alerts)
    )  

    # Rule 3: RSI extreme detection
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30

    df["rsi_signal"] = "neutral"

    df.loc[
        df["rsi_14"] > RSI_OVERBOUGHT,
        "rsi_signal"
    ] = "overbought"

    df.loc[
        df["rsi_14"] < RSI_OVERSOLD,
        "rsi_signal"
    ] = "oversold"

    # Initial periods do not have enough data for RSI
    df.loc[
        df["rsi_14"].isna(),
        "rsi_signal"
    ] = "unavailable"

    rsi_alerts = df[
        df["rsi_signal"].isin(["overbought", "oversold"])
    ]

    print(f"\nRSI extreme alerts for {symbol}:")

    print(
        rsi_alerts[["rsi_14", "rsi_signal"]]
        .tail(10)
        .to_string()
    )

    print("\nRSI signal counts:")
    print(df["rsi_signal"].value_counts().to_string())

    # Save asset-level risk signals
    output_path = DATA_DIR / f"{symbol}_risk_signals.csv"

    df.to_csv(output_path)

    print(f"\nSaved risk signals: {output_path}")
    print("Final shape:", df.shape)

# Rule 4: Cross-asset correlation monitoring
correlation_df = pd.read_csv(
    DATA_DIR / "SPY_GLD_correlation_20d.csv",
    index_col="Date",
    parse_dates=True
)

print("\nCross-asset correlation analysis")
print("Dataset shape:", correlation_df.shape)

print("\nAvailable columns:")
print(correlation_df.columns.tolist())

print("\nLatest correlation values:")
print(
    correlation_df[["rolling_correlation_20d"]]
    .tail(5)
    .to_string()
)    

# Rule 4: Detect significant correlation changes

CORRELATION_CHANGE_THRESHOLD = 0.40
CORRELATION_LOOKBACK = 5

# Calculate change over the previous 5 trading days
correlation_df["correlation_change_5d"] = (
    correlation_df["rolling_correlation_20d"]
    - correlation_df["rolling_correlation_20d"].shift(
        CORRELATION_LOOKBACK
    )
)

# Flag significant changes in either direction
correlation_df["correlation_shift_alert"] = (
    correlation_df["correlation_change_5d"].abs()
    >= CORRELATION_CHANGE_THRESHOLD
)

correlation_alerts = correlation_df[
    correlation_df["correlation_shift_alert"]
]

print("\nSignificant correlation shifts:")

print(
    correlation_alerts[
        [
            "rolling_correlation_20d",
            "correlation_change_5d",
            "correlation_shift_alert"
        ]
    ].tail(10).to_string()
)

print("\nTotal correlation shift alerts:",
    len(correlation_alerts)
)

# Save cross-asset correlation risk signals
correlation_output = DATA_DIR / "SPY_GLD_correlation_signals.csv"

correlation_df.to_csv(correlation_output)

print(f"\nSaved correlation signals: {correlation_output}")
print("Final shape:", correlation_df.shape)