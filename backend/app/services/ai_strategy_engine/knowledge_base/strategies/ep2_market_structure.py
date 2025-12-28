import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# ==========================================
# 1. CONFIGURATION
# ==========================================
@dataclass
class Config:
    # Lookback for identifying a raw swing (fractal)
    # Arjo uses visual swings, typically 3-5 candles.
    fractal_lookback: int = 2
    # To simulate the "Daily" targets vs "4H" structure mentioned in the video:
    # We will look for Major Swings (Daily Proxies) using a larger lookback
    daily_proxy_lookback: int = 50
    # If True, prints detailed logic steps
    verbose: bool = True

config = Config()

# ==========================================
# 2. DATA STRUCTURES
# ==========================================
@dataclass
class SwingPoint:
    type: str # 'HIGH' or 'LOW'
    price: float
    index: int
    timestamp: pd.Timestamp
    # Is this an Intermediate Term Swing? (Validated by neighbors)
    is_intermediate: bool = False

@dataclass
class FairValueArea:
    """
    Arjo Ep 2 Definition:
    A range defined by an ITH and an ITL (3-swing movement).
    """
    type: str # 'BEARISH' (ITH to ITL) or 'BULLISH' (ITL to ITH)
    top_price: float # ITH price (bearish) or ITH price (bullish target)
    bottom_price: float # ITL price (bearish target) or ITL price (bullish)
    start_index: int # Creation time (usually the 2nd swing)
    break_index: Optional[int] = None # When structure was broken to confirm the FVA
    active: bool = False
    protection_level: float = 0.0 # The invalidation point (ITH for Bearish, ITL for Bullish)

