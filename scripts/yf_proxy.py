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
        
        # Helper to convert DF to dict with string index/columns
        def df_to_dict(df):
            if df is None or (isinstance(df, pd.DataFrame) and df.empty): return {}
            # Ensure index and columns are strings for JSON serialization
            df_copy = df.copy()
            df_copy.index = df_copy.index.astype(str)
            if isinstance(df_copy, pd.DataFrame):
                df_copy.columns = df_copy.columns.astype(str)
            return df_copy.to_dict()

        data = {
            "info": t.info,
            "financials": df_to_dict(t.financials),
            "balance_sheet": df_to_dict(t.balance_sheet),
            "cashflow": df_to_dict(t.cashflow),
            "dividends": df_to_dict(t.dividends),
            "history_5y": df_to_dict(t.history(period="5y"))
        }
        
        try:
            shares = t.get_shares_full(start=datetime(datetime.now().year-5, 1, 1))
            data["shares"] = df_to_dict(shares)
        except:
            data["shares"] = {}

        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        return data
    except Exception as e:
        print(f"⚠️ Error fetching {ticker_sym}: {e}")
        return None

class ProxyTicker:
    """A wrapper that mimics yf.Ticker but uses cached data and returns proper DataFrames."""
    def __init__(self, ticker_sym):
        self.ticker_sym = ticker_sym
        self.data = get_cached_ticker(ticker_sym)
        
        if not self.data:
            self.info = {}
            self.financials = pd.DataFrame()
            self.balance_sheet = pd.DataFrame()
            self.cashflow = pd.DataFrame()
            self.dividends = pd.Series()
            self.history_5y = pd.DataFrame()
            return

        self.info = self.data.get("info", {})
        
        def try_datetime(idx):
            """Tries to convert an index/column to datetime if it looks like a date."""
            try:
                # Check if the first element looks like a date string (YYYY-MM-DD)
                first_val = str(idx[0])
                if len(first_val) >= 7 and '-' in first_val:
                    return pd.to_datetime(idx, utc=True)
            except:
                pass
            return idx

        # Helper to restore DataFrame and convert index/columns back to datetime
        def restore_df(key):
            d = self.data.get(key, {})
            if not d: return pd.DataFrame()
            df = pd.DataFrame.from_dict(d)
            
            # Check rows
            df.index = try_datetime(df.index)
            # Check columns
            df.columns = try_datetime(df.columns)
            
            # Sort if it's a time series (index is datetime)
            if isinstance(df.index, pd.DatetimeIndex):
                df = df.sort_index()
                
            return df

        self.financials = restore_df("financials")
        self.balance_sheet = restore_df("balance_sheet")
        self.cashflow = restore_df("cashflow")
        
        # Restore dividends (Series)
        div_dict = self.data.get("dividends", {})
        if div_dict:
            s = pd.Series(div_dict)
            s.index = try_datetime(s.index)
            if isinstance(s.index, pd.DatetimeIndex):
                s = s.sort_index()
            self.dividends = s
        else:
            self.dividends = pd.Series()
            
        self.history_5y = restore_df("history_5y")

    def history(self, start=None, end=None, **kwargs):
        """Mock history method using cached 5y data."""
        if self.history_5y.empty:
            return pd.DataFrame()
        
        df = self.history_5y
        if start and isinstance(df.index, pd.DatetimeIndex):
            start_dt = pd.to_datetime(start, utc=True)
            df = df[df.index >= start_dt]
        if end and isinstance(df.index, pd.DatetimeIndex):
            end_dt = pd.to_datetime(end, utc=True)
            df = df[df.index <= end_dt]
        return df

    def get_shares_full(self, **kwargs):
        """Mock shares history."""
        sh_dict = self.data.get("shares", {})
        if not sh_dict: return pd.Series()
        s = pd.Series(sh_dict)
        s.index = try_datetime(s.index)
        if isinstance(s.index, pd.DatetimeIndex):
            s = s.sort_index()
        return s

def proxy_download(tickers, **kwargs):
    """
    A proxy for yf.download that caches results to disk.
    """
    import hashlib
    
    # Create a unique key for this request
    key_str = f"{sorted(tickers)}_{kwargs.get('period')}_{kwargs.get('interval')}"
    key_hash = hashlib.md5(key_str.encode()).hexdigest()
    
    today_str = datetime.now().strftime("%Y%m%d")
    cache_path = os.path.join(CACHE_DIR, today_str, f"batch_{key_hash}.pkl")
    
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    
    if os.path.exists(cache_path):
        try:
            print(f"📦 Loading cached batch data ({len(tickers)} tickers)...")
            return pd.read_pickle(cache_path)
        except Exception:
            pass
            
    print(f"📡 Downloading live batch data for {len(tickers)} tickers...")
    df = yf.download(tickers, **kwargs)
    
    if not df.empty:
        try:
            df.to_pickle(cache_path)
        except Exception as e:
            print(f"⚠️ Failed to cache batch: {e}")
            
    return df
