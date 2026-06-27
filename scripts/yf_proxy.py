import yfinance as yf
import json
import os
import time
import pandas as pd
from datetime import datetime
from threading import Lock

# Fetch max requests from environment if set, default to 50 requests per minute
max_req_env = os.environ.get('YF_MAX_REQUESTS')
default_max_requests = int(max_req_env) if max_req_env and max_req_env.isdigit() else 50

class RateLimiter:
    def __init__(self, max_requests=default_max_requests, period=60.0):
        self.max_requests = max_requests
        self.period = period
        self.requests = []
        self.lock = Lock()
        self.last_cooldown = 0.0

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
                self.requests = [t for t in self.requests if now - t < self.period]
            self.requests.append(now)
            return len(self.requests)

    def report_rate_limit(self, cooldown_duration=15.0):
        with self.lock:
            now = time.time()
            if now - self.last_cooldown < self.period:
                # Cooldown was already triggered recently, no need to repeat
                return
            print(f"\n⚠️ [Rate Limiter] Rate limit warning detected from Yahoo Finance! Cooling down for {cooldown_duration}s and pausing subsequent requests...")
            time.sleep(cooldown_duration)
            now = time.time()
            self.last_cooldown = now
            # Fill the requests history to block immediate new requests
            self.requests = [now] * self.max_requests

def auto_detect_splits_single(df):
    if df.empty or 'Close' not in df.columns:
        return df
    df = df.copy()
    if isinstance(df.index, pd.DatetimeIndex):
        df = df.sort_index()
        
    factors = [2, 3, 4, 5, 6, 7, 8, 10, 20, 50, 100]
    for i in range(1, len(df)):
        p_prev = df.iloc[i-1]['Close']
        p_curr = df.iloc[i]['Close']
        
        if pd.isna(p_prev) or pd.isna(p_curr) or p_prev <= 0 or p_curr <= 0:
            continue
            
        ratio = p_prev / p_curr
        
        # Check forward split
        for R in factors:
            if abs(ratio - R) < 0.15 * R:
                start_win = max(0, i - 5)
                end_win = min(len(df), i + 6)
                has_official_split = False
                if 'Stock Splits' in df.columns:
                    window_splits = df.iloc[start_win:end_win]['Stock Splits']
                    if ((window_splits.notna()) & (window_splits > 0) & (window_splits != 1.0)).any():
                        has_official_split = True
                
                if not has_official_split:
                    drop_date = df.index[i]
                    print(f"🔄 [yf_proxy] Auto-detected unrecorded forward split of {R}:1 on {drop_date.date()} (Price went from {p_prev:.2f} to {p_curr:.2f}). Adjusting history...")
                    for metric in ['Open', 'High', 'Low', 'Close']:
                        if metric in df.columns:
                            df.iloc[:i, df.columns.get_loc(metric)] /= R
                    break
                    
        # Check reverse split
        rev_ratio = p_curr / p_prev
        for R in factors:
            if abs(rev_ratio - R) < 0.15 * R:
                start_win = max(0, i - 5)
                end_win = min(len(df), i + 6)
                has_official_split = False
                if 'Stock Splits' in df.columns:
                    window_splits = df.iloc[start_win:end_win]['Stock Splits']
                    if ((window_splits.notna()) & (window_splits > 0) & (window_splits != 1.0)).any():
                        has_official_split = True
                        
                if not has_official_split:
                    jump_date = df.index[i]
                    print(f"🔄 [yf_proxy] Auto-detected unrecorded reverse split of 1:{R} on {jump_date.date()} (Price went from {p_prev:.2f} to {p_curr:.2f}). Adjusting history...")
                    for metric in ['Open', 'High', 'Low', 'Close']:
                        if metric in df.columns:
                            df.iloc[:i, df.columns.get_loc(metric)] *= R
                    break
    return df

