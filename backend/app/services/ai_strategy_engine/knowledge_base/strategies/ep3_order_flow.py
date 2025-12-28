import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Dict

# ==========================================
# 1. CONFIGURATION
# ==========================================
@dataclass
class Config:
    # Lookback for identifying a Short Term Swing (STH/STL)
    # Arjo defines STH/STL as standard swings (e.g., 3-candle fractal)
    swing_lookback: int = 1
    # Distance to look ahead for FVG creation to validate the leg
    # "Immediately followed by an FVG"
    fvg_search_window: int = 3
    # Minimum size of FVG (in pips/points) to be considered significant
    min_fvg_size: float = 0.0001

config = Config()

# ==========================================
# 2. DATA STRUCTURES
# ==========================================
@dataclass
class OrderFlowLeg:
    """
    Represents a Valid Order Flow Leg.
    Must have: Swing Point + FVG.
    """
    bias: str # 'BULLISH' or 'BEARISH'
    swing_price: float # The Protection Level (STH/STL)
    swing_index: int
    fvg_top: float
    fvg_bottom: float
    fvg_index: int # Index where FVG was confirmed (candle 3 of the gap)
    target_hit: bool = False
    invalidated: bool = False
    
    @property
    def protection_level(self):
        return self.swing_price

# ==========================================
# 3. ORDER FLOW ENGINE
# ==========================================
class OrderFlowDetector:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.active_legs: List[OrderFlowLeg] = []
        self.completed_legs: List[OrderFlowLeg] = []

    def _is_swing_high(self, idx: int) -> bool:
        # Standard Fractal High
        if idx < config.swing_lookback or idx >= len(self.df) - config.swing_lookback:
            return False
        current_high = self.df['high'].iloc[idx]
        left_side = self.df['high'].iloc[idx - config.swing_lookback : idx].max()
        right_side = self.df['high'].iloc[idx + 1 : idx + config.swing_lookback + 1].max()
        return current_high > left_side and current_high > right_side

    def _is_swing_low(self, idx: int) -> bool:
        # Standard Fractal Low
        if idx < config.swing_lookback or idx >= len(self.df) - config.swing_lookback:
             return False
        current_low = self.df['low'].iloc[idx]
        left_side = self.df['low'].iloc[idx - config.swing_lookback : idx].min()
        right_side = self.df['low'].iloc[idx + 1 : idx + config.swing_lookback + 1].min()
        return current_low < left_side and current_low < right_side

    def _find_fvg(self, start_idx: int, direction: str) -> Optional[Dict]:
        """
        Scans forward from swing point to find the IMMEDIATE FVG.
        """
        limit = min(start_idx + config.fvg_search_window + 2, len(self.df))
        
        # Standard ICT FVG Logic: Gap between Candle i and i+2
        # We start checking from the candle forming the swing
        for i in range(start_idx, limit - 2):
            if direction == 'BEARISH':
                # Bearish FVG: Low(i) > High(i+2)
                candle_1_low = self.df['low'].iloc[i]
                candle_3_high = self.df['high'].iloc[i+2]
                
                if candle_1_low > candle_3_high:
                    gap_size = candle_1_low - candle_3_high
                    if gap_size >= config.min_fvg_size:
                        return {
                            'top': candle_1_low,
                            'bottom': candle_3_high,
                            'index': i+2
                        }
            
            elif direction == 'BULLISH':
                 # Bullish FVG: High(i) < Low(i+2)
                candle_1_high = self.df['high'].iloc[i]
                candle_3_low = self.df['low'].iloc[i+2]
                
                if candle_3_low > candle_1_high:
                    gap_size = candle_3_low - candle_1_high
                    if gap_size >= config.min_fvg_size:
                        return {
                            'top': candle_3_low,
                            'bottom': candle_1_high,
                            'index': i+2
                        }
        return None

    def scan(self):
        """
        Main Loop:
        1. Find Swings (STH/STL).
        2. Verify Intention (Check for FVG).
        3. Create Order Flow Leg.
        4. Track Leg Protection.
        """
        # Start scanning after initial lookback
        for i in range(config.swing_lookback, len(self.df) - config.fvg_search_window - 2):
            
            # --- BEARISH ORDER FLOW CHECK ---
            if self._is_swing_high(i):
                sth_price = self.df['high'].iloc[i]
                # Verify Intention: Look for Bearish FVG
                fvg = self._find_fvg(i, 'BEARISH')
                
                if fvg:
                    # Valid Order Flow Leg found
                    leg = OrderFlowLeg(
                        bias='BEARISH',
                        swing_price=sth_price,
                        swing_index=i,
                        fvg_top=fvg['top'],
                        fvg_bottom=fvg['bottom'],
                        fvg_index=fvg['index']
                    )
                    self.active_legs.append(leg)

            # --- BULLISH ORDER FLOW CHECK ---
            if self._is_swing_low(i):
                stl_price = self.df['low'].iloc[i]
                # Verify Intention: Look for Bullish FVG
                fvg = self._find_fvg(i, 'BULLISH')
                
                if fvg:
                    # Valid Order Flow Leg found
                    leg = OrderFlowLeg(
                        bias='BULLISH',
                        swing_price=stl_price,
                        swing_index=i,
                        fvg_top=fvg['top'],
                        fvg_bottom=fvg['bottom'],
                        fvg_index=fvg['index']
                    )
                    self.active_legs.append(leg)

            # --- TRACKING / VALIDATION ---
            # Check if active legs are invalidated (Protection Breached)
            current_high = self.df['high'].iloc[i]
            current_low = self.df['low'].iloc[i]
            
            for leg in self.active_legs:
                if leg.invalidated: continue
                
                # Only check validation after the leg is fully formed
                if i <= leg.fvg_index: continue
                
                if leg.bias == 'BEARISH':
                    # Invalidated if price closes above STH (Arjo mentions protection)
                    # Using High > Protection for stricter checking in code
                    if current_high > leg.protection_level:
                        leg.invalidated = True
                
                elif leg.bias == 'BULLISH':
                    # Invalidated if price closes below STL
                    if current_low < leg.protection_level:
                        leg.invalidated = True
                        
        return self.active_legs

