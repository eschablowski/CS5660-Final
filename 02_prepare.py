from transformers import pipeline
import db
import sqlalchemy
import tqdm
import pandas as pd
import functools
import math
import sklearn.cluster

def download_books(output_dir: str = "books"):
    import urllib.request
    import shutil
    import os.path

    tqdm.tqdm.write("Downloading books")
    def update(blocknum, blocksize, totalsize):
        progressbar.total = totalsize
        if blocknum == 0:
            progressbar.update(blocksize)
        else:
            progressbar.update(progressbar.n + blocksize)

    url = "http://aleph.gutenberg.org/cache/generated/feeds/txt-files.tar.zip"
    progressbar = tqdm.tqdm(total=0, unit="B", unit_scale=True)
    urllib.request.urlretrieve(url, "books.tar.zip", reporthook=update)
    shutil.unpack_archive("books.tar.zip", output_dir, format="zip")
    shutil.unpack_archive("books.tar", output_dir, format="tar")

    url = "http://aleph.gutenberg.org/cache/generated/feeds/pg_catalog.csv"
    progressbar = tqdm.tqdm(total=0, unit="B", unit_scale=True)
    urllib.request.urlretrieve(url, os.path.join(output_dir, "books.csv"), reporthook=update)
    progressbar.close()

@functools.lru_cache(maxsize=1)
def load_metadata(metadata_file: str):
    return pd.read_csv(metadata_file)

def get_book(directory: str, book_id: int):
    import os.path
    if not os.path.exists(os.path.join(directory, f"{directory}/{book_id}.txt")):
        return None
    with open(os.path.join(directory, f"{directory}/{book_id}.txt")) as f:
        return f.read()

def summarize(data: db.Book):
    summarizer = pipeline("summarization", model="pszemraj/pegasus-x-large-book-summary", trust_remote_code=True)
    return summarizer(data, max_length=130, min_length=30, do_sample=False)


def create_embeddings(data: str, model: str = "nvidia/NV-Embed-v2"):
    from transformers import AutoModel

    model = AutoModel.from_pretrained(model, trust_remote_code=True)

    # get the embeddings
    max_length = 32768
    return model.encode([data], instruction="", max_length=max_length)

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--batchsize", type=int, default=10)
    parser.add_argument("--embedding_model", type=str, default="nvidia/NV-Embed-v2")
    parser.add_argument("--summary_model", type=str, default="pszemraj/pegasus-x-large-book-summary")
    parser.add_argument("--output_dir", type=str, default="books")
    parser.add_argument("--cluster_batchsize", type=int, default=2000)
    args = parser.parse_args()

    import os.path


    ## Download books
    if not os.path.exists("books"):
        download_books()
    
    engine = sqlalchemy.create_engine("sqlite:///books.db")
    db.Base.metadata.create_all(engine)
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()

    ## Load books into database
    if not session.query(db.Book).count():
        for book_id in load_metadata("books")["Text#"]:
            book_text = get_book("books", book_id)
            if book_text:
                book = db.Book(id=book_id, text=book_text)
                session.add(book)
    
    session.commit()

    for books in session.query(db.Book).yield_per(args.batchsize):
        for book in books:
            db.Summary(book=book, text=summarize(book.text, model=args.summary_model))
    
    session.commit()


    for books in session.query(db.Book).yield_per(args.batchsize):
        for book in books:
            db.Embedding(book=book,
                        summary=create_embeddings(book.text, model=args.embedding_model),
                        title=create_embeddings(book.title, model=args.embedding_model),
                        authors=[create_embeddings(a.name, model=args.embedding_model) for a in book.authors],
                        subjects=[create_embeddings(s.nam, model=args.embedding_modele) for s in book.subjects],
                        locc=[create_embeddings(l.name, model=args.embedding_model) for l in book.locc]
            )
    session.commit()
    
    kmeans = sklearn.cluster.MiniBatchKMeans(n_clusters=math.sqrt(session.query(db.Embedding).count()).astype(int))
    for embeddings in session.query(db.Embedding).yield_per(args.cluster_batchsize):
        for embedding in embeddings:
            kmeans.partial_fit(embedding)
    for id, cluster in kmeans.cluster_centers_:
        db.Cluster(id=id, centroid=cluster)
    session.commit()

    for books in session.query(db.Book).yield_per(args.batchsize):
        for book in books:
            book.cluster = kmeans.predict(book.embedding)