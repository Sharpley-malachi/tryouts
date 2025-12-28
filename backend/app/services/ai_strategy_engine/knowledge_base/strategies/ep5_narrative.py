import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple

# ==========================================
# 1. CONFIGURATION
# ==========================================
@dataclass
class Config:
    swing_lookback: int = 2
    min_fvg_size: float = 0.0001
    
    # Scoring weights for probability
    score_fvg_present: int = 10
    score_no_fvg_llod: int = 10
    score_fvg_failed_llod: int = -10

config = Config()

# ==========================================
# 2. DATA STRUCTURES
# ==========================================
@dataclass
class OrderFlowLeg:
    bias: str # 'BULLISH' or 'BEARISH'
    start_index: int # The Swing Point Index
    end_index: int # The end of the impulsive move (before retrace)
    swing_price: float # The Swing Point Price (LLOD)
    leg_high: float
    leg_low: float
    fvg: Optional[Dict[str, float]] = None # {'top': x, 'bottom': y, 'index': z} or None

@dataclass
class DefenseLines:
    flod: Dict[str, float] # First Line of Defense Zone
    od: Optional[Dict[str, float]] # Overlapping Defense Zone
    llod: float # Last Line of Defense Level
    
    # Descriptions for the narrative
    flod_type: str # 'FVG' (Strong) or 'FVA' (Weak)
    od_type: str # 'Overlap' or 'None'
    llod_prob: str # 'High' (Liquidity Seek) or 'Low' (Structure Break likely)

# ==========================================
# 3. LEG DETECTION ENGINE (Recap of Ep 3 + Refinement)
# ==========================================
class LegDetector:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def find_fvg(self, start: int, end: int, direction: str) -> Optional[Dict[str, float]]:
        for i in range(start, end - 1):
            if direction == 'BEARISH':
                # Gap between Low(i) and High(i+2)
                low_1 = self.df['low'].iloc[i]
                high_3 = self.df['high'].iloc[i+2] if i+2 < len(self.df) else 0
                
                if low_1 > high_3 and (low_1 - high_3) > config.min_fvg_size:
                    return {'top': low_1, 'bottom': high_3, 'index': i+1}
            
            elif direction == 'BULLISH':
                # Gap between High(i) and Low(i+2)
                high_1 = self.df['high'].iloc[i]
                low_3 = self.df['low'].iloc[i+2] if i+2 < len(self.df) else 999999
                
                if low_3 > high_1 and (low_3 - high_1) > config.min_fvg_size:
                     return {'top': low_3, 'bottom': high_1, 'index': i+1}
        return None

    def get_recent_leg(self, current_index: int) -> Optional[OrderFlowLeg]:
        """
        Scans backwards from current_index to find the most recent completed swing point
        that initiated a move.
        """
        # Simplified fractal search for the sake of the example
        # In production, this would use the full Swing Point array from Ep 2
        for i in range(current_index - 2, config.swing_lookback, -1):
            
            # Check Bearish Swing (High)
            window = self.df.iloc[i-config.swing_lookback : i+config.swing_lookback+1]
            if self.df['high'].iloc[i] == window['high'].max():
                # We found a swing high. Now define the leg.
                # The leg exists from this high down to the lowest point before current retracement
                lowest_point_idx = i
                lowest_price = self.df['low'].iloc[i]
                
                # Find the 'impulse' end (lowest low before price started coming back up)
                for j in range(i+1, current_index):
                    if self.df['low'].iloc[j] < lowest_price:
                        lowest_price = self.df['low'].iloc[j]
                        lowest_point_idx = j
                
                # Look for FVG in this leg
                fvg = self.find_fvg(i, lowest_point_idx, 'BEARISH')
                
                return OrderFlowLeg(
                    bias='BEARISH',
                    start_index=i,
                    end_index=lowest_point_idx,
                    swing_price=self.df['high'].iloc[i],
                    leg_high=self.df['high'].iloc[i],
                    leg_low=lowest_price,
                    fvg=fvg
                )
        return None

