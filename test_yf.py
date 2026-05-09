import yfinance as yf
import pandas as pd
import time

tickers = ["7203.T", "6758.T", "6501.T", "9984.T"]
data_frames = []
chunk_size = 2
for i in range(0, len(tickers), chunk_size):
    chunk = tickers[i:i+chunk_size]
    print(f"Fetching chunk {i//chunk_size + 1}...")
    df_chunk = yf.download(chunk, period="1mo", interval="1d", group_by='ticker', progress=False, threads=True)
    if not df_chunk.empty:
        data_frames.append(df_chunk)
    time.sleep(1)

data = pd.concat(data_frames, axis=1)
print(data.columns.levels[0])
print(data.head(2))
