import pandas as pd
from screener import get_tw_tickers

tw_names = get_tw_tickers()
df = pd.read_csv('/home/tonyho/workspace/invest/report/dma_200_screen_results_tw.csv')
for i, row in df.iterrows():
    ticker = row['Ticker']
    if ticker in tw_names:
        # Don't duplicate if it's already there
        if f"({tw_names[ticker]})" not in row['Name']:
            df.at[i, 'Name'] = f"{row['Name']} ({tw_names[ticker]})"
df.to_csv('/home/tonyho/workspace/invest/report/dma_200_screen_results_tw.csv', index=False)
print("Updated CSV with Chinese names!")
