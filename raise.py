
import sqlite3
import requests
import pandas as pd
import sys
import time


def summarize_change(before, cur, label):
    if before != cur:
        print(label, 'dropped' if before > cur else 'increased', 'from', before, 'to', cur)
        

price = int(sys.argv[1])

raise_url = "https://www.raise.com/a/merchant/listings/buy-the-home-depot-gift-cards/"
raise_tail = f"?discount_sort=desc&per=100&price_min={price-5}&price_max={price+5}"
db = "raise.db"
sku = "Home Depot"

data = []
for page in range(20):
    r = requests.get(f"{raise_url}{str(page)}{raise_tail}")

    listings = r.json()['listings']

    for listing in listings:
        row = {
         'price': float(listing['price'].replace('$', '')),
         'value': float(listing['value'].replace('$', ''))
        }

        data.append(row)

df = pd.DataFrame(data)

rows_of_price = df.loc[df.value == price]
row = rows_of_price['price']

print(rows_of_price['price'].describe())

conn = sqlite3.connect(db)
cursor = conn.cursor()

prev_stats = f'''SELECT sku, denomination, count, min, mean, percent_25, percent_50, percent_75 
                 FROM stats 
                 WHERE denomination={price} 
                    AND update_time=(
                        SELECT max(update_time) 
                        FROM stats 
                        WHERE denomination={price}
                    )'''

cursor.execute(prev_stats)
prev = cursor.fetchall()

if prev:
    summarize_change(int(prev[0][2]), int(row.count()), 'count')
    summarize_change(prev[0][3], row.min(), 'min')
    summarize_change(prev[0][4], row.mean(), 'mean')
    summarize_change(prev[0][5], row.quantile(.25), '25th %ile')
    summarize_change(prev[0][6], row.quantile(.5), '50th %ile')
    summarize_change(prev[0][7], row.quantile(.75), '75th %ile')

cursor.execute('''INSERT INTO stats (sku, denomination, count, min, mean, std, percent_25, percent_50, percent_75, update_time) 
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (sku, price, int(row.count()) , row.min(), row.mean(), row.std(), row.quantile(.25), row.quantile(.5),
                   row.quantile(.75), int(time.time())))
conn.commit()
