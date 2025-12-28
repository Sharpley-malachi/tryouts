import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Dict

# ==========================================
# 1. CONFIGURATION
# ==========================================
@dataclass
class Config:
    swing_lookback: int = 5
    # A sweep is valid if price goes beyond swing by at least X ticks but closes inside
    min_sweep_dist: float = 0.0001
    # Lookahead to confirm the reversal after a potential sweep
    confirmation_candles: int = 2

config = Config()

# ==========================================
# 2. DATA STRUCTURES
# ==========================================
@dataclass
class SwingPoint:
    type: str # 'HIGH' or 'LOW'
    price: float
    index: int
    tested: bool = False

@dataclass
class LiquidityEvent:
    swing: SwingPoint
    interaction_index: int
    interaction_type: str # 'SWEEP' or 'RUN'
    description: str
    # Outcome tracking
    reversal_success: bool = False
    continuation_success: bool = False

# ==========================================
# 3. LIQUIDITY ENGINE
# ==========================================
class LiquidityEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.swings: List[SwingPoint] = []
        self.events: List[LiquidityEvent] = []

    def detect_swings(self):
        """
        Standard Fractal Swing Detection.
        """
        lb = config.swing_lookback
        for i in range(lb, len(self.df) - lb):
            # Swing High
            if self.df['high'].iloc[i] == self.df['high'].iloc[i-lb:i+lb+1].max():
                self.swings.append(SwingPoint('HIGH', self.df['high'].iloc[i], i))
            # Swing Low
            if self.df['low'].iloc[i] == self.df['low'].iloc[i-lb:i+lb+1].min():
                self.swings.append(SwingPoint('LOW', self.df['low'].iloc[i], i))

    def analyze_interactions(self):
        """
        Checks if price interacts with old swings and classifies as Run or Sweep.
        """
        # Sort swings by time
        self.swings.sort(key=lambda x: x.index)
        
        for i in range(config.swing_lookback * 2, len(self.df)):
            current_candle = self.df.iloc[i]
            
            # Check against all UNTESTED swings that formed at least 'lookback' ago
            valid_swings = [s for s in self.swings if s.index < i - config.swing_lookback and not s.tested]
            
            for swing in valid_swings:
                # --- INTERACTION WITH SWING HIGH (Liquidity Pool) ---
                if swing.type == 'HIGH':
                    if current_candle['high'] > swing.price:
                        # Interaction confirmed
                        swing.tested = True
                        
                        # Classify: RUN or SWEEP?
                        if current_candle['close'] > swing.price:
                            # Close ABOVE High = RUN (Continuation/Strength)
                            self.events.append(LiquidityEvent(
                                swing, i, 'RUN',
                                "Bullish Run: Comfortable Close above High"
                            ))
                        else:
                            # Close BELOW High = SWEEP (Turtle Soup/Reversal)
                            self.events.append(LiquidityEvent(
                                swing, i, 'SWEEP',
                                "Bearish Sweep: Wick above High, Close Below (Turtle Soup)"
                            ))
                            
                # --- INTERACTION WITH SWING LOW (Liquidity Pool) ---
                elif swing.type == 'LOW':
                    if current_candle['low'] < swing.price:
                        swing.tested = True
                        
                        if current_candle['close'] < swing.price:
                            # Close BELOW Low = RUN (Continuation/Weakness)
                            self.events.append(LiquidityEvent(
                                swing, i, 'RUN',
                                "Bearish Run: Comfortable Close below Low"
                            ))
                        else:
                            # Close ABOVE Low = SWEEP (Turtle Soup/Reversal)
                            self.events.append(LiquidityEvent(
                                swing, i, 'SWEEP',
                                "Bullish Sweep: Wick below Low, Close Above (Turtle Soup)"
                            ))

    def print_results(self):
        print(f"Total Swings Detected: {len(self.swings)}")
        print(f"Total Liquidity Events: {len(self.events)}")
        
        sweeps = [e for e in self.events if e.interaction_type == 'SWEEP']
        runs = [e for e in self.events if e.interaction_type == 'RUN']
        
        print(f"\n--- STATS ---")
        print(f"Liquidity Sweeps (Turtle Soup): {len(sweeps)}")
        print(f"Liquidity Runs (Continuation): {len(runs)}")
        
        print("\n--- RECENT EVENTS ---")
        for e in self.events[-5:]:
            print(f"Index {e.interaction_index}: {e.description} (Swing Price: {e.swing.price:.5f})")

# ==========================================
# 4. EXECUTION WRAPPER
# ==========================================
def run_arjo_ep8():
    print("--- Arjo Ep 8: Liquidity Sweep vs Run ---")
    
    # Generate Synthetic Data
    # Pattern: 
    # 1. Create High.
    # 2. Sweep High (Wick only).
    # 3. Drop (Reversal).
    # 4. Create Low.
    # 5. Run Low (Close below).
    
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
    data = {'high': [], 'low': [], 'open': [], 'close': []}
    
    price = 100.0
    for i in range(100):
        # i=10: Form Swing High at 105
        if i == 10: 
            h, l, c, o = 105.0, 100.0, 102.0, 101.0
        # i=30: Sweep High (Go to 106, Close at 104) -> Turtle Soup
        elif i == 30:
            h, l, c, o = 106.0, 100.0, 104.0, 101.0 # High > 105, Close < 105
        # i=50: Form Swing Low at 95
        elif i == 50:
            h, l, c, o = 100.0, 95.0, 98.0, 99.0
        # i=70: Run Low (Go to 94, Close at 93) -> Continuation
        elif i == 70:
            h, l, c, o = 98.0, 94.0, 93.0, 97.0 # Low < 95, Close < 95
        else:
            base = 100.0 + np.random.randn()
            h, l, c, o = base+1, base-1, base, base+0.5
            
        data['high'].append(h)
        data['low'].append(l)
        data['close'].append(c)
        data['open'].append(o)
        
    df = pd.DataFrame(data, index=dates)
    
    engine = LiquidityEngine(df)
    engine.detect_swings()
    engine.analyze_interactions()
    engine.print_results()

if __name__ == "__main__":
    run_arjo_ep8()
