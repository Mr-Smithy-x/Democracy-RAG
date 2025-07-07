#%%
# Import necessary libraries
import json

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

from dotenv import load_dotenv
import os

load_dotenv()
# Import functions from your existing file
# Assuming your file is named vector_search.py - adjust as needed
# If importing doesn't work, you'll need to copy the relevant functions

PG_DB_USER = os.getenv('PG_DB_USER')
PG_DB_PASS = os.getenv('PG_DB_PASS')
PG_DB_HOST = os.getenv('PG_DB_HOST')
PG_DB_PORT = os.getenv('PG_DB_PORT')
PG_DB_NAME = os.getenv('PG_DB_NAME')


def connect_postgres_db():
    """Connect to PostgreSQL database"""
    import psycopg2
    return psycopg2.connect(
        dbname=PG_DB_NAME,
        host=PG_DB_HOST,
        port=PG_DB_PORT,
        password=PG_DB_PASS,
        user=PG_DB_USER
    )

def get_embedding2(text: str) -> np.ndarray:
    """
    Convert text to embeddings using the transformer model.

    Args:
        text (str): Input text to convert to embedding

    Returns:
        np.ndarray: The embedding vector
    """
    # You need to initialize these variables with your model
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)


    # Ensure model is on the correct device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)

    # Tokenize the text and convert to tensor
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)


    # Move inputs to the same device as model
    inputs = {k: v.to(device) for k, v in inputs.items()}

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

    return embeddings.cpu().numpy()


def get_embedding(text: str) -> np.ndarray:
    """
    Convert text to embeddings using the transformer model.

    Args:
        text (str): Input text to convert to embedding

    Returns:
        np.ndarray: The embedding vector
    """
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Load model on meta device first (this is what's causing your issue)
    model = AutoModel.from_pretrained(model_name, device_map="auto")

    # Check if model is on meta device and move it properly
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # If model parameters are on meta device, use to_empty()
    if next(model.parameters()).device.type == 'meta':
        model = model.to_empty(device=device)
        # Reload the weights from the pretrained model
        state_dict = AutoModel.from_pretrained(model_name).state_dict()
        model.load_state_dict(state_dict)
    else:
        # If not on meta device, use regular to()
        model = model.to(device)

    # Tokenize the text and convert to tensor
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

    # Move inputs to the same device as model
    inputs = {k: v.to(device) for k, v in inputs.items()}

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

    return embeddings.cpu().numpy()

def find_similar(package_id, query_vector: np.ndarray, limit: int = 5):
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
                            WHERE package_id = %s
                        ORDER BY details_similarity DESC
                        LIMIT %s
                        """, (np.array(query_vector[0]).tolist(), np.array(query_vector[0]).tolist(), package_id, limit))

            results = cur.fetchall()
            return results

        finally:
            cur.close()
            conn.close()

def api_search(package_id: str, query: str, limit: int = 5):
    try:
        # Get embedding for the query
        query_vector = get_embedding(query)

        # Find similar documents
        similar_results = find_similar(package_id, query_vector, limit=limit)

        # Format results
        results = []
        for (package_id, id_reference, title, text, description, details, title_perc, details_perc) in similar_results:
            results.append({
                'package_id': package_id,
                'id_reference': id_reference,
                'title': title,
                'text': text,
                'description': description,
                'details': details,
                'title_similarity': float(title_perc),
                'details_ similarity': float(details_perc)  # Convert to float for JSON serialization
            })
        return json.dumps({
            'query': query,
            'results': results
        })

    except Exception as e:
        return json.dumps({'error': str(e)})


import argparse
import sys


def main():
    # As good practice, it's better to get arguments from sys.argv[1:]
    # as the first argument is the script name.
    args = sys.argv[1:]

    parser = argparse.ArgumentParser(description="A script demonstrating named arguments.")

    # Add a named argument that expects a value
    # You can access it via args.output
    parser.add_argument(
        '-p', '--package',
        help='Specify a package',
        type=str  # Provides a default value if not specified
    )

    # Add a named argument that acts as a switch (a boolean flag)
    # You can access it via args.verbose
    parser.add_argument(
        '-q', '--query',
        help='Query a package',
        required=True,
        type=str
    )
    # action='store_true'
    # Makes it a flag; stores True if present, False otherwise

    parser.add_argument(
        '-l', '--limit',
        help='limit the number of results',
        type=int,  # Automatically converts the argument to an integer
        required=True  # Makes this named argument mandatory
    )

    # The parse_args() method will read the arguments and handle them
    # according to how you defined them.
    parsed_args = parser.parse_args(args=args)

    if parsed_args.limit <= 0:
        print(json.dumps({"error": "Limit is required. Please provide a positive integer for limit."}))
        return

    if len(parsed_args.query) <= 0:
        print(json.dumps({"error": "Query is required. Please provide a query text."}))
        return

    if len(parsed_args.package) <= 0:
        print(json.dumps({"error": "Package is required. Please provide a package name."}))
        return

    #print(f"\nProcessing completed for number {parsed_args.limit}. Result saved to {parsed_args.query}.")
    print(api_search(parsed_args.package, parsed_args.query, parsed_args.limit))

if __name__ == "__main__":
    main()