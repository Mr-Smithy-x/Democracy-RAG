import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple

# Set random seed for reproducibility
np.random.seed(42)
torch.manual_seed(42)

class SimilaritySearch:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the similarity search with a specific transformer model.

        Args:
            model_name (str): The name of the transformer model to use from Hugging Face
        """
        # Load tokenizer and model from Hugging Face
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.documents = []
        self.documents_df = None
        self.embeddings = None

    def create_mock_data(self, num_documents: int = 20) -> pd.DataFrame:
        """
        Create mock text data for similarity search.

        Args:
            num_documents (int): Number of mock documents to create

        Returns:
            pd.DataFrame: DataFrame containing mock text documents and metadata
        """
        topics = [
            "artificial intelligence and machine learning",
            "climate change and environmental sustainability",
            "renewable energy technologies",
            "space exploration and astronomy",
            "quantum computing and physics",
            "biotechnology and genetic engineering",
            "cryptocurrency and blockchain technology",
            "cybersecurity and data privacy"
        ]

        documents = []
        main_topics = []
        additional_topics_list = []

        for i in range(num_documents):
            # Select a random topic as the main subject
            main_topic = np.random.choice(topics)
            main_topics.append(main_topic)

            # Select 0-2 additional topics to blend in
            num_additional = np.random.randint(0, 3)
            additional_topics = np.random.choice(
                [t for t in topics if t != main_topic],
                size=min(num_additional, len(topics)-1),
                replace=False
            )
            additional_topics_list.append(list(additional_topics))

            # Create a document about the topic(s)
            doc = f"Document {i+1}: This text discusses {main_topic}"
            if len(additional_topics) > 0:
                doc += f" with connections to {' and '.join(additional_topics)}"
            doc += "."

            # Add some random sentences
            sentences = [
                "The latest research in this field shows promising results.",
                "Many experts consider this area crucial for future development.",
                "Recent advances have accelerated progress significantly.",
                "This subject has gained considerable attention in recent years.",
                "There are still many unanswered questions in this domain.",
                "Interdisciplinary approaches are proving valuable in this context."
            ]

            # Add 1-3 random sentences
            for _ in range(np.random.randint(1, 4)):
                doc += " " + np.random.choice(sentences)

            documents.append(doc)

        # Create a DataFrame with documents and metadata
        self.documents_df = pd.DataFrame({
            "document_id": range(num_documents),
            "text": documents,
            "main_topic": main_topics,
            "additional_topics": additional_topics_list,
            "created_at": pd.Timestamp.now()
        })

        self.documents = documents
        return self.documents_df

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Convert text to embeddings using the transformer model.

        Args:
            text (str): Input text to convert to embedding

        Returns:
            np.ndarray: The embedding vector
        """
        # Tokenize the text and convert to tensor
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

        # Get model output
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Use mean pooling to get a single vector representation
        attention_mask = inputs['attention_mask']
        token_embeddings = outputs.last_hidden_state

        # Calculate mean of token embeddings weighted by attention mask
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

        return embeddings.numpy()

    def index_documents(self) -> np.ndarray:
        """
        Create embeddings for all documents in the collection.

        Returns:
            np.ndarray: Matrix of document embeddings
        """
        all_embeddings = []
        for doc in self.documents:
            embedding = self.get_embedding(doc)
            all_embeddings.append(embedding[0])

        self.embeddings = np.array(all_embeddings)
        return self.embeddings

    def search(self, query: str, top_k: int = 5) -> pd.DataFrame:
        """
        Search for documents similar to the query.

        Args:
            query (str): Search query
            top_k (int): Number of top results to return

        Returns:
            pd.DataFrame: DataFrame containing search results with similarity scores
        """
        if self.embeddings is None:
            raise ValueError("No documents have been indexed. Call index_documents() first.")

        # Get embedding for the query
        query_embedding = self.get_embedding(query)

        # Calculate cosine similarity between query and all documents
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]

        # Get indices of top_k most similar documents
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # Prepare results using pandas
        results_data = []
        for idx in top_indices:
            results_data.append({
                "document_id": idx,
                "similarity": round(float(similarities[idx]), 4),
                "text": self.documents[idx],
                "main_topic": self.documents_df.loc[idx, "main_topic"],
                "additional_topics": self.documents_df.loc[idx, "additional_topics"]
            })

        results_df = pd.DataFrame(results_data)
        return results_df

    def display_results(self, results: pd.DataFrame) -> None:
        """
        Display search results in a formatted way.

        Args:
            results (pd.DataFrame): Search results from the search method
        """
        if results.empty:
            print("No results found.")
            return

        print(f"\n{'=' * 80}")
        print(f"{'SEARCH RESULTS':^80}")
        print(f"{'=' * 80}")

        for i, (_, row) in enumerate(results.iterrows()):
            print(f"\nRESULT #{i+1} (Score: {row['similarity']:.4f})")
            print(f"{'-' * 80}")
            print(f"Document: {row['text']}")
            print(f"Main Topic: {row['main_topic']}")
            if len(row['additional_topics']) > 0:
                print(f"Additional Topics: {', '.join(row['additional_topics'])}")

        print(f"\n{'=' * 80}\n")


# Example usage
if __name__ == "__main__":
    # Initialize similarity search engine
    print("Initializing similarity search with transformer model...")
    search_engine = SimilaritySearch()

    # Create mock data
    print("Creating mock documents...")
    documents_df = search_engine.create_mock_data(num_documents=15)

    # Print a sample of documents with metadata
    print(f"\nCreated {len(documents_df)} mock documents. Sample:")
    print("\nSample Documents with Metadata:")
    print(documents_df[["document_id", "text", "main_topic"]].head(3).to_string())

    # Index the documents
    print("\nIndexing documents with transformer model...")
    search_engine.index_documents()

    # Perform some sample searches
    sample_queries = [
        "Tell me about artificial intelligence",
        "Climate change and renewable energy",
        "Cybersecurity threats and solutions",
        "Quantum computing applications"
    ]

    for query in sample_queries:
        print(f"\nSearching for: '{query}'")
        results = search_engine.search(query, top_k=3)
        search_engine.display_results(results)

        # Demonstrate pandas functionality - analysis example
        print("\nPandas Analysis of Results:")
        if not results.empty:
            print(f"Average similarity score: {results['similarity'].mean():.4f}")
            print(f"Topics in results: {results['main_topic'].unique()}")
            print("\nResults Summary:")
            print(results[["document_id", "similarity", "main_topic"]].to_string(index=False))