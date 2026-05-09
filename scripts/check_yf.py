import yfinance as yf
import sys

def check_connectivity():
    print("🌐 Checking Yahoo Finance connectivity...")
    try:
        # Try to fetch a single, reliable ticker
        ticker = yf.Ticker("AAPL")
        info = ticker.fast_info
        if info and 'lastPrice' in info and info['lastPrice'] > 0:
            print("✅ Connectivity OK. (AAPL price: ${:.2f})".format(info['lastPrice']))
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
