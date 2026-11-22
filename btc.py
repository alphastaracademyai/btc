
import csv
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import yfinance as yf

price = float(yf.Ticker("BTC-USD").history(period="1d", interval="5m")["Close"].iloc[-1])
now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

with open("btc_prices.csv", "a", newline="") as file:
    csv.writer(file).writerow([now, f"{price:.2f}"])

with open("btc_prices.csv", newline="") as file:
    rows = list(csv.DictReader(file))

times = [datetime.fromisoformat(row["time_utc"].replace("Z", "+00:00")) for row in rows]
prices = [float(row["price_usd"]) for row in rows]

# Plot all prices.
plt.figure(figsize=(9, 4))
plt.plot(times, prices, marker="o")
plt.title("BTC-USD Price")
plt.xlabel("Time (UTC)")
plt.ylabel("Price (USD)")
plt.grid(alpha=0.3)
plt.gcf().autofmt_xdate()
plt.tight_layout()
plt.savefig("btc_chart.png", dpi=140)
plt.close()

print(f"Recorded BTC price: ${price:,.2f}")
