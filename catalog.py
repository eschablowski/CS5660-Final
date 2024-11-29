import pandas as pd
import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('cleaned.db')

dateparse = lambda x: datetime.strptime(x, '%Y-%m-%d')

df = pd.read_csv('pg_catalog.csv', parse_dates=['Issued'], date_parser=dateparse)


conn.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                id INTEGER PRIMARY KEY,
                issued INTEGER,
                title TEXT,
                language TEXT,
                authors TEXT,
                subjects TEXT,
                LoCC TEXT,
                bookshelves TEXT
            );
             ''')

epoch = pd.Timestamp("1970-01-01")

print([
                     row['Authors']
                     for index, row in df.head(20).iterrows()
                 ])

conn.executemany('INSERT INTO metadata (id, issued, title, language, authors, subjects, LoCC, bookshelves) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                 [
                     (row['Text#'], (row['Issued'] - epoch).seconds, row['Title'], row['Language'], json.dumps(str(row['Authors']).split(';')), json.dumps(str(row['Subjects']).split(';')), json.dumps(str(row['LoCC']).split(';')), json.dumps(str(row['Bookshelves']).split(';')))
                     for index, row in df.iterrows() if row['Type'] == 'Text'
                 ])
conn.commit()