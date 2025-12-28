import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

# ==========================================
# 1. CONFIGURATION
# ==========================================
@dataclass
class Config:
    # Thresholds for "Small" and "Long" wicks as a percentage of the total candle range.
    # Arjo describes them visually; we translate this to ratios.
    small_wick_ratio: float = 0.20 # Wick is < 20% of range
    long_wick_ratio: float = 0.40  # Wick is > 40% of range
    # Backtesting target lookahead (1 candle)
    prediction_horizon: int = 1

config = Config()

# ==========================================
# 2. DATA STRUCTURES
# ==========================================
@dataclass
class CandleClassification:
    timestamp: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    type: str # 'DISRESPECT_BULL', 'DISRESPECT_BEAR', 'RESPECT_BULL', 'RESPECT_BEAR', 'INDECISION'
    bias: str # 'BULLISH', 'BEARISH', 'NEUTRAL'
    description: str

# ==========================================
# 3. CANDLE SCIENCE ENGINE
# ==========================================
class CandleScienceClassifier:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.classifications: List[CandleClassification] = []

    def _analyze_single_candle(self, row) -> CandleClassification:
        open_ = row['open']
        high = row['high']
        low = row['low']
        close = row['close']
        total_range = high - low
        
        if total_range == 0:
             return CandleClassification(row.name, open_, high, low, close, 'DOJI', 'NEUTRAL', 'No Range')

        body_size = abs(close - open_)
        upper_wick = high - max(open_, close)
        lower_wick = min(open_, close) - low
        
        upper_ratio = upper_wick / total_range
        lower_ratio = lower_wick / total_range
        
        candle_type = 'INDECISION'
        bias = 'NEUTRAL'
        desc = 'Consolidation/Neutral'

        # --- LOGIC 1: DISRESPECT CANDLES (CONTINUATION) ---
        # Bullish Disrespect: Up close, small upper wick
        if close > open_:
            if upper_ratio <= config.small_wick_ratio:
                candle_type = 'DISRESPECT_BULL'
                bias = 'BULLISH'
                desc = 'Bullish Disrespect (Continuation)'
        
        # Bearish Disrespect: Down close, small lower wick
        elif close < open_:
            if lower_ratio <= config.small_wick_ratio:
                candle_type = 'DISRESPECT_BEAR'
                bias = 'BEARISH'
                desc = 'Bearish Disrespect (Continuation)'

        # --- LOGIC 2: RESPECT CANDLES (REVERSAL/REJECTION) ---
        # Overrides Disrespect if the wick is extremely significant (Order Flow Reversal)
        
        # Bullish Respect: Long Lower Wick (Price went down, rejected, closed higher relative to low)
        # Note: Can be a red or green candle, the wick is what matters.
        if lower_ratio >= config.long_wick_ratio:
            # If it was already labeled disrespect bull, this reinforces it or changes context.
            # Arjo emphasizes the wick.
            candle_type = 'RESPECT_BULL'
            bias = 'BULLISH'
            desc = 'Bullish Respect (Rejection of Lows)'
            
        # Bearish Respect: Long Upper Wick
        if upper_ratio >= config.long_wick_ratio:
             candle_type = 'RESPECT_BEAR'
             bias = 'BEARISH'
             desc = 'Bearish Respect (Rejection of Highs)'
        
        # Conflict Check: What if both wicks are long? (Spinning Top/High Volatility)
        if lower_ratio >= config.long_wick_ratio and upper_ratio >= config.long_wick_ratio:
             candle_type = 'INDECISION'
             bias = 'NEUTRAL'
             desc = 'Indecision (Both sides rejected)'

        return CandleClassification(
            timestamp=row.name,
            open=open_, high=high, low=low, close=close,
            type=candle_type,
            bias=bias,
            description=desc
        )

    def analyze(self) -> pd.DataFrame:
        results = []
        for index, row in self.df.iterrows():
            results.append(self._analyze_single_candle(row))
        self.classifications = results
        
        # Convert to DataFrame for easy viewing
        res_df = pd.DataFrame([vars(c) for c in results])
        if not res_df.empty:
            res_df.set_index('timestamp', inplace=True)
        return res_df

