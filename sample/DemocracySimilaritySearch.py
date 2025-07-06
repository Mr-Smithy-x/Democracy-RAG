import numpy
import numpy as np
import psycopg2
import torch
import mysql.connector
from mysql.connector import Error
from psycopg2.extensions import register_adapter, AsIs
from transformers import AutoTokenizer, AutoModel
from dotenv import load_dotenv
import os
import requests


def download_file(url, filename):
    # Send a GET request to the URL
    response = requests.get(url, stream=True)

    # Check if the request was successful
    response.raise_for_status()

    # Write the content to a file
    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

    print(f"File downloaded successfully to {filename}")



load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

PG_DB_USER = os.getenv('PG_DB_USER')
PG_DB_PASS = os.getenv('PG_DB_PASS')
PG_DB_HOST = os.getenv('PG_DB_HOST')
PG_DB_PORT = os.getenv('PG_DB_PORT')
PG_DB_NAME = os.getenv('PG_DB_NAME')


model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)


# Register adapter for numpy array to ensure proper conversion
def addapt_numpy_array(numpy_array):
    return AsIs(list(numpy_array))


register_adapter(numpy.ndarray, addapt_numpy_array)


def connect_mysql_db():
    """Connect to Mysql database"""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )


def connect_postgres_db():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(
        dbname=PG_DB_NAME,
        host=PG_DB_HOST,
        port=PG_DB_PORT,
        password=PG_DB_PASS,
        user=PG_DB_USER
    )

