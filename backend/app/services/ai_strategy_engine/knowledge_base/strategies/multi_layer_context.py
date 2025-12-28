import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
from enum import Enum

# --- Constants & Enums ---
class MarketState(Enum):
    OFFERING_FAIR_VALUE = 1
    SEEKING_LIQUIDITY = 2

class Trend(Enum):
    BULLISH = 1
    BEARISH = -1

class DefenseType(Enum):
    FLOD = "First Line of Defense"
    OD = "Overlapping Defense"
    LLOD = "Last Line of Defense"

@dataclass
class Candle:
    time: str
    open: float
    high: float
    low: float
    close: float
    index: int

@dataclass
class PDArray:
    type: str  # 'FVG', 'SWING_HIGH', 'SWING_LOW', 'CANDLE_HIGH', 'CANDLE_LOW'
    top: float
    bottom: float
    trend: Trend
    index: int
    mitigated: bool = False
    invalidated: bool = False

@dataclass
class ContextSetup:
    context_type: str # 'Usual' or 'Unusual'
    boundary: PDArray # The FVG/FVA allowing entry
    target: PDArray   # The Opposing PD Array
    active: bool = True
    success: bool = False
    fail: bool = False

class ArjoMoneyMakingContext_10:
    """
    Implements Arjo's Usual and Unusual Context Logic.
    Layer 4 Strategy Logic Orchestrator.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.pd_arrays: List[PDArray] = []
        self.context_log: List[ContextSetup] = []
        self.current_market_state = MarketState.OFFERING_FAIR_VALUE
        
    def detect_pd_arrays(self):
        """
        Scans for FVGs and Swings to populate the map.
        Similar to Ep 1 & 6 logic.
        """
        # Swings
        for i in range(2, len(self.df)-2):
            # Swing High
            if self.df['high'].iloc[i] > self.df['high'].iloc[i-1] and \
               self.df['high'].iloc[i] > self.df['high'].iloc[i+1]:
                self.pd_arrays.append(PDArray(
                    type='SWING_HIGH', top=self.df['high'].iloc[i], bottom=self.df['high'].iloc[i],
                    trend=Trend.BEARISH, index=i
                ))
            # Swing Low
            if self.df['low'].iloc[i] < self.df['low'].iloc[i-1] and \
               self.df['low'].iloc[i] < self.df['low'].iloc[i+1]:
                 self.pd_arrays.append(PDArray(
                    type='SWING_LOW', top=self.df['low'].iloc[i], bottom=self.df['low'].iloc[i],
                    trend=Trend.BULLISH, index=i
                ))
                
        # FVGs
        for i in range(len(self.df)-2):
            # Bullish FVG
            if self.df['low'].iloc[i+2] > self.df['high'].iloc[i]:
                 self.pd_arrays.append(PDArray(
                    type='FVG', top=self.df['low'].iloc[i+2], bottom=self.df['high'].iloc[i],
                    trend=Trend.BULLISH, index=i+1
                ))
            # Bearish FVG
            elif self.df['high'].iloc[i+2] < self.df['low'].iloc[i]:
                 self.pd_arrays.append(PDArray(
                    type='FVG', top=self.df['low'].iloc[i], bottom=self.df['high'].iloc[i+2],
                    trend=Trend.BEARISH, index=i+1
                ))

    def get_unmitigated_boundary(self, current_idx, direction: Trend) -> Optional[PDArray]:
        """Looks for the nearest unmitigated FVG/FVA in the trade direction."""
        candidates = [
            a for a in self.pd_arrays 
            if a.index < current_idx and not a.mitigated and not a.invalidated
            and a.trend == direction
        ]
        # Return most recent
        if candidates:
            return candidates[-1]
        return None

    def get_opposing_target(self, current_idx, boundary: PDArray) -> Optional[PDArray]:
        """Looks for the nearest opposing array (Target)."""
        opposing_direction = Trend.BEARISH if boundary.trend == Trend.BULLISH else Trend.BULLISH
        
        candidates = [
            a for a in self.pd_arrays
            if a.index < current_idx and a.trend == opposing_direction
        ]
        
        # Filter logic: Target must be "ahead" of price.
        # For Bullish: Target > Boundary. For Bearish: Target < Boundary.
        if boundary.trend == Trend.BULLISH:
            valid_targets = [t for t in candidates if t.bottom > boundary.top]
            if valid_targets: return min(valid_targets, key=lambda x: x.bottom)
        else:
            valid_targets = [t for t in candidates if t.top < boundary.bottom]
            if valid_targets: return max(valid_targets, key=lambda x: x.top)
            
        return None

    def run_epoch(self):
        print("--- Running Multi-Layer Context Logic ---")
        self.detect_pd_arrays()
        
        # Simulation Loop
        for i in range(10, len(self.df)):
            curr = self.df.iloc[i]
            
            # 1. CHECK FOR USUAL CONTEXT FORMATION
            # Are we in a boundary?
            # Check Bullish Boundary (Support)
            bull_boundary = self.get_unmitigated_boundary(i, Trend.BULLISH)
            
            if bull_boundary:
                # Interaction Check: Low <= Top and High >= Bottom
                if curr['low'] <= bull_boundary.top and curr['high'] >= bull_boundary.bottom:
                    
                    # We are INSIDE a boundary. Look for Target.
                    target = self.get_opposing_target(i, bull_boundary)
                    
                    if target:
                        # CREATE CONTEXT
                        setup = ContextSetup(
                            context_type="Use_Of_Context",
                            boundary=bull_boundary,
                            target=target
                        )
                        self.context_log.append(setup)
                        
                        # Mark mitigated
                        bull_boundary.mitigated = True 
                        print(f"[{i}] USUAL CONTEXT FOUND: Bullish FVG Mitigated. Target: {target.type} at {target.bottom}")

            # 2. CHECK FOR UNUSUAL CONTEXT (FAILED BOUNDARY)
            # Did a boundary fail recently?
            # (Simplified check for demo)
            # If price closes below a Bullish Boundary -> Market is SEEKING LIQUIDITY
            # Target becomes the swing low of that failed boundary structure
            pass 

    def print_report(self):
        print(f"Total Contexts Identified: {len(self.context_log)}")

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    # Generate random data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='4h')
    df = pd.DataFrame({
         'open': np.random.randn(100).cumsum() + 100,
         'high': np.random.randn(100).cumsum() + 102,
         'low': np.random.randn(100).cumsum() + 98,
         'close': np.random.randn(100).cumsum() + 100
    }, index=dates)
    
    # fix high/low
    df['high'] = df[['open','close','high']].max(axis=1)
    df['low'] = df[['open','close','low']].min(axis=1)

    algo = ArjoMoneyMakingContext_10(df)
    algo.run_epoch()
    algo.print_report()
