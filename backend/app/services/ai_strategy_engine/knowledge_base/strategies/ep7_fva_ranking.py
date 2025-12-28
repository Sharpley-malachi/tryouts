import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple

# ==========================================
# 1. CONFIGURATION
# ==========================================
@dataclass
class Config:
    # Lookback for Swing Points
    swing_lookback: int = 5
    # FVG Minimum size
    min_fvg_size: float = 0.0001
    # Simulation of Lower Timeframe (LTF) by checking previous candles?
    # Real LTF data would require multi-timeframe inputs.
    # We will simulate "Nested" checks by looking for micro-structures in the same timeframe for this standalone code.
    check_nested_sim: bool = True

config = Config()

# ==========================================
# 2. DATA STRUCTURES
# ==========================================
@dataclass
class FairValueGap:
    bias: str # 'BULLISH' or 'BEARISH'
    top: float
    bottom: float
    index: int

@dataclass
class FairValueArea:
    bias: str # 'BULLISH' (ITL to ITH) or 'BEARISH' (ITH to ITL)
    top: float # High of the range
    bottom: float # Low of the range
    start_index: int
    end_index: int
    
    # Ranking Attributes
    has_overlapping_fvg: bool = False
    has_nested_fva: bool = False
    is_sweep_only: bool = False # Tier 3 indicator

    @property
    def tier(self):
        if self.has_overlapping_fvg and self.has_nested_fva:
            return 1 # Best
        if self.has_overlapping_fvg:
            return 2 # Good
        return 3 # Worst (Sweep/Wick)

# ==========================================
# 3. STRUCTURE & FVA ENGINE
# ==========================================
class FVA_Engine:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.fvgs: List[FairValueGap] = []
        self.fvas: List[FairValueArea] = []

    def detect_fvgs(self):
        """
        Standard FVG detection (Gap between candle i and i+2).
        """
        for i in range(len(self.df) - 2):
            # Bullish FVG
            if self.df['low'].iloc[i+2] > self.df['high'].iloc[i]:
                self.fvgs.append(FairValueGap(
                    bias='BULLISH',
                    top=self.df['low'].iloc[i+2],
                    bottom=self.df['high'].iloc[i],
                    index=i+1
                ))
            # Bearish FVG
            elif self.df['high'].iloc[i+2] < self.df['low'].iloc[i]:
                self.fvgs.append(FairValueGap(
                    bias='BEARISH',
                    top=self.df['low'].iloc[i],
                    bottom=self.df['high'].iloc[i+2],
                    index=i+1
                ))

    def detect_fvas_and_rank(self):
        """
        Identifies FVAs based on 3-swing moves and ranks them.
        """
        # 1. Identify Swings (Simplified Fractal)
        lb = config.swing_lookback
        highs = []
        lows = []
        for i in range(lb, len(self.df) - lb):
            if self.df['high'].iloc[i] == self.df['high'].iloc[i-lb:i+lb+1].max():
                highs.append((i, self.df['high'].iloc[i]))
            if self.df['low'].iloc[i] == self.df['low'].iloc[i-lb:i+lb+1].min():
                lows.append((i, self.df['low'].iloc[i]))
        
        # 2. Construct Bullish FVAs (Low -> High -> Break High)
        # This matches the logic: ITL -> ITH -> Expansion
        for i in range(len(lows) - 1):
            l_idx, l_price = lows[i]
            # Find next high
            next_highs = [h for h in highs if h[0] > l_idx]
            if not next_highs: continue
            h_idx, h_price = next_highs[0]
            
            # Define the FVA Range (ITL to ITH)
            fva = FairValueArea(
                bias='BULLISH',
                top=h_price,
                bottom=l_price,
                start_index=l_idx,
                end_index=h_idx
            )
            
            # 3. RANKING LOGIC
            # Check Overlapping FVG
            # Look for a Bullish FVG that formed physically inside this price range
            # And chronologically during/after the leg formation (but before retrace)
            overlaps = []
            for fvg in self.fvgs:
                if fvg.bias == 'BULLISH' and fvg.index >= l_idx:
                    # Check geometric overlap
                    # Ideally FVG is completely inside FVA or intersects significantly
                    if (fvg.bottom >= fva.bottom and fvg.top <= fva.top):
                        overlaps.append(fvg)
            
            if len(overlaps) > 0:
                fva.has_overlapping_fvg = True
            
            # Check Nested FVA (Simulation)
            # In a real engine, we would pass a 1H dataframe to check inside a 4H FVA.
            # Here we simulate by checking if there was a 'micro' structure break inside the leg.
            # Simple proxy: Was the leg formed by multiple candles with their own small pullbacks?
            if (h_idx - l_idx) > 5: # Arbitrary complexity proxy
                fva.has_nested_fva = True

            # Check Tier 3 (Sweep Only)
            # If we broke a previous high but NO overlapping FVG was created
            # And price wicked back down immediately?
            # Logic: Look at candles immediately after h_idx
            scan_limit = min(h_idx + 3, len(self.df))
            displacement = False
            for k in range(h_idx, scan_limit):
                if self.df['close'].iloc[k] > h_price:
                    displacement = True
            
            if not fva.has_overlapping_fvg and not displacement:
                fva.is_sweep_only = True
            
            self.fvas.append(fva)

    def run_analysis(self):
        self.detect_fvgs()
        self.detect_fvas_and_rank()
        return self.fvas

