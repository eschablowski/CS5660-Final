import sqlite3
import pickle
import numpy as np
from sklearn.preprocessing import LabelEncoder
import tqdm

le = LabelEncoder()
conn = sqlite3.connect('cleaned.db')

cursor = conn.execute('SELECT E.id, E.summary, E.title, E.authors, E.subjects, E.bookshelves, M.issued, M.language from llama_embeddings as E INNER JOIN metadata M on E.id == m.id;')

conn.execute('''
             CREATE TABLE IF NOT EXISTS clusterable (
                id INTEGER PRIMARY KEY,
                data BLOB,
                unitized BLOB
             );
             ''')

count, = conn.execute('''SELECT COUNT(E.id) from llama_embeddings as E INNER JOIN metadata M on E.id == m.id;''').fetchone()

languages = conn.execute('SELECT DISTINCT language from metadata;').fetchall()
le.fit(languages)

def combine(arrays):
    arrays = [np.array(X) for X in arrays]
    result = arrays[0]
    for arr in arrays[0:]:
        result *= arr
    return result

for id, summary, title, authors, subjects, bookshelves, issued, language in tqdm.tqdm(cursor, total=count):
    summary = pickle.loads(summary)
    title = pickle.loads(title)
    authors = pickle.loads(authors)
    subjects = pickle.loads(subjects)
    bookshelves = pickle.loads(bookshelves)

    language = le.transform([language])[0]

    authors = combine(authors)
    subjects = combine(subjects)
    bookshelves = combine(bookshelves)

    data = np.concatenate((summary, title, authors, subjects, bookshelves, [language]))
    length = np.sqrt((data ** 2).sum())
    conn.execute('INSERT OR REPLACE INTO clusterable (id, data, unitized) VALUES (?, ?, ?);', (id, pickle.dumps(data), pickle.dumps(data / length)))

conn.commit()
