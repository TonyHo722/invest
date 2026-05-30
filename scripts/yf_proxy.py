import yfinance as yf
import json
import os
import time
import pandas as pd
from datetime import datetime
from threading import Lock

class RateLimiter:
    def __init__(self, max_requests=100, period=60.0):
        self.max_requests = max_requests
        self.period = period
        self.requests = []
        self.lock = Lock()

    def wait_if_needed(self):
        with self.lock:
            now = time.time()
            self.requests = [t for t in self.requests if now - t < self.period]
            if len(self.requests) >= self.max_requests:
                oldest = self.requests[0]
                sleep_time = self.period - (now - oldest)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                now = time.time()
            self.requests.append(now)

_limiter = RateLimiter(max_requests=100, period=60.0)

CACHE_DIR = "scratch/cache"

def get_cache_dir():
    """Returns the effective cache directory (daily or debug)."""
    if os.environ.get('YF_DEBUG') == '1':
        debug_dir = os.path.join(CACHE_DIR, "debug")
        if os.path.exists(debug_dir):
            return debug_dir
    return os.path.join(CACHE_DIR, datetime.now().strftime("%Y%m%d"))

def get_cached_ticker(ticker_sym):
    """
    A proxy for yf.Ticker that caches data locally to disk.
    If data exists for today, it returns the cached version.
    """
    cache_dir = get_cache_dir()
    cache_path = os.path.join(cache_dir, f"{ticker_sym}.json")
    
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                # Check if all required keys are present (handle migration for quarterly data)
                if "quarterly_financials" in cached_data:
                    return cached_data
                print(f"🔄 Cache for {ticker_sym} is missing quarterly data. Re-fetching...")
        except Exception:
            pass

    _limiter.wait_if_needed()
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
            "quarterly_financials": df_to_dict(t.quarterly_financials),
            "quarterly_balance_sheet": df_to_dict(t.quarterly_balance_sheet),
            "quarterly_cashflow": df_to_dict(t.quarterly_cashflow),
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

def try_datetime(idx):
    """Tries to convert an index/column to datetime if it looks like a date."""
    try:
        if len(idx) == 0: return idx
        # Check if the first element looks like a date string (YYYY-MM-DD)
        first_val = str(idx[0])
        if len(first_val) >= 7 and '-' in first_val:
            return pd.to_datetime(idx, utc=True)
    except:
        pass
    return idx

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
            self.quarterly_financials = pd.DataFrame()
            self.quarterly_balance_sheet = pd.DataFrame()
            self.quarterly_cashflow = pd.DataFrame()
            self.dividends = pd.Series()
            self.history_5y = pd.DataFrame()
            return

        self.info = self.data.get("info", {})
        
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
        self.quarterly_financials = restore_df("quarterly_financials")
        self.quarterly_balance_sheet = restore_df("quarterly_balance_sheet")
        self.quarterly_cashflow = restore_df("quarterly_cashflow")
        
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
    
    cache_dir = get_cache_dir()
    cache_path = os.path.join(cache_dir, f"batch_{key_hash}.pkl")
    
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    
    if os.path.exists(cache_path):
        try:
            print(f"📦 Loading cached batch data ({len(tickers)} tickers)...")
            return pd.read_pickle(cache_path), True
        except Exception:
            pass
            
    print(f"📡 Downloading live batch data for {len(tickers)} tickers...")
    df = yf.download(tickers, **kwargs)
    
    if not df.empty:
        try:
            df.to_pickle(cache_path)
        except Exception as e:
            print(f"⚠️ Failed to cache batch: {e}")
            
    return df, False

def get_cached_list(list_key, fetch_func):
    """
    Caches a list (like ticker symbols) for the day.
    """
    cache_dir = get_cache_dir()
    cache_path = os.path.join(cache_dir, f"list_{list_key}.json")
    
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                print(f"📦 Loading cached ticker list for {list_key}...")
                return json.load(f)
        except Exception:
            pass
            
    print(f"📡 Fetching live ticker list for {list_key}...")
    data = fetch_func()
    
    if data:
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Failed to cache list: {e}")
            
    return data