# ==========================================
# 4. EXECUTION WRAPPER
# ==========================================
def run_arjo_ep7():
    print("--- Arjo Ep 7: Fair Value Areas Ranking ---")
    
    # Generate Synthetic Data
    # Scenario:
    # 1. Price consolidates (Tier 3 behavior)
    # 2. Price explodes with FVG (Tier 2)
    # 3. Price explodes with FVG and microstructure (Tier 1)
    
    dates = pd.date_range(start='2024-01-01', periods=100, freq='4h')
    data = {
        'open': [100]*100, 'high': [100]*100, 'low': [100]*100, 'close': [100]*100
    }
    
    # Manually construct the path
    price = 100.0
    for i in range(100):
        # Tier 3 Sweep setup (i=10 to 20)
        if 10 <= i <= 20:
             price += np.random.randn() * 0.5
             if i == 15: price = 102.0 # High sweep
             # No FVG created here in simulation logic
        
        # Tier 2/1 Setup (i=40 to 60)
        elif 40 <= i <= 60:
            price += 1.0 # Strong trend
            # This creates gaps naturally (Low[i] > High[i-2])
        
        else:
             price += np.random.randn() * 0.5
        
        data['open'][i] = price
        data['close'][i] = price + 0.2
        data['high'][i] = price + 0.5
        data['low'][i] = price - 0.5

    df = pd.DataFrame(data, index=dates)
    
    engine = FVA_Engine(df)
    ranked_fvas = engine.run_analysis()
    
    print(f"Identified {len(ranked_fvas)} Fair Value Areas.")
    
    t1 = [f for f in ranked_fvas if f.tier == 1]
    t2 = [f for f in ranked_fvas if f.tier == 2]
    t3 = [f for f in ranked_fvas if f.tier == 3]
    
    print(f"\n[RANKING RESULTS]")
    print(f"Tier 1 (Best - Overlap + Nested): {len(t1)}")
    print(f"Tier 2 (Good - Overlap): {len(t2)}")
    print(f"Tier 3 (Worst - Sweep/No FVG): {len(t3)}")
    
    if len(t1) > 0:
        print(f"\nExample Tier 1 FVA Range: {t1[0].bottom:.2f} - {t1[0].top:.2f}")
        print("Strategy: Set Limit at FVA Top (Bullish) or Bottom (Bearish).")

if __name__ == "__main__":
    run_arjo_ep7()