# ==========================================
# 3. MARKET STRUCTURE ENGINE
# ==========================================
class MarketStructureEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.raw_swings: List[SwingPoint] = []
        self.ith_itl_points: List[SwingPoint] = []
        self.fva_list: List[FairValueArea] = []
        self.daily_targets: List[float] = []

    def _detect_raw_swings(self):
        """
        Standard Fractal Detection (Short term Highs/Lows).
        """
        lb = config.fractal_lookback
        for i in range(lb, len(self.df) - lb):
            # Swing High
            if self.df['high'].iloc[i] == self.df['high'].iloc[i-lb:i+lb+1].max():
                self.raw_swings.append(SwingPoint(
                    type='HIGH', price=self.df['high'].iloc[i], 
                    index=i, timestamp=self.df.index[i]
                ))
            # Swing Low
            if self.df['low'].iloc[i] == self.df['low'].iloc[i-lb:i+lb+1].min():
                self.raw_swings.append(SwingPoint(
                    type='LOW', price=self.df['low'].iloc[i], 
                    index=i, timestamp=self.df.index[i]
                ))
        
        # Sort strictly by time
        self.raw_swings.sort(key=lambda x: x.index)

    def _classify_intermediate_structure(self):
        """
        Classifies Swings into ITH (Intermediate Term High) and ITL.
        Rule: ITH = Swing High with a LOWER Swing High to the Left AND Right.
        Rule: ITL = Swing Low with a HIGHER Swing Low to the Left AND Right.
        """
        # Separate lists for easier comparison
        highs = [s for s in self.raw_swings if s.type == 'HIGH']
        lows = [s for s in self.raw_swings if s.type == 'LOW']

        # Process Highs
        for k in range(1, len(highs) - 1):
            prev_h = highs[k-1]
            curr_h = highs[k]
            next_h = highs[k+1]
            
            # Arjo's Definition of ITH
            if curr_h.price > prev_h.price and curr_h.price > next_h.price:
                curr_h.is_intermediate = True
                self.ith_itl_points.append(curr_h)

        # Process Lows
        for k in range(1, len(lows) - 1):
            prev_l = lows[k-1]
            curr_l = lows[k]
            next_l = lows[k+1]
            
            # Arjo's Definition of ITL
            if curr_l.price < prev_l.price and curr_l.price < next_l.price:
                curr_l.is_intermediate = True
                self.ith_itl_points.append(curr_l)
        
        # Re-merge and sort
        self.ith_itl_points.sort(key=lambda x: x.index)

    def _generate_fair_value_areas(self):
        """
        Identify FVAs based on the 3-Swing Movement.
        Bearish FVA: ITH -> ITL -> Break of ITL.
        Bullish FVA: ITL -> ITH -> Break of ITH.
        """
        # Iterate through classified structures
        for i in range(len(self.ith_itl_points) - 1):
            p1 = self.ith_itl_points[i]   # Start of range (Protection)
            p2 = self.ith_itl_points[i+1] # End of range (Target to break)
            
            # BEARISH SETUP (High then Low)
            if p1.type == 'HIGH' and p2.type == 'LOW':
                # Check for Break of Structure (BOS) below p2 (ITL)
                # Scan price action AFTER p2
                for k in range(p2.index + 1, len(self.df)):
                    # If we break the ITL, FVA is confirmed
                    if self.df['close'].iloc[k] < p2.price:
                        # Logic: Are we still respecting the ITH (p1)?
                        if self.df['high'].iloc[p2.index:k+1].max() < p1.price:
                            fva = FairValueArea(
                                type='BEARISH',
                                top_price=p1.price, # ITH (Protected)
                                bottom_price=p2.price, # ITL (Broken)
                                start_index=p2.index,
                                break_index=k,
                                active=True,
                                protection_level=p1.price
                            )
                            self.fva_list.append(fva)
                        break # FVA found for this sequence
                    
                    # Invalidation: If price breaks ITH before breaking ITL, pattern invalid
                    if self.df['high'].iloc[k] > p1.price:
                        break

            # BULLISH SETUP (Low then High)
            elif p1.type == 'LOW' and p2.type == 'HIGH':
                # Check for Break of Structure (BOS) above p2 (ITH)
                for k in range(p2.index + 1, len(self.df)):
                    if self.df['close'].iloc[k] > p2.price:
                        # Logic: Are we still respecting the ITL (p1)?
                         if self.df['low'].iloc[p2.index:k+1].min() > p1.price:
                            fva = FairValueArea(
                                type='BULLISH',
                                top_price=p2.price, # ITH (Broken)
                                bottom_price=p1.price, # ITL (Protected)
                                start_index=p2.index,
                                break_index=k,
                                active=True,
                                protection_level=p1.price
                            )
                            self.fva_list.append(fva)
                         break
                    
                    if self.df['low'].iloc[k] < p1.price:
                        break

    def _scan_daily_targets(self):
        """
        Simulates identifying 'Daily' targets by looking for major pivots
        across the entire dataset (larger lookback).
        """
        lb = config.daily_proxy_lookback
        targets = []
        for i in range(lb, len(self.df) - lb):
            if self.df['low'].iloc[i] == self.df['low'].iloc[i-lb:i+lb+1].min():
                targets.append({'price': self.df['low'].iloc[i], 'type': 'DAILY_LOW'})
            if self.df['high'].iloc[i] == self.df['high'].iloc[i-lb:i+lb+1].max():
                targets.append({'price': self.df['high'].iloc[i], 'type': 'DAILY_HIGH'})
        self.daily_targets = targets

    def run_analysis(self):
        self._detect_raw_swings()
        self._classify_intermediate_structure()
        self._generate_fair_value_areas()
        self._scan_daily_targets()
        return self.fva_list

