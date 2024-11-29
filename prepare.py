import os
import tqdm
from gutenbergpy import textget as gutenberg
from multiprocessing import Pool
import sqlite3


folder = "./txt-files/cache/epub/"
files = os.listdir(folder)

conn = sqlite3.Connection('cleaned.db')

conn.execute('''CREATE TABLE IF NOT EXISTS cleaned_books (
                    id INTEGER PRIMARY KEY,
                    text TEXT
                )''')
conn.execute('DELETE FROM cleaned_books WHERE 1=1;')
cursor = conn.cursor()

def process(file):
    with open(f'{folder}{file}/pg{file}.txt') as f:
        raw_book = bytes(f.read(), 'utf-8')
        clean_book = gutenberg.strip_headers(raw_book).strip() # without headers

        return (int(file), clean_book)

with Pool() as p:
    cursor.executemany('INSERT INTO cleaned_books (id, text) VALUES (?, ?);', tqdm.tqdm(p.imap_unordered(process, files), total=len(files)))
    conn.commit()
    cursor.close()
