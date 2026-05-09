import requests_cache
from datetime import timedelta
import os

def get_session():
    """
    Returns a requests-cache session for yfinance.
    Caches results for 24 hours to avoid repeated network calls during development.
    """
    # Create a cache directory if it doesn't exist
    cache_dir = "scratch/cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    cache_path = os.path.join(cache_dir, "yfinance_cache")
    
    # Cache for 1 day (24 hours)
    session = requests_cache.CachedSession(
        cache_path,
        expire_after=timedelta(days=1),
        backend='sqlite',
        allowable_methods=['GET', 'POST']
    )
    
    # Headers to look like a browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    return session
