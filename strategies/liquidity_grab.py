# File: liquidity_grab.py
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

# Liquidity Grab Strategy
def liquidity_grab(data: pd.DataFrame, regime: MarketRegime, weight: float) -> Optional[Signal]:
    if np.random.random() > 0.2:  # 20% chance
        return None
    current_price = data['close'].iloc[-1]
    atr = calculate_atr(data)
    signal_type = TradeType.SELL if np.random.random() > 0.5 else TradeType.BUY
    if signal_type == TradeType.BUY:
        stop_loss = current_price - (atr * 1.5)
        take_profit = current_price + (atr * 3)
    else:
        stop_loss = current_price + (atr * 1.5)
        take_profit = current_price - (atr * 3)
    confidence = 80 + (weight * 40)
    return Signal(
        strategy="liquidityGrab",
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
    logger.info("🚀 Liquidity Grab Strategy Test Starting...")
    data = get_historical_data()
    regime = detect_market_regime(data)
    while True:
        signal = liquidity_grab(data, regime, weight=0.25)
        if signal:
            logger.info(f"📊 SIGNAL GENERATED: {signal.strategy} {signal.signal_type.value.upper()} | "
                        f"Entry: {signal.entry:.5f} | SL: {signal.stop_loss:.5f} | TP: {signal.take_profit:.5f} | "
                        f"Confidence: {signal.confidence:.1f}%")
        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
