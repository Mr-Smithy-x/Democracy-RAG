#%%
# Import necessary libraries
from flask import Flask, request, jsonify
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


try:
    from vector_search import get_embedding, find_similar
    print("Successfully imported functions from vector_search.py")
except ImportError:
    print("Could not import from vector_search.py. Defining functions here instead.")

    # Define the necessary functions if import fails
    def get_embedding(text: str) -> np.ndarray:
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

    def find_similar(query_vector: np.ndarray, limit: int = 5):
        """Find similar vectors using cosine similarity"""
        conn = connect_postgres_db()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                    SELECT 
                        bill,
                        title, 
                        text_content, 
                        1 - (embedding <=> %s::vector) as similarity, 
                        1 - (title_embedding <=> %s::vector) as short_title_similarity
                    FROM bills 
                    ORDER BY short_title_similarity DESC, similarity DESC LIMIT %s;
                """,
                (np.array(query_vector[0]).tolist(), np.array(query_vector[0]).tolist(), limit)
            )
            results = cur.fetchall()
            return results

        finally:
            cur.close()
            conn.close()


# Create a Flask app to serve search functionality
app = Flask(__name__)

@app.route('/search', methods=['GET'], strict_slashes=False)
def api_search():
    data = request.args
    print(data)
    if not data or 'query' not in data:
        return jsonify({'error': 'No query provided'}), 400

    query_text = data['query']
    limit = data.get('limit', 5)  # Default to 5 results if not specified

    try:
        # Get embedding for the query
        query_vector = get_embedding(query_text)

        # Find similar documents
        similar_results = find_similar(query_vector, limit=limit)

        # Format results
        results = []
        for bill, title, text, similarity, short_title_similarity in similar_results:
            results.append({
                'bill': bill,
                'title': title,
                'text': text,
                'title_similarity': float(short_title_similarity),
                'similarity': float(similarity)  # Convert to float for JSON serialization
            })

        return jsonify({
            'query': query_text,
            'results': results
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
    print("Server running at http://localhost:5001")
    print("To test, send a POST request to http://localhost:5001/search with JSON body: {'query': 'your search text', 'limit': 5}")