# ==========================================
# 4. BACKTESTING / ANALYSIS LOGIC
# ==========================================
class DirectionalBacktester:
    """
    Tests Arjo's specific claim:
    "Intermediate Term Highs will be protected in a Bearish Trend."
    "Intermediate Term Lows will be protected in a Bullish Trend."
    """
    def __init__(self, df: pd.DataFrame, fva_list: List[FairValueArea]):
        self.df = df
        self.fva_list = fva_list
        self.log = []

    def test_protection(self):
        for fva in self.fva_list:
            # We start monitoring AFTER the BOS occurred
            start_monitor = fva.break_index + 1
            
            # Logic: Did price retrace into FVA?
            retraced = False
            failed = False
            succeeded = False
            
            # We need a target. In Arjo's logic, we target the Next Structural Low (Bearish).
            # For simulation, let's use a simple 1:1 expansion or next liquidity pool logic.
            # Here we just check if it continued the trend.
            extension_target = fva.bottom_price - (fva.top_price - fva.bottom_price) if fva.type == 'BEARISH' else fva.top_price + (fva.top_price - fva.bottom_price)
            
            for i in range(start_monitor, len(self.df)):
                curr_high = self.df['high'].iloc[i]
                curr_low = self.df['low'].iloc[i]
                
                # CHECK RETRACEMENT
                if fva.type == 'BEARISH':
                    # Entered FVA?
                    if curr_high > fva.bottom_price:
                        retraced = True
                    
                    # Invalidated? (Broke Protection ITH)
                    if curr_high > fva.protection_level:
                        failed = True
                        self.log.append({
                            'index': i, 'type': 'BEARISH_FAIL', 
                            'reason': 'ITH Broken', 'fva_idx': fva.start_index
                        })
                        break
                    
                    # Continuation? (New Low made after retrace)
                    if retraced and curr_low < extension_target:
                        succeeded = True
                        self.log.append({
                            'index': i, 'type': 'BEARISH_SUCCESS', 
                            'reason': 'Trend Continued after Retrace', 'fva_idx': fva.start_index
                        })
                        break

                elif fva.type == 'BULLISH':
                    # Entered FVA?
                    if curr_low < fva.top_price:
                        retraced = True
                    
                    # Invalidated? (Broke Protection ITL)
                    if curr_low < fva.protection_level:
                        failed = True
                        self.log.append({
                            'index': i, 'type': 'BULLISH_FAIL', 
                            'reason': 'ITL Broken', 'fva_idx': fva.start_index
                        })
                        break
                    
                    # Continuation?
                    if retraced and curr_high > extension_target:
                         succeeded = True
                         self.log.append({
                            'index': i, 'type': 'BULLISH_SUCCESS', 
                            'reason': 'Trend Continued after Retrace', 'fva_idx': fva.start_index
                        })
                         break
                         
        return pd.DataFrame(self.log)

# ==========================================
# 5. EXECUTION & DUMMY DATA
# ==========================================
def run_arjo_ep2_logic():
    print("--- Arjo Ep 2: Market Structure & Fair Value Areas ---")
    
    # 1. Generate Dummy Data (Trending Market Simulation)
    np.random.seed(42)
    periods = 500
    dates = pd.date_range(start='2024-01-01', periods=periods, freq='4h')
    
    # Create a synthetic bearish trend structure
    # Random walk with negative drift
    trend = np.linspace(100, 80, periods)
    noise = np.random.randn(periods) * 2
    
    # Inject explicit swings for the algorithm to find
    # (Manually crafting ITH/ITL structures is hard in random data, 
    # but noise+trend usually generates them naturally)
    close = trend + noise
    open_ = close + np.random.randn(periods) * 0.5
    high = np.maximum(open_, close) + abs(np.random.randn(periods) * 0.5)
    low = np.minimum(open_, close) - abs(np.random.randn(periods) * 0.5)
    
    df = pd.DataFrame({'timestamp': dates, 'open': open_, 'high': high, 'low': low, 'close': close})
    df.set_index('timestamp', inplace=True)
    
    # 2. Run Structure Engine
    engine = MarketStructureEngine(df)
    fvas = engine.run_analysis()
    
    print(f"Total Raw Swings Found: {len(engine.raw_swings)}")
    print(f"Intermediate Term Points (ITH/ITL) Classified: {len(engine.ith_itl_points)}")
    print(f"Fair Value Areas (3-Swing Sequences) Identified: {len(fvas)}")
    
    if len(fvas) > 0:
        print("\nExample Active FVA:")
        ex = fvas[-1]
        print(f"Type: {ex.type}")
        print(f"Range: {ex.bottom_price:.4f} to {ex.top_price:.4f}")
        print(f"Protection Level (Stop): {ex.protection_level:.4f}")
    
    # 3. Backtest Protection Logic
    tester = DirectionalBacktester(df, fvas)
    results = tester.test_protection()
    
    if not results.empty:
        print("\nBacktest Results (Protecting ITH/ITL):")
        success = len(results[results['type'].str.contains('SUCCESS')])
        fail = len(results[results['type'].str.contains('FAIL')])
        print(f"Successful Continuations: {success}")
        print(f"Failed Protections: {fail}")
        if success + fail > 0:
            print(f"Structural Integrity Rate: {(success/(success+fail))*100:.2f}%")
    else:
        print("No completed FVA sequences found in this data sample.")

# ==========================================
# FIREBASE HOOK
# ==========================================
def firebase_log_structure(structure_event):
    # db.collection('arjo_structure').add(structure_event)
    pass

if __name__ == "__main__":
    run_arjo_ep2_logic()
