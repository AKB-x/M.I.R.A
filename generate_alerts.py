import json
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/processed")
instruments = ["SPY", "GLD"]
alerts = []

for symbol in instruments:
    df = pd.read_csv(
        DATA_DIR / f"{symbol}_risk_signals.csv",
        index_col="Date",
        parse_dates=True
    )

    print(f"\nGenerating alerts for {symbol}")
    print("Dataset shape:", df.shape)

    #1: Large daily price movements
    large_moves = df[df["large_move_alert"]]

    for date, row in large_moves.iterrows():
        daily_return = float(row["daily_return"])

        alert = {
            "symbol": symbol,
            "date": date.strftime("%Y-%m-%d"),
            "alert_type": "large_price_move",
            "severity": "high" if abs(daily_return) >= 5.0 else "medium",
            "observed_value": round(daily_return, 4),
            "threshold": 3.0,
            "message": (
                f"{symbol} moved {daily_return:+.2f}% "
                f"on {date.strftime('%Y-%m-%d')}, "
                f"exceeding the 3% daily movement threshold."
            )
        }

        alerts.append(alert)

    #2: Volatility-adjusted price movements
    volatility_moves = df[df["volatility_adjusted_alert"]]

    for date, row in volatility_moves.iterrows():
        daily_return = float(row["daily_return"])
        threshold = float(row["volatility_threshold"])
        ratio = abs(daily_return) / threshold if threshold > 0 else 0

        alert = {
            "symbol": symbol,
            "date": date.strftime("%Y-%m-%d"),
            "alert_type": "volatility_adjusted_move",
            "severity": "high" if ratio >= 3.0 else "medium",
            "observed_value": round(daily_return, 4),
            "threshold": round(threshold, 4),
            "message": (
                f"{symbol} moved {daily_return:+.2f}% "
                f"on {date.strftime('%Y-%m-%d')}, "
                f"exceeding its volatility-adjusted threshold "
                f"of {threshold:.2f}%."
            )
        }

        alerts.append(alert)

    #3: RSI extreme conditions
    rsi_extremes = df[
        df["rsi_signal"].isin(["overbought", "oversold"])
    ]

    for date, row in rsi_extremes.iterrows():
        signal = row["rsi_signal"]
        rsi_value = float(row["rsi_14"])
        threshold = 70 if signal == "overbought" else 30

        if signal == "overbought":
            severity = "high" if rsi_value >= 80 else "medium"
        else:
            severity = "high" if rsi_value <= 20 else "medium"

        alert = {
            "symbol": symbol,
            "date": date.strftime("%Y-%m-%d"),
            "alert_type": f"rsi_{signal}",
            "severity": severity,
            "observed_value": round(rsi_value, 4),
            "threshold": threshold,
            "message": (
                f"{symbol} recorded an RSI of {rsi_value:.2f} "
                f"on {date.strftime('%Y-%m-%d')}, "
                f"indicating an {signal} momentum condition "
                f"relative to the RSI threshold of {threshold}."
            )
        }

        alerts.append(alert)


#4: Cross-asset correlation shifts
correlation_df = pd.read_csv(
    DATA_DIR / "SPY_GLD_correlation_signals.csv",
    index_col="Date",
    parse_dates=True
)

correlation_shifts = correlation_df[
    correlation_df["correlation_shift_alert"]
]

for date, row in correlation_shifts.iterrows():
    correlation_change = float(row["correlation_change_5d"])
    current_correlation = float(row["rolling_correlation_20d"])

    alert = {
        "symbol": "SPY-GLD",
        "date": date.strftime("%Y-%m-%d"),
        "alert_type": "correlation_shift",
        "severity": (
            "high" if abs(correlation_change) >= 0.60 else "medium"
        ),
        "observed_value": round(correlation_change, 4),
        "threshold": 0.40,
        "message": (
            f"SPY-GLD rolling correlation changed by "
            f"{correlation_change:+.2f} over five trading days "
            f"on {date.strftime('%Y-%m-%d')}. "
            f"The current 20-day correlation is "
            f"{current_correlation:+.2f}, and the absolute "
            f"change exceeded the 0.40 threshold."
        )
    }

    alerts.append(alert)


# Sort alerts chronologically, newest first
alerts.sort(
    key=lambda alert: alert["date"],
    reverse=True
)

# Display summary
print("\nTotal structured alerts:", len(alerts))

print("\nAlerts by type:")
alert_counts = pd.Series(
    [alert["alert_type"] for alert in alerts]
).value_counts()
print(alert_counts.to_string())

print("\nAlerts by severity:")
severity_counts = pd.Series(
    [alert["severity"] for alert in alerts]
).value_counts()
print(severity_counts.to_string())

print("\nLatest 3 alerts:")
for alert in alerts[:3]:
    print(alert)


# Save alerts as JSON for future FastAPI endpoints
output_path = DATA_DIR / "alerts.json"

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(alerts, file, indent=4)

print(f"\nSaved structured alerts: {output_path}")
print("Total saved alerts:", len(alerts))
