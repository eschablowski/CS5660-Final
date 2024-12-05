import sqlite3
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import tqdm
import pickle
import pandas as pd
from datetime import datetime
from transformers import AutoTokenizer, AutoModel
from multiprocessing import freeze_support


if __name__ == '__main__':
    freeze_support()

    dateparse = lambda x: datetime.strptime(x, '%Y-%m-%d')
    df = pd.read_csv('pg_catalog.csv', parse_dates=['Issued'], date_parser=dateparse)
    def progress(status, remaining, total):
        print(f'Copied {total-remaining} of {total} pages...')
    # conn.backup(cache, pages=100, progress=progress)

    embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-m3",
        # parallel_process=True
    )

    conn = sqlite3.Connection('cleaned.db')
    conn.execute('''
                CREATE TABLE IF NOT EXISTS llama_embeddings (
                    id INTEGER PRIMARY KEY,
                    text BLOB,
                    summary BLOB,
                    title BLOB,
                    authors BLOB,
                    subjects BLOB,
                    bookshelves BLOB
                );
                ''')
    #     # cache.execute('DELETE FROM llama_embeddings WHERE 1=1;')

    count, = conn.execute('''
                            SELECT COUNT(CB.id)
                            FROM cleaned_books as CB
                            LEFT JOIN llama_embeddings as LE
                                ON CB.id == LE.id
                            WHERE
                                CB.summary IS NOT NULL
                            AND CB.text IS NOT NULL
                            AND LE.summary IS NULL;
                        ''').fetchone()
    cursor = conn.execute('''
                            SELECT CB.id, CB.text, CB.summary
                            FROM cleaned_books as CB
                            LEFT JOIN llama_embeddings as LE
                                ON CB.id == LE.id
                            WHERE
                                CB.summary IS NOT NULL
                            AND CB.text IS NOT NULL
                            AND LE.summary IS NULL;
                        ''')
    #     cursor.executemany('INSERT INTO llama_embeddings (id, text, summary, title, subjects, bookshelves, authors) VALUES (?, ?, ?, ?, ?, ?, ?);', tqdm.tqdm(p.imap(process, cursor), total=count))
    #     cache.commit()
    for id, text, summary in tqdm.tqdm(cursor, total=count):
        summary = embed_model.get_text_embedding(
            summary
        )
        # text = embed_model.get_text_embedding(
        #     text.decode('utf-8')
        # )

        row = df[df['Text#'] == id].to_dict(orient='records')[0]

        title = embed_model.get_text_embedding(
            str(row['Title'])
        )
        subjects = [embed_model.get_text_embedding(
            subject
        ) for subject in str(row['Subjects']).split(';')]
        bookshelves = [embed_model.get_text_embedding(
            bookshelf
        ) for bookshelf in str(row['Bookshelves']).split(';')]
        authors = [embed_model.get_text_embedding(
            author
        ) for author in str(row['Authors']).split(';')]
        conn.execute('INSERT INTO llama_embeddings (id, text, summary, title, subjects, bookshelves, authors) VALUES (?, ?, ?, ?, ?, ?, ?);', (id, pickle.dumps(text), pickle.dumps(summary), pickle.dumps(title), pickle.dumps(subjects), pickle.dumps(bookshelves), pickle.dumps(authors)))

    conn.commit()