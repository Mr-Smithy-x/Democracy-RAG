import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch

model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)


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


def index_documents(documents: []) -> np.ndarray:
    """
    Create embeddings for all documents in the collection.
    Returns:
        np.ndarray: Matrix of document embeddings
    """
    all_embeddings = []
    for doc in documents:
        embedding = get_embedding(doc)
        all_embeddings.append(embedding[0])

    embeddings = np.array(all_embeddings)
    return embeddings


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


# Example usage
chunks = chunk_text_by_words('../bills/BILLS-119hr1086ih.htm')

# Print chunks with index
for i, chunk in enumerate(chunks):
    print(f"\nChunk {i + 1}:")
    print(chunk)
    print(get_embedding(chunk).size)
    print("-" * 50)  # Separator between chunks