import sqlite3

db = 'raise.db'

sql_create_stats_table  = """ CREATE TABLE IF NOT EXISTS stats (
      id integer PRIMARY KEY,
      sku text NOT NULL,
      denomination integer NOT NULL,
      count integer,
      min real,
      mean real,
      std real,
      percent_25 real,
      percent_50 real,
      percent_75 real,
      update_time integer);"""

conn = sqlite3.connect(db)
if conn:
     c = conn.cursor()
     c.execute(sql_create_stats_table)

 
