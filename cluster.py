import sqlite3
import pickle
import tqdm
import itertools
import numpy as np
from sklearn.cluster import MiniBatchKMeans
conn = sqlite3.connect('cleaned.db')

# From https://stackoverflow.com/questions/8290397/how-to-split-an-iterable-in-constant-size-chunks
def batch(iterable, n):
    "Batch data into lists of length n. The last batch may be shorter."
    # batched('ABCDEFG', 3) --> ABC DEF G
    it = iter(iterable)
    while True:
        batch = list(itertools.islice(it, n))
        if not batch:
            return
        yield batch

count, = conn.execute('''SELECT COUNT(id) from clusterable;''').fetchone()
kmeans = MiniBatchKMeans(n_clusters=200,
                         random_state=0,
                         batch_size=2000,
                         n_init="auto")

for data in batch(tqdm.tqdm(conn.execute("SELECT unitized from clusterable;"), total=count), 2000):
    embeddings = [pickle.loads(datum) for datum, in data]
    if len(embeddings) > 0:
        kmeans = kmeans.partial_fit(embeddings)

print(kmeans.__repr__())

conn.execute('''
             CREATE TABLE IF NOT EXISTS clusters (
                id INTEGER PRIMARY KEY,
                center BLOB
             )
             ''')
conn.execute("DELETE FROM clusters WHERE 1=1;")
conn.executemany("INSERT INTO clusters (id, center) VALUES (?, ?);", enumerate([pickle.dumps(center) for center in kmeans.cluster_centers_]))

try:
    conn.execute('ALTER TABLE cleaned_books ADD COLUMN cluster INTEGER default null;')
except:
    pass # column probably exists already
for id, unitized in tqdm.tqdm(conn.execute("SELECT id, unitized from clusterable;"), total=count):
    cluster = kmeans.predict([pickle.loads(unitized)])[0]

    conn.execute("UPDATE cleaned_books SET cluster = ? WHERE id = ?", (int(cluster), id))
conn.commit()
conn.close()