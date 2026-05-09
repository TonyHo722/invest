import yfinance as yf
import json
import os
import pandas as pd
from datetime import datetime

CACHE_DIR = "scratch/cache"

def get_cached_ticker(ticker_sym):
    """
    A proxy for yf.Ticker that caches data locally to disk.
    If data exists for today, it returns the cached version.
    """
    today_str = datetime.now().strftime("%Y%m%d")
    cache_path = os.path.join(CACHE_DIR, today_str, f"{ticker_sym}.json")
    
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass

    print(f"📡 Fetching live data for {ticker_sym}...")
    try:
        t = yf.Ticker(ticker_sym)
        
        # Helper to convert DF to dict with string index
        def df_to_dict(df):
            if df.empty: return {}
            # Ensure index is strings
            df_copy = df.copy()
            df_copy.index = df_copy.index.astype(str)
            df_copy.columns = df_copy.columns.astype(str)
            return df_copy.to_dict()

        data = {
            "info": t.info,
            "financials": df_to_dict(t.financials),
            "balance_sheet": df_to_dict(t.balance_sheet),
            "cashflow": df_to_dict(t.cashflow),
            "dividends": {str(k): v for k, v in t.dividends.to_dict().items()} if not t.dividends.empty else {},
            "history_5y": df_to_dict(t.history(period="5y"))
        }
        
        try:
            shares = t.get_shares_full(start=datetime(datetime.now().year-5, 1, 1))
            data["shares"] = {str(k): v for k, v in shares.to_dict().items()} if not shares.empty else {}
        except:
            data["shares"] = {}

        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        return data
    except Exception as e:
        print(f"⚠️ Error fetching {ticker_sym}: {e}")
        return None

class ProxyTicker:
    def __init__(self, ticker_sym):
        self.ticker_sym = ticker_sym
        self.data = get_cached_ticker(ticker_sym)
        
        self.info = self.data.get("info", {}) if self.data else {}
        self.financials = pd.DataFrame.from_dict(self.data.get("financials", {})) if self.data else pd.DataFrame()
        self.balance_sheet = pd.DataFrame.from_dict(self.data.get("balance_sheet", {})) if self.data else pd.DataFrame()
        self.cashflow = pd.DataFrame.from_dict(self.data.get("cashflow", {})) if self.data else pd.DataFrame()
        
        div_dict = self.data.get("dividends", {}) if self.data else {}
        self.dividends = pd.Series(div_dict) if div_dict else pd.Series()
        if not self.dividends.empty:
            self.dividends.index = pd.to_datetime(self.dividends.index, utc=True)
            
        hist_dict = self.data.get("history_5y", {}) if self.data else {}
        self.history_5y = pd.DataFrame.from_dict(hist_dict) if hist_dict else pd.DataFrame()
        if not self.history_5y.empty:
            self.history_5y.index = pd.to_datetime(self.history_5y.index, utc=True)

    def history(self, start=None, end=None, **kwargs):
        if self.history_5y.empty:
            return pd.DataFrame()
        
        df = self.history_5y
        # Convert index to UTC for safe comparison if needed, or just compare as strings/datetimes
        if start:
            start_dt = pd.to_datetime(start, utc=True)
            df = df[df.index >= start_dt]
        if end:
            end_dt = pd.to_datetime(end, utc=True)
            df = df[df.index <= end_dt]
        return df

    def get_shares_full(self, **kwargs):
        sh_dict = self.data.get("shares", {}) if self.data else {}
        if not sh_dict: return pd.Series()
        s = pd.Series(sh_dict)
        s.index = pd.to_datetime(s.index, utc=True)
        return s