# ==========================================
# 4. TOP-DOWN BIAS BUILDER
# ==========================================
def generate_top_down_bias(df_hourly: pd.DataFrame):
    """
    Simulates the Monthly -> Weekly -> Daily analysis flow described in the video.
    """
    print("\n--- Top Down Candle Science Analysis ---")
    
    # Resample to Monthly
    df_monthly = df_hourly.resample('M').agg({
        'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'
    }).dropna()
    
    # Resample to Weekly
    df_weekly = df_hourly.resample('W').agg({
        'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'
    }).dropna()
    
    # Analyze last closed Monthly Candle
    if len(df_monthly) > 1:
        last_month = df_monthly.iloc[-2] # -1 is current open candle, -2 is last closed
        classifier = CandleScienceClassifier(df_monthly)
        m_class = classifier._analyze_single_candle(last_month)
        
        print(f"\n[MONTHLY] Last Closed Candle: {last_month.name.strftime('%Y-%m')}")
        print(f"Type: {m_class.type}")
        print(f"Bias for Current Month: {m_class.bias} ({m_class.description})")
        
        # Analyze last closed Weekly Candle
        if len(df_weekly) > 1:
            last_week = df_weekly.iloc[-2]
            w_class = classifier._analyze_single_candle(last_week)
            
            print(f"\n[WEEKLY] Last Closed Candle: {last_week.name.strftime('%Y-%m-%d')}")
            print(f"Type: {w_class.type}")
            print(f"Bias for Current Week: {w_class.bias} ({w_class.description})")
            
            # Confluence Check
            if m_class.bias == w_class.bias and m_class.bias != 'NEUTRAL':
                print(f"\n>> CONFLUENCE DETECTED: FULL {m_class.bias} BIAS")
                print(f"Strategy: Look for {m_class.bias.lower()} Order Flow Legs on Daily/4H.")
            elif m_class.bias != 'NEUTRAL' and w_class.bias != 'NEUTRAL':
                print(f"\n>> CONFLICT: Monthly {m_class.bias} vs Weekly {w_class.bias}")
                print("Strategy: Wait for Weekly alignment or trade Weekly bias cautiously into Monthly PD arrays.")
            else:
                 print("\n>> NEUTRAL/INDECISION Context.")

# ==========================================
# 5. EXECUTION WRAPPER
# ==========================================
def run_arjo_ep4():
    # Generate dummy hourly data for 3 months
    dates = pd.date_range(start='2024-01-01', end='2024-04-01', freq='1h')
    np.random.seed(42)
    
    # Create a trending market structure (Bullish)
    price = 100
    opens, highs, lows, closes = [], [], [], []
    
    for _ in dates:
        change = np.random.randn() + 0.05 # Slight bullish drift
        open_p = price
        close_p = price + change
        high_p = max(open_p, close_p) + abs(np.random.randn()*0.3)
        low_p = min(open_p, close_p) - abs(np.random.randn()*0.3)
        
        opens.append(open_p)
        highs.append(high_p)
        lows.append(low_p)
        closes.append(close_p)
        price = close_p
        
    df = pd.DataFrame({
        'open': opens, 'high': highs, 'low': lows, 'close': closes
    }, index=dates)
    
    # Run the analysis
    generate_top_down_bias(df)
    
    # Detailed check on a subset of Daily candles
    print("\n--- Daily Candle Science Check (Last 5 Days) ---")
    df_daily = df.resample('D').agg({
        'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'
    }).dropna()
    
    classifier = CandleScienceClassifier(df_daily)
    daily_results = classifier.analyze()
    print(daily_results[['type', 'bias', 'description']].tail(5).to_string())

if __name__ == "__main__":
    run_arjo_ep4()
