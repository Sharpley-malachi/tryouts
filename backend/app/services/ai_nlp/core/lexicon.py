class TradingLexicon:
    FOREX = {
        "unit": "Pips",
        "liquidity_source": "Bank Sessions (London/NY)",
        "drivers": "Interest Rates / Central Banks",
        "description": "Currency Pair Correlation",
        "volatility_terms": ["Expansion", "Slippage", "Stop Hunt"],
        "adjectives": ["Violent", "Liquid", "Manipulated", "Structured"]
    }

    INDICES = {
        "unit": "Points",
        "liquidity_source": "Market Open / Power Hour",
        "drivers": "Sector Weighting / Earnings",
        "description": "Intraday Trend Persistence",
        "volatility_terms": ["Opening Drive", "Rejection at VWAP", "Gamma Exposure"],
        "adjectives": ["Aggressive", "Trending", "Momentum-driven", "Algorithmically Driven"]
    }

    @classmethod
    def get_lexicon(cls, market_type):
        return cls.FOREX if "FOREX" in market_type.upper() or "=" in market_type else cls.INDICES