def auto_detect_splits_multi(df):
    if df.empty:
        return df
    df = df.copy()
    if isinstance(df.index, pd.DatetimeIndex):
        df = df.sort_index()
        
    if not isinstance(df.columns, pd.MultiIndex):
        return auto_detect_splits_single(df)
        
    if 'Close' in df.columns.levels[0]:
        ticker_level = 1
        metric_level = 0
    elif 'Close' in df.columns.levels[1]:
        ticker_level = 0
        metric_level = 1
    else:
        return df
        
    tickers = df.columns.levels[ticker_level]
    factors = [2, 3, 4, 5, 6, 7, 8, 10, 20, 50, 100]
    
    for ticker in tickers:
        close_col = ('Close', ticker) if metric_level == 0 else (ticker, 'Close')
        splits_col = ('Stock Splits', ticker) if metric_level == 0 else (ticker, 'Stock Splits')
        
        if close_col not in df.columns:
            continue
            
        for i in range(1, len(df)):
            p_prev = df.iloc[i-1][close_col]
            p_curr = df.iloc[i][close_col]
            
            if pd.isna(p_prev) or pd.isna(p_curr) or p_prev <= 0 or p_curr <= 0:
                continue
                
            ratio = p_prev / p_curr
            
            # Check forward split
            for R in factors:
                if abs(ratio - R) < 0.15 * R:
                    start_win = max(0, i - 5)
                    end_win = min(len(df), i + 6)
                    has_official_split = False
                    if splits_col in df.columns:
                        window_splits = df.iloc[start_win:end_win][splits_col]
                        if ((window_splits.notna()) & (window_splits > 0) & (window_splits != 1.0)).any():
                            has_official_split = True
                            
                    if not has_official_split:
                        drop_date = df.index[i]
                        print(f"🔄 [yf_proxy] Auto-detected unrecorded forward split of {R}:1 for {ticker} on {drop_date.date()} (Price went from {p_prev:.2f} to {p_curr:.2f}). Adjusting history...")
                        for metric in ['Open', 'High', 'Low', 'Close']:
                            metric_col = (metric, ticker) if metric_level == 0 else (ticker, metric)
                            if metric_col in df.columns:
                                df.iloc[:i, df.columns.get_loc(metric_col)] /= R
                        break
                        
            # Check reverse split
            rev_ratio = p_curr / p_prev
            for R in factors:
                if abs(rev_ratio - R) < 0.15 * R:
                    start_win = max(0, i - 5)
                    end_win = min(len(df), i + 6)
                    has_official_split = False
                    if splits_col in df.columns:
                        window_splits = df.iloc[start_win:end_win][splits_col]
                        if ((window_splits.notna()) & (window_splits > 0) & (window_splits != 1.0)).any():
                            has_official_split = True
                            
                    if not has_official_split:
                        jump_date = df.index[i]
                        print(f"🔄 [yf_proxy] Auto-detected unrecorded reverse split of 1:{R} for {ticker} on {jump_date.date()} (Price went from {p_prev:.2f} to {p_curr:.2f}). Adjusting history...")
                        for metric in ['Open', 'High', 'Low', 'Close']:
                            metric_col = (metric, ticker) if metric_level == 0 else (ticker, metric)
                            if metric_col in df.columns:
                                df.iloc[:i, df.columns.get_loc(metric_col)] *= R
                        break
    return df

def adjust_single_splits(df):
    if df.empty:
        return df
        
    df = df.copy()
    if isinstance(df.index, pd.DatetimeIndex):
        df = df.sort_index()
        
    # Process official splits if 'Stock Splits' exists
    if 'Stock Splits' in df.columns:
        split_rows = df[df['Stock Splits'].notna() & (df['Stock Splits'] > 0) & (df['Stock Splits'] != 1.0)]
        for date in sorted(split_rows.index, reverse=True):
            R = split_rows.loc[date, 'Stock Splits']
            try:
                target_idx = df.index.get_loc(date)
            except KeyError:
                continue
                
            found_drop = False
            for i in range(5):
                idx = target_idx - i
                if idx <= 0:
                    break
                
                p_curr = df.iloc[idx]['Close']
                p_prev = df.iloc[idx-1]['Close']
                if pd.isna(p_curr) or pd.isna(p_prev) or p_prev == 0:
                    continue
                ratio = p_curr / p_prev
                expected_ratio = 1.0 / R
                
                if abs(ratio - expected_ratio) < 0.15:
                    drop_date = df.index[idx]
                    for metric in ['Open', 'High', 'Low', 'Close']:
                        if metric in df.columns:
                            df.loc[df.index < drop_date, metric] /= R
                    found_drop = True
                    break
                    
    # Apply automatic split detection fallback
    df = auto_detect_splits_single(df)
    return df

