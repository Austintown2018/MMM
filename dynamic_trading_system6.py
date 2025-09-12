# dynamic_trading_system_full.py
import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict

# === Logging setup ===
logging.basicConfig(level=logging.INFO, format='%(levelname)s [%(asctime)s] %(message)s')
logger = logging.getLogger(__name__)

# === Enums ===
class MarketRegime(Enum):
    TRENDING = "trending"
    RANGING = "ranging"
    VOLATILE = "volatile"

class TradeType(Enum):
    BUY = "buy"
    SELL = "sell"

# === Data classes ===
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

@dataclass
class Position:
    id: str
    strategy: str
    signal_type: TradeType
    entry: float
    stop_loss: float
    take_profit: float
    size: float
    entry_time: datetime
    unrealized_pnl: float = 0.0
    status: str = "open"

# === Market Data Provider ===
class MarketDataProvider:
    def __init__(self, symbol="EURUSD"):
        self.symbol = symbol
        self.current_price = 1.2000
        self.data = pd.DataFrame(columns=['timestamp','open','high','low','close','volume'])

    async def get_live_price(self) -> float:
        self.current_price += np.random.normal(0, 0.0005)
        new_row = {
            'timestamp': datetime.now(),
            'open': self.current_price,
            'high': self.current_price,
            'low': self.current_price,
            'close': self.current_price,
            'volume': np.random.randint(500,1500)
        }
        self.data = pd.concat([self.data, pd.DataFrame([new_row])], ignore_index=True)
        return round(self.current_price,5)

    def get_historical_data(self, periods=200):
        if len(self.data)>=periods:
            return self.data.tail(periods)
        # generate dummy historical data
        dates = pd.date_range(end=datetime.now(), periods=periods, freq='5min')
        price = self.current_price
        data=[]
        for d in dates:
            price += np.random.normal(0,0.0008)
            data.append({'timestamp':d,'open':price,'high':price+abs(np.random.normal(0,0.0003)),
                         'low':price-abs(np.random.normal(0,0.0003)),
                         'close':price,'volume':np.random.randint(500,1500)})
        self.data = pd.DataFrame(data)
        return self.data

# === Technical Indicators ===
class TechnicalIndicators:
    @staticmethod
    def calculate_atr(data, period=14):
        high_low = data['high'] - data['low']
        high_close = abs(data['high'] - data['close'].shift())
        low_close = abs(data['low'] - data['close'].shift())
        tr = np.maximum(high_low, np.maximum(high_close, low_close))
        return tr.rolling(period).mean().iloc[-1]

    @staticmethod
    def calculate_rsi(data, period=14):
        delta = data['close'].diff()
        gain = (delta.where(delta>0,0)).rolling(period).mean()
        loss = (-delta.where(delta<0,0)).rolling(period).mean()
        rs = gain/loss
        return 100 - (100/(1+rs)).iloc[-1]

    @staticmethod
    def detect_market_regime(data):
        if len(data)<50: return MarketRegime.TRENDING
        recent = data.tail(50)
        prices = recent['close'].values
        returns = np.diff(prices)/prices[:-1]
        volatility = np.std(returns)
        trend = (prices[-1]-prices[0])/prices[0]
        if abs(trend)>0.02 and volatility<0.015: return MarketRegime.TRENDING
        elif abs(trend)<0.01 and volatility<0.012: return MarketRegime.RANGING
        else: return MarketRegime.VOLATILE

