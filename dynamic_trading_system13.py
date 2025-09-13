import asyncio
import logging
from datetime import datetime
import random  # For simulating price movement
import pandas as pd

logging.basicConfig(
    format='[%(asctime)s] %(levelname)s %(message)s',
    level=logging.INFO
)

# -----------------------------
# Configuration
# -----------------------------
CONFLUENCE_THRESHOLD = 2  # Minimum strategies agreeing
DAILY_LOSS_LIMIT = 0.02   # Example: 2% of capital
CHECK_INTERVAL = 5         # seconds between price evaluations

# Example strategies with mock signals
STRATEGIES = ["structureBreak", "orderBlockBreakout", "liquidityGrab", "fibonacciReversal"]

# Portfolio to track open trades
active_trades = []
daily_loss = 0.0

# -----------------------------
# Helper Functions
# -----------------------------
def generate_signal():
    """
    Simulate strategy signals. Returns a dict with confluence strategies and confidence.
    """
    chosen_strategies = random.sample(STRATEGIES, k=random.randint(1, len(STRATEGIES)))
    direction = random.choice(["BUY", "SELL"])
    confidence = round(random.uniform(85, 105), 2)
    entry_price = round(random.uniform(1.195, 1.205), 5)
    sl = round(entry_price - 0.002 if direction=="BUY" else entry_price + 0.002, 5)
    tp = round(entry_price + 0.005 if direction=="BUY" else entry_price - 0.005, 5)

    return {
        "direction": direction,
        "strategies": chosen_strategies,
        "confidence": confidence,
        "entry": entry_price,
        "sl": sl,
        "tp": tp
    }

def open_trade(signal):
    trade = {
        "entry_time": datetime.now(),
        "direction": signal["direction"],
        "strategies": signal["strategies"],
        "confidence": signal["confidence"],
        "entry": signal["entry"],
        "sl": signal["sl"],
        "tp": signal["tp"]
    }
    active_trades.append(trade)
    logging.info(f"📊 TRADE OPENED: {trade['direction']} | Entry: {trade['entry']} | SL: {trade['sl']} | TP: {trade['tp']} | Confidence: {trade['confidence']}% | Strategies: {', '.join(trade['strategies'])}")

def close_trade(trade, current_price):
    global daily_loss
    if trade["direction"] == "BUY":
        pnl = current_price - trade["entry"]
    else:
        pnl = trade["entry"] - current_price

    daily_loss += min(0, -pnl)  # count only losses towards daily loss
    logging.info(f"✅ TRADE CLOSED: {trade['direction']} | PnL: {round(pnl, 5)} | Entry: {trade['entry']} | Exit: {current_price} | Strategies: {', '.join(trade['strategies'])}")
    active_trades.remove(trade)

def evaluate_trades(current_price):
    for trade in active_trades[:]:  # copy to avoid modification during iteration
        if trade["direction"] == "BUY":
            if current_price <= trade["sl"] or current_price >= trade["tp"]:
                close_trade(trade, current_price)
        else:
            if current_price >= trade["sl"] or current_price <= trade["tp"]:
                close_trade(trade, current_price)

# -----------------------------
# Main Loop
# -----------------------------
async def main():
    global daily_loss
    while True:
        # Simulate current market price
        current_price = round(random.uniform(1.195, 1.205), 5)

        # Generate signal
        signal = generate_signal()

        # Check confluence before opening
        if len(signal["strategies"]) >= CONFLUENCE_THRESHOLD:
            if daily_loss < DAILY_LOSS_LIMIT:
                open_trade(signal)
            else:
                logging.warning("⚠️ Daily loss limit reached. Halting new trades for today.")
        else:
            logging.info("INFO No confluence, waiting for next evaluation.")

        # Evaluate open trades against current price
        evaluate_trades(current_price)

        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