def adjust_multi_splits(df):
    if df.empty:
        return df
        
    df = df.copy()
    if isinstance(df.index, pd.DatetimeIndex):
        df = df.sort_index()
        
    if not isinstance(df.columns, pd.MultiIndex):
        return adjust_single_splits(df)
        
    if 'Close' in df.columns.levels[0]:
        ticker_level = 1
        metric_level = 0
    elif 'Close' in df.columns.levels[1]:
        ticker_level = 0
        metric_level = 1
    else:
        return df
        
    tickers = df.columns.levels[ticker_level]
    for ticker in tickers:
        stock_splits_col = ('Stock Splits', ticker) if metric_level == 0 else (ticker, 'Stock Splits')
        close_col = ('Close', ticker) if metric_level == 0 else (ticker, 'Close')
        
        if stock_splits_col not in df.columns or close_col not in df.columns:
            continue
            
        splits = df[stock_splits_col]
        split_rows = df[splits.notna() & (splits > 0) & (splits != 1.0)]
        
        for date in sorted(split_rows.index, reverse=True):
            R = df.loc[date, stock_splits_col]
            try:
                target_idx = df.index.get_loc(date)
            except KeyError:
                continue
                
            found_drop = False
            for i in range(5):
                idx = target_idx - i
                if idx <= 0:
                    break
                p_curr = df.iloc[idx][close_col]
                p_prev = df.iloc[idx-1][close_col]
                if pd.isna(p_curr) or pd.isna(p_prev) or p_prev == 0:
                    continue
                ratio = p_curr / p_prev
                expected_ratio = 1.0 / R
                if abs(ratio - expected_ratio) < 0.15:
                    drop_date = df.index[idx]
                    for metric in ['Open', 'High', 'Low', 'Close']:
                        metric_col = (metric, ticker) if metric_level == 0 else (ticker, metric)
                        if metric_col in df.columns:
                            df.loc[df.index < drop_date, metric_col] /= R
                    found_drop = True
                    break
                    
    # Apply automatic split detection fallback
    df = auto_detect_splits_multi(df)
    return df

_limiter = RateLimiter(max_requests=default_max_requests, period=60.0)

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

    req_count = _limiter.wait_if_needed()
    print(f"📡 Fetching live data for {ticker_sym} (Live requests in last 60s: {req_count}/{_limiter.max_requests})...")
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
        
    except Exception as e:
        err_msg = str(e)
        print(f"⚠️ Error fetching {ticker_sym}: {err_msg}")
        if "too many requests" in err_msg.lower() or "rate limited" in err_msg.lower():
            _limiter.report_rate_limit()
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
            
        self.history_5y = adjust_single_splits(restore_df("history_5y"))

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
    
    # We must enforce actions=True to get Stock Splits information
    kwargs_copy = kwargs.copy()
    kwargs_copy['actions'] = True
    
    # Create a unique key for this request using kwargs_copy to ensure consistent cache keys
    key_str = f"{sorted(tickers)}_{kwargs_copy.get('period')}_{kwargs_copy.get('interval')}_{kwargs_copy.get('actions')}"
    key_hash = hashlib.md5(key_str.encode()).hexdigest()
    
    cache_dir = get_cache_dir()
    cache_path = os.path.join(cache_dir, f"batch_{key_hash}.pkl")
    
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    
    if os.path.exists(cache_path):
        try:
            print(f"📦 Loading cached batch data ({len(tickers)} tickers)...")
            df = pd.read_pickle(cache_path)
            return adjust_multi_splits(df), True
        except Exception:
            pass
            
    req_count = _limiter.wait_if_needed()
    print(f"📡 Downloading live batch data for {len(tickers)} tickers (Live requests in last 60s: {req_count}/{_limiter.max_requests})...")
    try:
        df = yf.download(tickers, **kwargs_copy)
    except Exception as e:
        err_msg = str(e)
        if "too many requests" in err_msg.lower() or "rate limited" in err_msg.lower():
            _limiter.report_rate_limit()
        raise e
    
    if not df.empty:
        download_successful = True
        if len(tickers) > 1:
            cols = df.columns
            present_tickers = []
            if isinstance(cols, pd.MultiIndex):
                for lvl in range(min(2, len(cols.levels))):
                    l_vals = [str(x) for x in cols.levels[lvl]]
                    if any(t in l_vals for t in tickers):
                        present_tickers = [t for t in tickers if t in l_vals]
                        break
            else:
                present_tickers = [t for t in tickers if t in cols]
            
            missing_tickers = [t for t in tickers if t not in present_tickers]
            if missing_tickers:
                print(f"⚠️ yf.download failed to download data for {len(missing_tickers)} tickers: {missing_tickers}. Not caching this batch to allow re-fetching.")
                download_successful = False

        if download_successful:
            try:
                df.to_pickle(cache_path)
            except Exception as e:
                print(f"⚠️ Failed to cache batch: {e}")
            
    return adjust_multi_splits(df), False

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