# === Trading Strategies ===
class TradingStrategies:
    def __init__(self, data_provider):
        self.data_provider = data_provider
        self.indicators = TechnicalIndicators()

    def order_block_breakout(self, data, regime, weight):
        if np.random.random()>0.3: return None
        cp = data['close'].iloc[-1]
        atr = self.indicators.calculate_atr(data)
        stype = TradeType.BUY if np.random.random()>0.5 else TradeType.SELL
        sl,tp = (cp-atr*2, cp+atr*4) if stype==TradeType.BUY else (cp+atr*2, cp-atr*4)
        conf = 75+weight*50
        return Signal("orderBlockBreakout", stype, cp, sl, tp, conf, weight, regime, datetime.now())

    def liquidity_grab(self, data, regime, weight):
        if np.random.random()>0.2: return None
        cp = data['close'].iloc[-1]
        atr = self.indicators.calculate_atr(data)
        stype = TradeType.SELL if np.random.random()>0.5 else TradeType.BUY
        sl,tp = (cp-atr*1.5, cp+atr*3) if stype==TradeType.BUY else (cp+atr*1.5, cp-atr*3)
        conf = 80+weight*40
        return Signal("liquidityGrab", stype, cp, sl, tp, conf, weight, regime, datetime.now())

    def fibonacci_reversal(self, data, regime, weight):
        if np.random.random()>0.25: return None
        cp = data['close'].iloc[-1]
        atr = self.indicators.calculate_atr(data)
        rsi = self.indicators.calculate_rsi(data)
        stype = TradeType.BUY if rsi<50 else TradeType.SELL
        sl,tp = (cp-atr*1.8, cp+atr*3.6) if stype==TradeType.BUY else (cp+atr*1.8, cp-atr*3.6)
        conf = 70 + abs(50-rsi)
        return Signal("fibonacciReversal", stype, cp, sl, tp, conf, weight, regime, datetime.now())

    def structure_break(self, data, regime, weight):
        if np.random.random()>0.15: return None
        cp = data['close'].iloc[-1]
        atr = self.indicators.calculate_atr(data)
        stype = TradeType.BUY if np.random.random()>0.5 else TradeType.SELL
        sl,tp = (cp-atr*2.2, cp+atr*4.4) if stype==TradeType.BUY else (cp+atr*2.2, cp-atr*4.4)
        conf = 75+weight*50
        return Signal("structureBreak", stype, cp, sl, tp, conf, weight, regime, datetime.now())

# === Trading Engine ===
class DynamicTradingSystem:
    def __init__(self):
        self.data_provider = MarketDataProvider()
        self.strategies = TradingStrategies(self.data_provider)
        self.positions: List[Position] = []
        self.account_balance = 10000
        self.trade_counter = 0
        self.strategy_weights = {
            "orderBlockBreakout":0.25,
            "liquidityGrab":0.25,
            "fibonacciReversal":0.25,
            "structureBreak":0.25
        }

    async def generate_signals(self):
        data = self.data_provider.get_historical_data()
        regime = TechnicalIndicators.detect_market_regime(data)
        signals = []
        for strat_name, func in [
            ("orderBlockBreakout", self.strategies.order_block_breakout),
            ("liquidityGrab", self.strategies.liquidity_grab),
            ("fibonacciReversal", self.strategies.fibonacci_reversal),
            ("structureBreak", self.strategies.structure_break)
        ]:
            sig = func(data, regime, self.strategy_weights[strat_name])
            if sig: signals.append(sig)
        return signals

    async def execute_signals(self, signals: List[Signal]):
        for sig in signals:
            self.trade_counter +=1
            size = self.account_balance*0.01 # 1% per trade
            position = Position(
                id=f"POS{self.trade_counter}",
                strategy=sig.strategy,
                signal_type=sig.signal_type,
                entry=sig.entry,
                stop_loss=sig.stop_loss,
                take_profit=sig.take_profit,
                size=size,
                entry_time=datetime.now()
            )
            self.positions.append(position)
            logger.info(f"📊 SIGNAL GENERATED: {sig.strategy} {sig.signal_type.value.upper()} | Entry: {sig.entry} | SL: {sig.stop_loss} | TP: {sig.take_profit} | Confidence: {sig.confidence}%")

    async def update_positions(self):
        current_price = await self.data_provider.get_live_price()
        for pos in self.positions:
            if pos.status=="closed": continue
            if pos.signal_type==TradeType.BUY:
                if current_price>=pos.take_profit:
                    pos.unrealized_pnl = (pos.take_profit - pos.entry)*pos.size
                    pos.status="closed"
                    self.account_balance += pos.unrealized_pnl
                elif current_price<=pos.stop_loss:
                    pos.unrealized_pnl = (pos.stop_loss - pos.entry)*pos.size
                    pos.status="closed"
                    self.account_balance += pos.unrealized_pnl
            else:
                if current_price<=pos.take_profit:
                    pos.unrealized_pnl = (pos.entry - pos.take_profit)*pos.size
                    pos.status="closed"
                    self.account_balance += pos.unrealized_pnl
                elif current_price>=pos.stop_loss:
                    pos.unrealized_pnl = (pos.entry - pos.stop_loss)*pos.size
                    pos.status="closed"
                    self.account_balance += pos.unrealized_pnl

    async def run(self):
        while True:
            signals = await self.generate_signals()
            await self.execute_signals(signals)
            await self.update_positions()
            await asyncio.sleep(5)

# === Main ===
async def main():
    system = DynamicTradingSystem()
    await system.run()

if __name__=="__main__":
    asyncio.run(main())
