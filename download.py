import requests
import pandas as pd
import tqdm
import os
from multiprocessing import Pool
import random

df = pd.read_csv("./pg_catalog.csv")

if not os.path.exists("./data"):
    os.mkdir("./data")

ids = filter(lambda id: not os.path.exists(f'./data/{id}.txt'), df['Text#'])
ids = list(ids)

mirrors = [
    'http://mirror.csclub.uwaterloo.ca/gutenberg/',
    'https://gutenberg.nabasny.com/',
    'https://www.gutenberg.org/',
    'https://aleph.gutenberg.org/',
    'https://gutenberg.pglaf.org/'
]

def download(id):
    mirror = random.choice(mirrors)
    try:
        res = requests.get(f"{mirror}/cache/epub/{id}/pg{id}.txt")
        with open("./data/{}.txt".format(id), "w") as f:
            f.write(res.text)
    except:
        pass

with Pool() as p:
    r = list(tqdm.tqdm(p.imap(download, ids), total=len(ids)))

missing = list(filter(lambda id: not os.path.exists(f'./data/{id}.txt'), df['Text#']))

print(f'Still missing: {len(missing)}')
print(missing)
# for id in tqdm.tqdm(df["Text#"]):
#     if(os.path.exists("./data/{}.txt".format(id))):
#         continue
#     res = requests.get("https://www.gutenberg.org/cache/epub/{}/pg{}.txt".format(id, id))
#     with open("./data/{}.txt".format(id), "w") as f:
#         f.write(res.text)