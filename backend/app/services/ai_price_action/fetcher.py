import yfinance as yf
import pandas as pd
import os
import json
from .config import ASSETS, TIMEFRAMES, get_training_date_range
from .processor import DataProcessor

class DataAgent:
    def __init__(self, data_dir="data"):
        self.processor = DataProcessor()
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def fetch_automated_data(self):
        """
        Connects to API (yfinance) to fetch training data.
        """
        start_date, end_date = get_training_date_range()
        full_database = {}
        print(f"--- AI #1: Fetching Data [{start_date} to {end_date}] ---")

        all_tickers = ASSETS['CURRENCIES'] + ASSETS['STOCKS'] + ASSETS['INDICES']

        for ticker in all_tickers:
            print(f"Processing {ticker}...")
            ticker_data = {}
            
            try:
                # 1. Fetch Monthly, Weekly, Daily directly
                for tf_name, tf_code in TIMEFRAMES.items():
                    if tf_name == '4H': continue  # Handle separately
                    
                    raw_df = yf.download(ticker, start=start_date, end=end_date, interval=tf_code, progress=False)
                    if raw_df.empty:
                         print(f"Warning: No data for {ticker} {tf_name}")
                         continue
                         
                    # Fix multi-index columns if present (yfinance update)
                    if isinstance(raw_df.columns, pd.MultiIndex):
                        raw_df.columns = raw_df.columns.get_level_values(0)

                    processed_df = self.processor.add_visual_attributes(raw_df)
                    ticker_data[tf_name] = processed_df

                # 2. Fetch Hourly and transform to 4H (yfinance limitation workaround)
                # Note: yfinance 1h data is limited to 730 days. 12 months fits within this.
                raw_1h = yf.download(ticker, start=start_date, end=end_date, interval="1h", progress=False)
                if not raw_1h.empty:
                    if isinstance(raw_1h.columns, pd.MultiIndex):
                        raw_1h.columns = raw_1h.columns.get_level_values(0)
                        
                    df_4h = self.processor.resample_1h_to_4h(raw_1h)
                    ticker_data['4H'] = self.processor.add_visual_attributes(df_4h)
                else:
                    print(f"Warning: No 1H data for {ticker}")

                # 3. Create Hierarchy
                hierarchy = self.processor.align_hierarchies(ticker_data)
                full_database[ticker] = hierarchy
            except Exception as e:
                print(f"Error processing {ticker}: {e}")

        return full_database

    def save_to_local_storage(self, data):
        """
        Saves the aligned hierarchical JSON to local file system.
        """
        # Save one JSON file per asset
        strategies_dir = os.path.join(self.data_dir, "pipeline_storage")
        if not os.path.exists(strategies_dir):
            os.makedirs(strategies_dir)

        count = 0 
        for ticker, hierarchy in data.items():
            clean_name = ticker.replace("=X", "").replace("^", "")
            file_path = os.path.join(strategies_dir, f"{clean_name}.json")
            
            # Serialize dates properly
            with open(file_path, 'w') as f:
                json.dump(hierarchy, f, default=str, indent=2)
            count += 1
            
        print(f"Successfully saved {count} assets to local storage.")
        return count
