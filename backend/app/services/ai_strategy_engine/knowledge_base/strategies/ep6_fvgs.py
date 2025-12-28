import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# ==========================================
# 1. CONFIGURATION
# ==========================================
@dataclass
class Config:
    swing_lookback: int = 5
    min_fvg_size: float = 0.0001
    # How many candles after hitting resistance do we allow a new FVG to form
    # to still consider it "Created at Resistance"?
    reaction_window: int = 3

config = Config()

# ==========================================
# 2. DATA STRUCTURES
# ==========================================
@dataclass
class PDArray:
    id: str
    type: str # 'SWING_HIGH', 'SWING_LOW', 'FVG_BEAR', 'FVG_BULL'
    top: float
    bottom: float
    creation_index: int
    mitigated: bool = False
    mitigation_index: Optional[int] = None

@dataclass
class TradeSetup:
    direction: str # 'LONG' or 'SHORT'
    entry_fvg: PDArray
    opposing_array_hit: PDArray
    timestamp: pd.Timestamp

# ==========================================
# 3. PD ARRAY MANAGER
# ==========================================
class PDArrayManager:
    def __init__(self):
        self.arrays: List[PDArray] = []
        self.counter = 0

    def add_array(self, type_: str, top: float, bottom: float, idx: int):
        self.counter += 1
        self.arrays.append(PDArray(
            id=f"{type_}_{self.counter}",
            type=type_,
            top=top,
            bottom=bottom,
            creation_index=idx
        ))

    def check_mitigations(self, current_candle, current_idx):
        """
        Updates mitigation status of existing arrays based on current price action.
        """
        high = current_candle['high']
        low = current_candle['low']
        
        for array in self.arrays:
            if array.mitigated: continue
            
            # Logic: If price touches the array zone
            # Bearish Arrays (Resistance): Mitigated if Price touches Bottom or goes higher
            if array.type in ['SWING_HIGH', 'FVG_BEAR']:
                if high >= array.bottom: # Simple touch mitigation
                    array.mitigated = True
                    array.mitigation_index = current_idx
            
            # Bullish Arrays (Support): Mitigated if Price touches Top or goes lower
            elif array.type in ['SWING_LOW', 'FVG_BULL']:
                if low <= array.top:
                    array.mitigated = True
                    array.mitigation_index = current_idx

    def get_unmitigated_opposing(self, direction: str, current_price: float) -> List[PDArray]:
        """
        Returns list of unmitigated arrays that stand in the way of the trend.
        """
        opposing = []
        if direction == 'BULLISH':
            # Look for Bearish Arrays above current price (Resistance)
            # Or just Bearish Arrays that are unmitigated (could be slightly below if just wicked)
            opposing = [a for a in self.arrays if a.type in ['SWING_HIGH', 'FVG_BEAR'] and not a.mitigated]
        elif direction == 'BEARISH':
            # Look for Bullish Arrays below current price (Support)
            opposing = [a for a in self.arrays if a.type in ['SWING_LOW', 'FVG_BULL'] and not a.mitigated]
        return opposing

