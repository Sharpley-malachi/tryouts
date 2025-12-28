import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
@dataclass
class Config:
    # Arjo mentions "Swing Points" but doesn't define the lookback in this intro.
    # We use a standard short-term swing definition to allow the code to function.
    swing_lookback: int = 3
    # Arjo mentions FVGs. Standard ICT definition applies until he refines it in Video 2.
    use_fvgs: bool = True
    # "Fair Value Area" is mentioned but undefined in video.
    # Placeholder boolean to enable logic once defined in future code updates.
    use_fair_value_areas: bool = False
    # Logic: How close must price get to "hit" a PD array?
    tolerance_ticks: float = 0.0001
    
config = Config()

# ==========================================
# DATA STRUCTURES
# ==========================================
@dataclass
class PDArray:
    type: str # 'SWING_HIGH', 'SWING_LOW', 'FVG_BEAR', 'FVG_BULL'
    price_level: float # The specific price interest point (e.g., FVG start, Swing exact level)
    zone_top: float
    zone_bottom: float
    index: int
    mitigated: bool = False
    
    @property
    def is_premium(self):
        # Premium arrays push price down (Resistance)
        return self.type in ['SWING_HIGH', 'FVG_BEAR']
    
    @property
    def is_discount(self):
        # Discount arrays push price up (Support)
        return self.type in ['SWING_LOW', 'FVG_BULL']

# ==========================================
# MODULE 1: PD ARRAY DETECTION (The Tools)
# ==========================================
class PDArrayDetector:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.arrays: List[PDArray] = []

    def detect_swings(self):
        """
        Identifies Swing Points (Highs and Lows).
        Logic: A high is higher than N candles left and right.
        """
        lb = config.swing_lookback
        for i in range(lb, len(self.df) - lb):
            # Swing High
            if self.df['high'].iloc[i] == self.df['high'].iloc[i-lb:i+lb+1].max():
                self.arrays.append(PDArray(
                    type='SWING_HIGH',
                    price_level=self.df['high'].iloc[i],
                    zone_top=self.df['high'].iloc[i],
                    zone_bottom=self.df['high'].iloc[i], # Swings are often treated as specific levels
                    index=i
                ))
            # Swing Low
            if self.df['low'].iloc[i] == self.df['low'].iloc[i-lb:i+lb+1].min():
                self.arrays.append(PDArray(
                    type='SWING_LOW',
                    price_level=self.df['low'].iloc[i],
                    zone_top=self.df['low'].iloc[i],
                    zone_bottom=self.df['low'].iloc[i],
                    index=i
                ))

    def detect_fvgs(self):
        """
        Identifies Fair Value Gaps.
        Logic: Gap between Candle 1 and Candle 3.
        """
        if not config.use_fvgs: return
        
        for i in range(2, len(self.df)):
            # Bullish FVG (gap between Low[i] and High[i-2])
            if self.df['low'].iloc[i] > self.df['high'].iloc[i-2]:
                top = self.df['low'].iloc[i]
                bottom = self.df['high'].iloc[i-2]
                self.arrays.append(PDArray(
                    type='FVG_BULL',
                    price_level=bottom, # Usually interested in the refill to the bottom or top
                    zone_top=top,
                    zone_bottom=bottom,
                    index=i-1 # Formed at the middle candle
                ))
            
            # Bearish FVG (gap between High[i] and Low[i-2])
            if self.df['high'].iloc[i] < self.df['low'].iloc[i-2]:
                top = self.df['low'].iloc[i-2]
                bottom = self.df['high'].iloc[i]
                self.arrays.append(PDArray(
                    type='FVG_BEAR',
                    price_level=top,
                    zone_top=top,
                    zone_bottom=bottom,
                    index=i-1
                ))

    def detect_fair_value_areas(self):
        """
        Placeholder for 'Fair Value Area'.
        Arjo explicitly states this is for the next video.
        """
        pass

    def scan(self) -> List[PDArray]:
        self.detect_swings()
        self.detect_fvgs()
        self.detect_fair_value_areas()
        # Sort by index
        self.arrays.sort(key=lambda x: x.index)
        return self.arrays

