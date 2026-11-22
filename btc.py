import csv
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

FOLDER = Path(__file__).parent
CSV_FILE = FOLDER / "btc_prices.csv"
PNG_FILE = FOLDER / "btc_chart.png"


def get_price():
    import yfinance as yf

    data = yf.Ticker("BTC-USD").history(
        period="1d", interval="5m", timeout=20, raise_errors=True
    )
    if data.empty or data["Close"].dropna().empty:
        raise RuntimeError("Yahoo Finance did not return a BTC-USD price")

    closes = data["Close"].dropna()
    price = float(closes.iloc[-1])
    timestamp = closes.index[-1].to_pydatetime().astimezone(timezone.utc)

    if not math.isfinite(price) or price <= 0:
        raise RuntimeError("Yahoo Finance returned an invalid BTC-USD price")
    if datetime.now(timezone.utc) - timestamp > timedelta(minutes=90):
        raise RuntimeError("Yahoo Finance returned a stale BTC-USD price")

    return timestamp, price


def read_prices():
    with CSV_FILE.open(newline="", encoding="utf-8") as file:
        return [
            (datetime.fromisoformat(row["time_utc"].replace("Z", "+00:00")),
             float(row["price_usd"]))
            for row in csv.DictReader(file)
        ]


def save_price(timestamp, price):
    previous = read_prices()
    if previous and timestamp <= previous[-1][0]:
        return False

    with CSV_FILE.open("a", newline="", encoding="utf-8") as file:
        csv.writer(file).writerow([
            timestamp.isoformat(timespec="seconds").replace("+00:00", "Z"),
            f"{price:.2f}",
        ])
    return True


def make_chart():
    prices = read_prices()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    fig.patch.set_facecolor("white")

    if prices:
        cutoff = prices[-1][0] - timedelta(days=7)
        recent = [(time, price) for time, price in prices if time >= cutoff]
        times, values = zip(*recent)
        ax.plot(times, values, color="#3182bd", linewidth=2)
        ax.scatter(times[-1], values[-1], color="#3182bd", s=32, zorder=3)
        ax.set_title(f"BTC / USD     ${values[-1]:,.2f}", loc="left", fontsize=17, pad=17)
        ax.set_xlabel("Time (UTC)")
        ax.set_ylabel("Price (USD)")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d\n%H:%M", tz=timezone.utc))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value:,.0f}"))
        ax.grid(axis="y", color="#e5edf4")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.margins(x=0.06, y=0.12)
    else:
        ax.text(0.5, 0.5, "No BTC prices yet. Run the GitHub workflow.",
                ha="center", va="center", transform=ax.transAxes, fontsize=12)
        ax.set_axis_off()
        ax.set_title("BTC / USD", loc="left", fontsize=17, pad=17)

    fig.tight_layout()
    fig.savefig(PNG_FILE, dpi=140)
    plt.close(fig)


timestamp, price = get_price()
saved = save_price(timestamp, price)
make_chart()
print(f"BTC-USD: ${price:,.2f} at {timestamp:%Y-%m-%d %H:%M UTC}")
print("Saved a new observation" if saved else "This price was already recorded")