# ==========================================
# 4. ANALYSIS & REPORTING
# ==========================================
def analyze_order_flow_chains(legs: List[OrderFlowLeg]):
    """
    Analyzes the sequence of legs to determine the dominant Order Flow Chain.
    """
    print("\n--- Order Flow Chain Analysis ---")
    bearish_chain = [l for l in legs if l.bias == 'BEARISH']
    bullish_chain = [l for l in legs if l.bias == 'BULLISH']
    
    valid_bear = [l for l in bearish_chain if not l.invalidated]
    valid_bull = [l for l in bullish_chain if not l.invalidated]
    
    print(f"Total Bearish Legs Detected: {len(bearish_chain)}")
    print(f"Holding Bearish Legs (Protected): {len(valid_bear)}")
    print(f"Total Bullish Legs Detected: {len(bullish_chain)}")
    print(f"Holding Bullish Legs (Protected): {len(valid_bull)}")
    
    if len(valid_bear) > len(valid_bull):
        print("\nDOMINANT INTENTION: BEARISH")
        print("Market is respecting Short Term Highs + FVGs.")
    elif len(valid_bull) > len(valid_bear):
        print("\nDOMINANT INTENTION: BULLISH")
        print("Market is respecting Short Term Lows + FVGs.")
    else:
        print("\nDOMINANT INTENTION: NEUTRAL / CONSOLIDATION")

# ==========================================
# 5. EXECUTION WRAPPER
# ==========================================
def run_script():
    print("--- Arjo Ep 3: Order Flow Logic ---")
    
    # Generate Dummy Data with Order Flow characteristics
    np.random.seed(101)
    periods = 300
    dates = pd.date_range(start='2024-01-01', periods=periods, freq='1h')
    
    # Simulate a bearish order flow: Price trending down with pullbacks
    price = 100.0
    opens, highs, lows, closes = [], [], [], []
    
    for i in range(periods):
        change = np.random.randn()
        # Add bearish bias
        if i > 50 and i < 250:
             change -= 0.1
        
        open_p = price
        close_p = price + change
        high_p = max(open_p, close_p) + abs(np.random.randn() * 0.2)
        low_p = min(open_p, close_p) - abs(np.random.randn() * 0.2)
        
        # Inject deliberate Order Flow signatures (Drop + Gap)
        if i % 20 == 0:
            # Big bearish displacement candle
            close_p -= 1.0
            low_p = close_p - 0.1
        
        opens.append(open_p)
        closes.append(close_p)
        highs.append(high_p)
        lows.append(low_p)
        
        price = close_p
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes
    })
    
    detector = OrderFlowDetector(df)
    legs = detector.scan()
    
    # Print discovered legs details
    if legs:
        print(f"Detected {len(legs)} Potential Order Flow Legs.")
        print("Last 5 Legs:")
        for leg in legs[-5:]:
            status = "INVALIDATED" if leg.invalidated else "ACTIVE"
            print(f"[{leg.bias}] Swing: {leg.swing_price:.4f} | FVG Index: {leg.fvg_index} | Status: {status}")
            
        analyze_order_flow_chains(legs)

if __name__ == "__main__":
    run_script()
