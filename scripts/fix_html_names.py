import pandas as pd
from bs4 import BeautifulSoup

csv_file = '/home/tonyho/workspace/invest/report/dma_200_screen_results_tw.csv'
html_file = '/home/tonyho/workspace/invest/report/dma_200_screen_results_tw.html'

df = pd.read_csv(csv_file)
name_map = dict(zip(df['Ticker'], df['Name']))

with open(html_file, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

for tr in soup.find_all('tr'):
    badge = tr.find('span', class_='ticker-badge')
    if badge:
        ticker = badge.text.strip()
        if ticker in name_map:
            # The next td contains the name
            name_td = tr.find_all('td')[1]
            name_td.string = name_map[ticker]

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(soup.prettify())
print("Updated HTML with Chinese names!")
