from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# --- ASSETS ---
ASSETS = {
    "CURRENCIES": ["AUDJPY=X", "GBPAUD=X", "EURUSD=X", "USDCAD=X", "EURCHF=X"],
    "STOCKS": ["MSFT", "NVDA", "META"],
    "INDICES": ["^IXIC", "^GSPC", "^DJI"]  # Nasdaq, S&P 500, Dow Jones
}

# --- TIMEFRAMES ---
# yfinance keys mapped to your system's names
TIMEFRAMES = {
    "4H": "60m",  # We fetch 1H and resample to 4H for accuracy
    "DAILY": "1d",
    "WEEKLY": "1wk",
    "MONTHLY": "1mo"
}

def get_training_date_range():
    """
    Calculates the last 12 months excluding the current month.
    """
    today = datetime.now()
    # First day of this month
    first_of_this_month = today.replace(day=1)
    # Last day of previous month
    end_date = first_of_this_month - timedelta(days=1)
    # 12 months before that
    start_date = (first_of_this_month - relativedelta(months=12))
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