# ==========================================
# MODULE 2: DIRECTIONAL BIAS LOGIC (The Strategy)
# ==========================================
class DirectionalBiasEngine:
    """
    Implements the video's core logic:
    "Price is always moving towards a PD Array."
    "We need to find out which PD Array we are moving towards next."
    """
    def __init__(self, df: pd.DataFrame, arrays: List[PDArray]):
        self.df = df
        self.arrays = arrays
        self.bias_log = []

    def get_active_pd_arrays(self, current_index: int) -> List[PDArray]:
        """Returns PD Arrays formed in the past relative to current_index."""
        return [a for a in self.arrays if a.index < current_index]

    def evaluate_direction(self):
        """
        Walks through the data.
        1. If price hits a Discount Array, Expectation = BULLISH -> Target nearest Premium Array.
        2. If price hits a Premium Array, Expectation = BEARISH -> Target nearest Discount Array.
        """
        active_bias = None # 'BULLISH' or 'BEARISH'
        target_array = None
        origin_array = None

        for i in range(config.swing_lookback, len(self.df)):
            current_high = self.df['high'].iloc[i]
            current_low = self.df['low'].iloc[i]
            
            past_arrays = self.get_active_pd_arrays(i)
            
            # Check for interaction with existing arrays
            for array in reversed(past_arrays): # Look at most recent first
                
                # Check interaction with Discount Array (Support)
                if array.is_discount:
                    # Logic: If price dips into/touches Discount
                    if current_low <= array.zone_top and current_high >= array.zone_bottom:
                        if active_bias != 'BULLISH':
                            # New Bullish Bias derived from "Trading FROM" a PD Array
                            active_bias = 'BULLISH'
                            origin_array = array
                            
                            # Find Target: Nearest Unmitigated Premium Array above
                            premiums = [a for a in past_arrays if a.is_premium and a.zone_bottom > current_low]
                            if premiums:
                                target_array = min(premiums, key=lambda x: x.zone_bottom)
                                
                                self.bias_log.append({
                                    'time': self.df.index[i],
                                    'index': i,
                                    'bias': 'BULLISH',
                                    'origin_type': array.type,
                                    'target_type': target_array.type,
                                    'target_price': target_array.zone_bottom,
                                    'status': 'OPEN'
                                })
                        break
                
                # Check interaction with Premium Array (Resistance)
                elif array.is_premium:
                    # Logic: If price pushes into/touches Premium
                    if current_high >= array.zone_bottom and current_low <= array.zone_top:
                        if active_bias != 'BEARISH':
                            # New Bearish Bias derived from "Trading FROM" a PD Array
                            active_bias = 'BEARISH'
                            origin_array = array
                            
                            # Find Target: Nearest Unmitigated Discount Array below
                            discounts = [a for a in past_arrays if a.is_discount and a.zone_top < current_high]
                            if discounts:
                                target_array = max(discounts, key=lambda x: x.zone_top)

                                self.bias_log.append({
                                    'time': self.df.index[i],
                                    'index': i,
                                    'bias': 'BEARISH',
                                    'origin_type': array.type,
                                    'target_type': target_array.type,
                                    'target_price': target_array.zone_top,
                                    'status': 'OPEN'
                                })
                        break

            # Check for Target Completion (The "Result" mentioned in the video)
            if self.bias_log and self.bias_log[-1]['status'] == 'OPEN':
                last_log = self.bias_log[-1]
                
                if last_log['bias'] == 'BULLISH':
                    # Hit Target?
                    if current_high >= last_log['target_price']:
                        last_log['status'] = 'SUCCESS (Target Hit)'
                        last_log['end_index'] = i
                    # Invalidated? (Price breaks below Origin)
                    elif current_low < origin_array.zone_bottom:
                        last_log['status'] = 'FAIL (Origin Broken)'
                        last_log['end_index'] = i
                        
                elif last_log['bias'] == 'BEARISH':
                    # Hit Target?
                    if current_low <= last_log['target_price']:
                        last_log['status'] = 'SUCCESS (Target Hit)'
                        last_log['end_index'] = i
                    # Invalidated? (Price breaks above Origin)
                    elif current_high > origin_array.zone_top:
                        last_log['status'] = 'FAIL (Origin Broken)'
                        last_log['end_index'] = i

        return pd.DataFrame(self.bias_log)

# ==========================================
# MODULE 3: AUTOMATIC BACKTESTING (Validation)
# ==========================================
def run_arjo_analysis(csv_path: str):
    """
    Runs the pipeline on a CSV.
    Expected CSV columns: 'timestamp', 'open', 'high', 'low', 'close'
    """
    # 1. Load Data
    try:
        df = pd.read_csv(csv_path)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
    except Exception as e:
        return f"Error loading CSV: {e}"

    # 2. Detect PD Arrays
    detector = PDArrayDetector(df)
    pd_arrays = detector.scan()
    print(f"Detected {len(pd_arrays)} PD Arrays.")

    # 3. Analyze Directional Bias
    engine = DirectionalBiasEngine(df, pd_arrays)
    results = engine.evaluate_direction()

    # 4. Generate Report
    if results is not None and not results.empty:
        total = len(results)
        success = len(results[results['status'] == 'SUCCESS (Target Hit)'])
        fail = len(results[results['status'] == 'FAIL (Origin Broken)'])
        open_trades = len(results[results['status'] == 'OPEN'])
        
        accuracy = (success / (success + fail)) * 100 if (success + fail) > 0 else 0
        
        print("\n=== MONEY MAKING CONCEPTS - EP 1 ANALYSIS ===")
        print(f"Total Directional Bias Signals: {total}")
        print(f"Successful Targets Reached: {success}")
        print(f"Bias Invalidated: {fail}")
        print(f"Arjo Directional Accuracy: {accuracy:.2f}%")
        print("\nSample Log:")
        print(results.tail())
        return results
    else:
        print("No directional bias shifts detected based on Swing/FVG interactions.")
        return None

# ==========================================
# FIREBASE HOOKS (SCAFFOLDING)
# ==========================================
def firebase_log_bias(bias_event: Dict):
    """
    Placeholder: Uploads the identified directional bias to Firebase.
    Structure: Arjo_MMC_Collection -> Document ID -> Fields
    """
    # db.collection('arjo_analysis').add(bias_event)
    pass

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # Create a dummy CSV for demonstration purposes since no file is present
    data = {
        'timestamp': pd.date_range(start='2023-01-01', periods=100, freq='H'),
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 102,
        'low': np.random.randn(100).cumsum() + 98,
        'close': np.random.randn(100).cumsum() + 100
    }
    # Ensure High is highest and Low is lowest
    df_dummy = pd.DataFrame(data)
    df_dummy['high'] = df_dummy[['open', 'close', 'high']].max(axis=1)
    df_dummy['low'] = df_dummy[['open', 'close', 'low']].min(axis=1)
    df_dummy.to_csv('dummy_ochl.csv', index=False)
    
    # Run Analysis
    run_arjo_analysis('dummy_ochl.csv')