# ==========================================
# 4. STRATEGY LOGIC: CREATED AT RESISTANCE
# ==========================================
class Ep6Strategy:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.manager = PDArrayManager()
        self.setups: List[TradeSetup] = []

    def detect_swings(self, i: int):
        lb = config.swing_lookback
        if i < lb or i >= len(self.df) - lb: return
        
        # Swing High
        if self.df['high'].iloc[i] == self.df['high'].iloc[i-lb:i+lb+1].max():
            self.manager.add_array('SWING_HIGH', self.df['high'].iloc[i], self.df['high'].iloc[i], i)
        
        # Swing Low
        if self.df['low'].iloc[i] == self.df['low'].iloc[i-lb:i+lb+1].min():
            self.manager.add_array('SWING_LOW', self.df['low'].iloc[i], self.df['low'].iloc[i], i)

    def detect_new_fvg(self, i: int) -> Optional[PDArray]:
        # Standard ICT FVG detection (Gap between i-2 and i)
        # Checked at close of candle i
        if i < 2: return None
        
        # Bullish FVG
        if self.df['low'].iloc[i] > self.df['high'].iloc[i-2]:
            gap = self.df['low'].iloc[i] - self.df['high'].iloc[i-2]
            if gap > config.min_fvg_size:
                # Create temp object, added to manager later if needed
                return PDArray("temp", "FVG_BULL", self.df['low'].iloc[i], self.df['high'].iloc[i-2], i-1)
        
        # Bearish FVG
        if self.df['high'].iloc[i] < self.df['low'].iloc[i-2]:
            gap = self.df['low'].iloc[i-2] - self.df['high'].iloc[i]
            if gap > config.min_fvg_size:
                return PDArray("temp", "FVG_BEAR", self.df['low'].iloc[i-2], self.df['high'].iloc[i], i-1)
        
        return None

    def run(self):
        print("Running Ep 6 Logic: FVG Created at Resistance...")
        
        # Tracking recent interactions
        # {index_of_interaction: opposing_array_obj}
        recent_interactions: Dict[int, PDArray] = {}
        
        for i in range(len(self.df)):
            current_candle = self.df.iloc[i]
            
            # 1. Detect Swings formed at 'i' (actually identified after lookback, but for sim we check structure)
            # In live stream logic, we usually check i-lb. Here simplified for loop.
            self.detect_swings(i)
            
            # 2. Check Mitigations (Did we hit something?)
            # Before checking, get list of unmitigated
            # We essentially check if we hit an opposing array in this candle
            # Optimization: Only check arrays that exist before i
            active_arrays = [a for a in self.manager.arrays if a.creation_index < i and not a.mitigated]
            
            hit_array = None
            for array in active_arrays:
                # Check Bearish Interaction (We are moving up into Bearish Array)
                if array.type in ['SWING_HIGH', 'FVG_BEAR']:
                    if current_candle['high'] >= array.bottom:
                        hit_array = array
                        # Mark as mitigated in manager
                        array.mitigated = True
                        array.mitigation_index = i
                        break # Only register first significant hit for simplicity
                
                # Check Bullish Interaction (We are moving down into Bullish Array)
                elif array.type in ['SWING_LOW', 'FVG_BULL']:
                    if current_candle['low'] <= array.top:
                        hit_array = array
                        array.mitigated = True
                        array.mitigation_index = i
                        break

            if hit_array:
                recent_interactions[i] = hit_array
            
            # Clean up old interactions outside window
            recent_interactions = {k:v for k,v in recent_interactions.items() if i - k <= config.reaction_window}

            # 3. Detect New FVG Formation
            new_fvg = self.detect_new_fvg(i)
            if new_fvg:
                # Add to manager regardless
                self.manager.add_array(new_fvg.type, new_fvg.top, new_fvg.bottom, new_fvg.creation_index)
                
                # 4. QUALITY FILTER: Was this FVG created due to a recent interaction?
                # Check if we interacted with an opposing array in the last 'window' candles
                # If Bullish FVG, we need a Bearish Array interaction
                if new_fvg.type == 'FVG_BULL':
                    valid_trigger = None
                    for idx, trigger_array in recent_interactions.items():
                        if trigger_array.type in ['SWING_HIGH', 'FVG_BEAR']:
                            valid_trigger = trigger_array
                            break
                    if valid_trigger:
                        self.setups.append(TradeSetup('LONG', new_fvg, valid_trigger, self.df.index[i]))
                
                # If Bearish FVG, we need a Bullish Array interaction
                elif new_fvg.type == 'FVG_BEAR':
                    valid_trigger = None
                    for idx, trigger_array in recent_interactions.items():
                        if trigger_array.type in ['SWING_LOW', 'FVG_BULL']:
                            valid_trigger = trigger_array
                            break
                    if valid_trigger:
                        self.setups.append(TradeSetup('SHORT', new_fvg, valid_trigger, self.df.index[i]))

    def report(self):
        print(f"Total Setups Found: {len(self.setups)}")
        for setup in self.setups[-5:]:
            print(f"\n--- {setup.direction} SETUP ---")
            print(f"Time: {setup.timestamp}")
            print(f"Trigger: Price hit unmitigated {setup.opposing_array_hit.type} (Created at idx {setup.opposing_array_hit.creation_index})")
            print(f"Result: Created High Prob {setup.entry_fvg.type} at {setup.entry_fvg.bottom:.4f} - {setup.entry_fvg.top:.4f}")

# ==========================================
# 5. EXECUTION WRAPPER
# ==========================================
def run_arjo_ep6():
    # Generate synthetic data: Uptrend hitting resistance and reacting
    np.random.seed(42)
    periods = 200
    dates = pd.date_range(start='2024-01-01', periods=periods, freq='4h')
    
    price = 100.0
    data = []
    
    # Create a Bearish Swing High early on (Resistance)
    # Then price drops, then rallies back up to hit it
    for i in range(periods):
        # Simple logic to create specific scenario
        if i == 20: price = 105.0 # High
        elif i == 21: price = 104.0 # Swing High formed at 105
        elif i > 21 and i < 50: price -= 0.5 # Drop
        elif i >= 50 and i < 80: price += 0.8 # Rally back up
        # At i=80, price is around 104-105 (Hitting resistance)
        # At i=82, create a bullish displacement (FVG)
        elif i == 82: price += 2.0 
        else: price += np.random.randn() * 0.5
        
        open_ = price
        close = price + (np.random.randn() * 0.2)
        high = max(open_, close) + 0.1
        low = min(open_, close) - 0.1
        
        data.append([open_, high, low, close])

    df = pd.DataFrame(data, columns=['open', 'high', 'low', 'close'], index=dates)
    
    strategy = Ep6Strategy(df)
    strategy.run()
    strategy.report()

if __name__ == "__main__":
    run_arjo_ep6()
