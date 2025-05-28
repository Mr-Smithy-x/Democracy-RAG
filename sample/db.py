import os
import psycopg2
import re
import os.path as path
from datetime import datetime
from urllib.parse import quote_plus
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch

model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Get database credentials from environment variables
DB_USER = os.getenv('DB_USER', 'smithy')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'smithy')
conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=None, host="localhost", port=5432)


def chunk_text_by_words(filename, chunk_size=384):
    # Read the file
    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read()

    # Split the text into words
    words = text.split()

    # Create chunks of specified size
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


def get_embedding(text: str) -> np.ndarray:
    """
    Convert text to embeddings using the transformer model.

    Args:
        text (str): Input text to convert to embedding

    Returns:
        np.ndarray: The embedding vector
    """
    # Tokenize the text and convert to tensor
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

    # Get model output
    with torch.no_grad():
        outputs = model(**inputs)

    # Use mean pooling to get a single vector representation
    attention_mask = inputs['attention_mask']
    token_embeddings = outputs.last_hidden_state

    # Calculate mean of token embeddings weighted by attention mask
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1),
                                                                                    min=1e-9)

    return embeddings.numpy()


def chunk_and_store_text(filename, db_path='chunks.db', chunk_size=384):
    """Read file, create chunks, and store them in SQLite database"""
    # Connect to SQLite database (creates if not exists)

    try:
        # Read and process the file
        chunks = chunk_text_by_words('../bills/BILLS-119hr1086ih.htm')

        # Insert chunks into database
        cursor = conn.cursor()
        for chunk in chunks:
            print((path.basename(filename), get_embedding(chunk)[0], chunk))
            cursor.execute("INSERT INTO documents.docs (bill, embedding, embedding_raw_text) VALUES (?, ?, ?)", (path.basename(filename), get_embedding(chunk)[0], chunk))

        # Commit the changes
        conn.commit()

        print(f"Successfully stored {len(chunks)} chunks in the database.")
        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        conn.rollback()
        return False

    finally:
        conn.close()


def retrieve_chunks(db_path='chunks.db', source_file=None):
    """Retrieve chunks from the database with optional filtering"""
    cursor = conn.cursor()

    try:
        if source_file:
            cursor.execute('''
                           SELECT id, bill, embedding, embedding_raw_text
                           FROM documents.docs
                           ORDER BY id
                           ''')
        else:
            cursor.execute('''
                           SELECT id, bill, embedding, embedding_raw_text
                           FROM documents.docs
                           ORDER BY id
                           ''')

        chunks = cursor.fetchall()
        return chunks

    finally:
        conn.close()


# Example usage
def main():
    # Store chunks from a file
    filename = "../bills/BILLS-119hr1086ih.htm"

    # Create database URL
    db_url = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    db_url_clean = f"postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    print(db_url_clean)
    db_path = db_url_clean #"text_chunks.db"

    try:
        # Store chunks
        success = chunk_and_store_text(filename, db_path)
        if success:
            # Retrieve and display chunks
            chunks = retrieve_chunks(db_path, filename)

            print("\nRetrieved chunks:")
            for chunk in chunks:
                chunk_id, text, word_count, source, timestamp = chunk
                print(f"\nChunk ID: {chunk_id}")
                print(f"Word count: {word_count}")
                print(f"Source: {source}")
                print(f"Created: {timestamp}")
                print(f"Preview: {text[:100]}...")
                print("-" * 50)

            print(f"\nTotal chunks retrieved: {len(chunks)}")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()