def setup_database():
    """Create the necessary tables and extensions"""
    conn = connect_postgres_db()
    cur = conn.cursor()

    try:
        # Enable vector extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")

        # Create table with vector column
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS bills
            (
                id
                bigserial
                primary
                key,
                bill
                varchar
            (
                255
            ),
                text_content text,
                embedding vector
            (
                384
            ),
                constraint docs_pk unique
            (
                text_content,
                bill
            )
                );
            """
        )

        conn.commit()
        print("Database setup completed successfully")

    except Exception as e:
        print(f"Error setting up database: {e}")
        conn.rollback()

    finally:
        cur.close()
        conn.close()

def insert_vector(file, text: str, vector: np.ndarray):
    """Insert text and its vector embedding"""
    conn = connect_postgres_db()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO bills (bill, embedding, text_content) VALUES (%s, %s, %s)",
            (file, np.array(vector[0]).tolist(), text)
        )
        conn.commit()
        print("Vector inserted successfully")

    except Exception as e:
        print(f"Error inserting vector: {e}")
        conn.rollback()

    finally:
        cur.close()
        conn.close()

def find_similar(query_vector: np.ndarray, limit: int = 5):
    """Find similar vectors using cosine similarity"""
    conn = connect_postgres_db()
    cur = conn.cursor()

    try:
        cur.execute("""
                    SELECT package_id,
                           id_reference,
                           title,
                           text,
                           description,
                           details_txt,
                           1 - (title_vector <=> %s::vector)   as title_similarity,
                           1 - (details_vector <=> %s::vector) as details_similarity
                    FROM interactive
                    ORDER BY details_similarity DESC
                    LIMIT %s
                    """, (np.array(query_vector[0]).tolist(), np.array(query_vector[0]).tolist(), limit))

        results = cur.fetchall()
        return results

    finally:
        cur.close()
        conn.close()

def get_all():
    """Find similar vectors using cosine similarity"""
    conn = connect_postgres_db()
    cur = conn.cursor()

    try:
        cur.execute(
            """
                SELECT * FROM interactive WHERE (title_vector IS NULL OR details_vector IS NULL) AND details_txt IS NOT NULL
            """
        )

        results = cur.fetchall()
        return results

    finally:
        cur.close()
        conn.close()


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

def chunk_text_by_words(filename, chunk_size=127):
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

def does_bill_exist(bill):
    conn = connect_postgres_db()
    cur = conn.cursor()

    try:
        # This is the correct syntax to check if a record exists
        cur.execute("SELECT EXISTS(SELECT 1 FROM bills WHERE bill = %s)", (bill,))
        # fetchone() returns a tuple with one element
        result = cur.fetchone()[0]
        return result  # This will be True if the bill exists, False otherwise
    except Exception as e:
        print(f"Error checking if bill exists: {e}")
        return False
    finally:
        cur.close()
        conn.close()



def insert_all_file_chunks_from_path(path='bills/'):
    files = os.listdir(path)
    for file in files:
        file_path = path + file
        chunks = chunk_text_by_words(file_path)
        bill = file.replace('.htm', '')
        if does_bill_exist(bill):
            print(f"Skipping {file} - bill already exists")
            continue
        print(f"Inserting {file} chunks - 127, 255, 384\n")
        for chunk in chunks:
            encoded = get_embedding(chunk)
            insert_vector(bill, chunk, encoded)
        chunks = chunk_text_by_words(file_path, 255)
        for chunk in chunks:
            encoded = get_embedding(chunk)
            insert_vector(bill, chunk, encoded)
        chunks = chunk_text_by_words(file_path, 384)
        for chunk in chunks:
            encoded = get_embedding(chunk)
            insert_vector(bill, chunk, encoded)
    # Example: Store some vectors

def get_bills():
    conn = connect_mysql_db()
    curr = conn.cursor()

    try:
        curr.execute("SELECT package_id, title, date_issued, last_modified, bill_type, bill_version, bill_number, `references` FROM packages WHERE collection_code='BILLS' AND congress=119 ORDER BY date_issued DESC;")
        results = curr.fetchall()
        return results
    finally:
        curr.close()
        conn.close()

def get_package_infos():
    conn = connect_mysql_db()
    curr = conn.cursor()

    try:
        curr.execute("SELECT package_id, title FROM package_infos WHERE package_id LIKE 'BILLS-119%' ORDER BY date_issued DESC;")
        results = curr.fetchall()
        return results
    finally:
        curr.close()
        conn.close()


def downloads():
    bills = get_bills()
    for bill in bills:
        (package_id, title, date_issued, last_modified, bill_type, bill_version, bill_number, references) = bill
        # Example usage
        file_name = f"htm/{package_id}.htm"
        if os.path.exists(file_name):
            print(f"File {file_name} already exists, skipping download.")
            continue
        print(
            f"Downloading bill {package_id} - {title} - {date_issued} - {last_modified} - {bill_type} - {bill_version} - {bill_number} - {references}"
        )
        url = f"https://www.govinfo.gov/content/pkg/{package_id}/html/{package_id}.htm"
        download_file(url, file_name)

def update_title_embeddings():
    bills = get_package_infos()

    conn = connect_postgres_db()
    cur = conn.cursor()

    for package_id, title in bills:
        if title is None:
            continue
        try:
            vector = get_embedding(title)
            cur.execute("UPDATE bills SET title = %s, title_embedding = %s WHERE bill = %s",
                        (title, np.array(vector[0]).tolist(), package_id))
            conn.commit()
            print("Title embeddings updated successfully")
        except Exception as e:
            print(f"Error updated vector: {e}")
            conn.rollback()
    cur.close()
    conn.close()

def update():
    results = get_all()

    conn = connect_postgres_db()
    cur = conn.cursor()
    for result in results:
        (package_id, id_reference, title, text, description, details, title_vector, details_vector, details_txt) = result

        title_vector = get_embedding(title)
        details_vector = get_embedding(details_txt)
        print(f"DOING SOMETHING: {package_id} - {id_reference} - {title}")

        try:
            cur.execute("UPDATE interactive SET title_vector = %s, details_vector = %s WHERE package_id = %s AND id_reference = %s",
                    (np.array(title_vector[0]).tolist(), np.array(details_vector[0]).tolist(), package_id, id_reference))
            conn.commit()
        except Exception as e:
            print(f"Error updating vector: {e}")
            conn.rollback()
        finally:
            print("Vector updated successfully")
    cur.close()
    conn.close()


# Example usage
if __name__ == "__main__":
    # Setup database first time
    #setup_database()
    #insert_all_file_chunks_from_path()




    def search(text: str):
        # Find similar vectors
        query = get_embedding(text)  # Your query vector
        print(query.tolist())
        similar_results = find_similar(query, limit=5)

        print(f"\nSimilar items via query: {text}, {len(similar_results)}")
        for (package_id, id_reference, title, text, description, details, title_perc, details_perc) in similar_results:
            print(f"Bill: {package_id} - {id_reference}: {title}...")
            print(f"Text: {details}...")
            print(f"Title Similarity: {title_perc:.4f}")
            print(f"Details Similarity: {details_perc:.4f}")
            print("-" * 50)


    try:
        #search("illegal immigrants")
        # downloads()

        #update_title_embeddings()
        #insert_all_file_chunks_from_path('htm/')

        update()
    except Exception as e:
        print(f"Error inserting chunks: {e}")
    finally:
        print("Doone")