# ==========================================
# 4. NARRATIVE & DEFENSE ENGINE (The Core of Ep 5)
# ==========================================
class NarrativeEngine:
    def __init__(self):
        pass

    def analyze_leg(self, leg: OrderFlowLeg) -> DefenseLines:
        """
        Applies Arjo's FLOD/OD/LLOD Logic to classify the leg.
        """
        # 1. LLOD (Last Line of Defense) - Always the Swing Point
        llod_price = leg.swing_price
        
        # 2. FLOD & OD Logic
        flod_zone = {}
        od_zone = None
        flod_desc = ""
        od_desc = ""
        llod_desc = ""
        
        # SCENARIO A: Leg has an FVG (High Probability Order Flow)
        if leg.fvg:
            # FLOD is the FVG (Best Case)
            flod_zone = leg.fvg
            flod_desc = "FVG (Strong Intention)"
            
            # OD is the overlap (which effectively is the FVG inside the leg)
            od_zone = leg.fvg
            od_desc = "Overlap (FVG + FVA)"
            
            # LLOD Probability is LOW (Price should hold at FLOD/OD)
            llod_desc = "Low Probability (Should hold at FVG)"
            
        # SCENARIO B: Leg has NO FVG (Liquidity Seeking)
        else:
            # FLOD is the Fair Value Area (Whole Leg Range) - Weak
            flod_zone = {'top': leg.leg_high, 'bottom': leg.leg_low}
            flod_desc = "FVA Only (Weak - No Intention)"
            
            # OD is None (No overlap of arrays)
            od_zone = None
            od_desc = "None"
            
            # LLOD Probability is HIGH (Seeking Liquidity at the High/Low)
            llod_desc = "High Probability (Seeking Liquidity/Sweep)"
            
        return DefenseLines(
            flod=flod_zone,
            od=od_zone,
            llod=llod_price,
            flod_type=flod_desc,
            od_type=od_desc,
            llod_prob=llod_desc
        )

    def print_narrative(self, leg: OrderFlowLeg, defenses: DefenseLines):
        print(f"\n--- NARRATIVE ANALYSIS ({leg.bias} LEG) ---")
        print(f"Leg Range: {leg.leg_high:.5f} to {leg.leg_low:.5f}")
        print(f"Intention Detected: {'YES (FVG)' if leg.fvg else 'NO (Seeking Liquidity)'}")
        
        print(f"\n[1] FLOD (First Line): {defenses.flod_type}")
        print(f"    Zone: {defenses.flod.get('top'):.5f} - {defenses.flod.get('bottom'):.5f}")
        
        if defenses.od:
            print(f"[2] OD (Overlap): {defenses.od_type}")
            print(f"    Zone: {defenses.od.get('top'):.5f} - {defenses.od.get('bottom'):.5f}")
        else:
             print(f"[2] OD (Overlap): None")
             
        print(f"[3] LLOD (Last Line): {defenses.llod_prob}")
        print(f"    Price: {defenses.llod:.5f}")
        
        print("\nSTRATEGY EXECUTION:")
        if leg.fvg:
            print(">> ACTION: Limit Entry at FLOD/OD (FVG). Stop Loss above LLOD.")
        else:
            print(">> ACTION: Wait for Sweep of LLOD (Swing Point). Look for reversal pattern after sweep.")

# ==========================================
# 5. EXECUTION WRAPPER
# ==========================================
def run_arjo_ep5():
    print("Generating Synthetic Price Data...")
    
    # Generate data that specifically creates an FVG pattern and a non-FVG pattern
    
    # Case 1: Strong Bearish Leg with FVG
    data_strong = {
        'high': [1.2000, 1.1950, 1.1900, 1.1800, 1.1820],
        'low':  [1.1900, 1.1880, 1.1800, 1.1700, 1.1750], # Gap between 1.1880 (low 1) and 1.1800 (high 3)
        'close':[1.1920, 1.1900, 1.1820, 1.1710, 1.1800],
        'open': [1.1950, 1.1940, 1.1880, 1.1820, 1.1710]
    }
    df_strong = pd.DataFrame(data_strong)
    
    # Case 2: Weak Bearish Leg (Drift) without FVG
    data_weak = {
        'high': [1.2000, 1.1980, 1.1960, 1.1940, 1.1950],
        'low':  [1.1950, 1.1940, 1.1920, 1.1900, 1.1910], # Wicks overlap, no gap
        'close':[1.1960, 1.1950, 1.1930, 1.1910, 1.1920],
        'open': [1.1990, 1.1970, 1.1950, 1.1930, 1.1910]
    }
    df_weak = pd.DataFrame(data_weak)

    detector = LegDetector(df_strong)
    engine = NarrativeEngine()
    
    # 1. Analyze Strong Leg
    print("\nAnalyzing Case 1: Price Drop WITH Displacement...")
    leg1 = detector.get_recent_leg(len(df_strong)-1)
    if leg1:
        defenses1 = engine.analyze_leg(leg1)
        engine.print_narrative(leg1, defenses1)

    # 2. Analyze Weak Leg
    print("\nAnalyzing Case 2: Price Drift WITHOUT Displacement...")
    detector.df = df_weak
    leg2 = detector.get_recent_leg(len(df_weak)-1)
    if leg2:
        defenses2 = engine.analyze_leg(leg2)
        engine.print_narrative(leg2, defenses2)

if __name__ == "__main__":
    run_arjo_ep5()
