import pandas as pd
import numpy as np

class DataProcessor:
    def __init__(self):
        pass

    def add_visual_attributes(self, df):
        """
        Adds Color (Green/Red) and 2D Geometry (Rectangle/Line) logic.
        """
        # Ensure proper columns exist
        required_cols = ['Open', 'High', 'Low', 'Close']
        if not all(col in df.columns for col in required_cols):
             return df
             
        # 1. Color Coding
        df['color'] = np.where(df['Close'] >= df['Open'], 'GREEN', 'RED')

        # 2. 2D Geometry Transformation
        # Body Rectangle: Y-coordinates for the box
        df['body_top'] = df[['Open', 'Close']].max(axis=1)
        df['body_bottom'] = df[['Open', 'Close']].min(axis=1)

        # Wick Lines: Y-coordinates for the lines
        df['wick_top'] = df['High']
        df['wick_bottom'] = df['Low']
        
        return df

    def resample_1h_to_4h(self, df_1h):
        """
        Aggregates 1H data into 4H candles to ensure precision.
        """
        conversion = {
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }
        # Verify columns exist before aggregation
        conversion = {k: v for k, v in conversion.items() if k in df_1h.columns}
        
        # Resample every 4 hours based on time
        df_4h = df_1h.resample('4H').agg(conversion).dropna()
        return df_4h

    def align_hierarchies(self, data_package):
        """
        The Arjo Logic: Nesting Timeframes.
        Links 4H candles to their parent Daily candle, etc.
        """
        # Convert index to column for processing
        for tf in data_package:
            if not isinstance(data_package[tf].index, pd.DatetimeIndex):
                data_package[tf].index = pd.to_datetime(data_package[tf].index)

        # We start from the top (Monthly) and link downwards
        # Handle missing keys gracefully
        if not all(k in data_package for k in ['MONTHLY', 'WEEKLY', 'DAILY', '4H']):
            return []

        monthly = data_package['MONTHLY']
        weekly = data_package['WEEKLY']
        daily = data_package['DAILY']
        four_hour = data_package['4H']

        aligned_data = []

        for m_date, m_row in monthly.iterrows():
            m_start = m_date
            m_end = m_date + pd.tseries.offsets.MonthEnd(0)

            # Find weeks inside this month
            weeks_in_month = weekly[(weekly.index >= m_start) & (weekly.index <= m_end)]
            weeks_data = []

            for w_date, w_row in weeks_in_month.iterrows():
                # Find days inside this week
                # Approximation: Week start to +7 days
                w_end = w_date + pd.Timedelta(days=6)
                days_in_week = daily[(daily.index >= w_date) & (daily.index <= w_end)]
                days_data = []

                for d_date, d_row in days_in_week.iterrows():
                    # Find 4H blocks inside this day
                    d_end = d_date + pd.Timedelta(hours=23, minutes=59)
                    four_h_in_day = four_hour[(four_hour.index >= d_date) & (four_hour.index <= d_end)]

                    days_data.append({
                        "date": d_date.strftime('%Y-%m-%d'),
                        "ohlc": d_row.to_dict(),
                        "children_4h": four_h_in_day.reset_index().to_dict(orient='records')
                    })

                weeks_data.append({
                    "date": w_date.strftime('%Y-%m-%d'),
                    "ohlc": w_row.to_dict(),
                    "children_daily": days_data
                })

            aligned_data.append({
                "period": m_date.strftime('%Y-%m'),
                "ohlc": m_row.to_dict(),
                "children_weekly": weeks_data
            })

        return aligned_data
