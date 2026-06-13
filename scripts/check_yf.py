import yfinance as yf
import sys
import os

def check_connectivity():
    if os.environ.get('YF_DEBUG') == '1':
        print("🌐 Offline debug mode active (YF_DEBUG=1). Bypassing real-time connectivity check.")
        return True
    print("🌐 Checking Yahoo Finance connectivity (REAL-TIME)...")
    try:
        # We bypass the proxy here to verify actual network status
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        
        if info and ('currentPrice' in info or 'regularMarketPrice' in info):
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            print("✅ Connectivity OK. (AAPL price: ${:.2f})".format(price))
            return True
        else:
            print("❌ Connectivity failed: Could not retrieve price data.")
            return False
    except Exception as e:
        print(f"❌ Connectivity failed: {str(e)}")
        return False

if __name__ == "__main__":
    if check_connectivity():
        sys.exit(0)
    else:
        print("\n⚠️ ERROR: Yahoo Finance is blocking your IP or is currently unreachable.")
        print("Stopping task to prevent further rate-limiting.")
        sys.exit(1)
