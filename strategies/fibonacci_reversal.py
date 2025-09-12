# File: fibonacci_reversal.py
import numpy as np
import pandas as pd
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import logging
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s [%(asctime)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Enums
class MarketRegime(Enum):
    TRENDING = "trending"
    RANGING = "ranging"
    VOLATILE = "volatile"

class TradeType(Enum):
    BUY = "buy"
    SELL = "sell"

# Signal dataclass
@dataclass
class Signal:
    strategy: str
    signal_type: TradeType
    entry: float
    stop_loss: float
    take_profit: float
    confidence: float
    weight: float
    market_regime: MarketRegime
    timestamp: datetime

# ATR Calculation
def calculate_atr(data: pd.DataFrame, period=14) -> float:
    high_low = data['high'] - data['low']
    high_close = abs(data['high'] - data['close'].shift())
    low_close = abs(data['low'] - data['close'].shift())
    tr = np.maximum(high_low, np.maximum(high_close, low_close))
    return tr.rolling(period).mean().iloc[-1]

# RSI Calculation
def calculate_rsi(data: pd.DataFrame, period=14) -> float:
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs)).iloc[-1]

# Market regime detection
def detect_market_regime(data: pd.DataFrame) -> MarketRegime:
    if len(data) < 50:
        return MarketRegime.TRENDING
    recent = data.tail(50)
    prices = recent['close'].values
    returns = np.diff(prices)/prices[:-1]
    volatility = np.std(returns)
    trend = (prices[-1]-prices[0])/prices[0]
    if abs(trend) > 0.02 and volatility < 0.015:
        return MarketRegime.TRENDING
    elif abs(trend) < 0.01 and volatility < 0.012:
        return MarketRegime.RANGING
    else:
        return MarketRegime.VOLATILE

# Simulated historical market data
def get_historical_data(periods=200) -> pd.DataFrame:
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='5min')
    price = 1.2000
    data = []
    for date in dates:
        price += np.random.normal(0, 0.0008)
        volume = np.random.randint(500, 1500)
        data.append({
            'timestamp': date,
            'open': price,
            'high': price + abs(np.random.normal(0, 0.0003)),
            'low': price - abs(np.random.normal(0, 0.0003)),
            'close': price,
            'volume': volume
        })
    return pd.DataFrame(data)

# Fibonacci Reversal Strategy
def fibonacci_reversal(data: pd.DataFrame, regime: MarketRegime, weight: float) -> Optional[Signal]:
    if np.random.random() > 0.25:  # 25% chance
        return None
    current_price = data['close'].iloc[-1]
    atr = calculate_atr(data)
    rsi = calculate_rsi(data)
    signal_type = TradeType.BUY if rsi < 50 else TradeType.SELL
    if signal_type == TradeType.BUY:
        stop_loss = current_price - (atr * 1.8)
        take_profit = current_price + (atr * 3.6)
    else:
        stop_loss = current_price + (atr * 1.8)
        take_profit = current_price - (atr * 3.6)
    confidence = 70 + abs(50 - rsi)
    return Signal(
        strategy="fibonacciReversal",
        signal_type=signal_type,
        entry=current_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        confidence=confidence,
        weight=weight,
        market_regime=regime,
        timestamp=datetime.now()
    )

# ===============================
# Example standalone execution
# ===============================
async def main():
    logger.info("🚀 Fibonacci Reversal Strategy Test Starting...")
    data = get_historical_data()
    regime = detect_market_regime(data)
    while True:
        signal = fibonacci_reversal(data, regime, weight=0.25)
        if signal:
            logger.info(f"📊 SIGNAL GENERATED: {signal.strategy} {signal.signal_type.value.upper()} | "
                        f"Entry: {signal.entry:.5f} | SL: {signal.stop_loss:.5f} | TP: {signal.take_profit:.5f} | "
                        f"Confidence: {signal.confidence:.1f}%")
        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
