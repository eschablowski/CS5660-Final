from transformers import PegasusForConditionalGeneration, PegasusTokenizer, PegasusXForConditionalGeneration

import torch
import tqdm
import sqlite3

with sqlite3.Connection('cleaned.db') as conn:

    model_name = "pszemraj/pegasus-x-large-book-summary"

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(device)

    tokenizer = PegasusTokenizer.from_pretrained(model_name)

    model = PegasusXForConditionalGeneration.from_pretrained(model_name).to(device)

    try:
        conn.execute('ALTER TABLE cleaned_books ADD COLUMN summary TEXT default null')
    except:
        pass # column probably exists already

    count, = conn.execute('SELECT COUNT(id) FROM cleaned_books WHERE summary IS NULL;').fetchone()
    cursor = conn.execute('SELECT id, text FROM cleaned_books WHERE summary IS NULL;')
    for id, book in tqdm.tqdm(cursor, total=count):
        batch = tokenizer(book.decode("utf-8"), truncation=True, padding="longest", return_tensors="pt").to(device)
        translated = model.generate(**batch)

        tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
        conn.execute('''
                UPDATE cleaned_books
                SET summary = ?
                WHERE id = ?;
                     ''', (tgt_text[0], id))
        
        conn.commit()