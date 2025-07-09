#!/usr/bin/env python3
"""
Test script to verify HuggingFace embeddings are working correctly.
"""

from code_indexer import embedding_fn

def test_embeddings():
    """Test the HuggingFace embeddings functionality."""
    print("Testing HuggingFace embeddings...")
    
    test_texts = [
        "Hello world",
        "This is a Python function",
        "def calculate_sum(a, b): return a + b",
        "Jenkins pipeline configuration"
    ]
    
    try:
        embeddings = embedding_fn.embed_documents(test_texts)
        
        print(f"Successfully generated embeddings for {len(test_texts)} texts")
        print(f"Embedding dimension: {len(embeddings[0])}")
        print(f"All embeddings have the same dimension: {all(len(emb) == len(embeddings[0]) for emb in embeddings)}")
        
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        embeddings_array = np.array(embeddings)
        similarity_matrix = cosine_similarity(embeddings_array)
        
        print(f"Similarity matrix shape: {similarity_matrix.shape}")
        print("Embeddings are working correctly!")
        
        return True
        
    except Exception as e:
        print(f"Error testing embeddings: {e}")
        return False

if __name__ == "__main__":
    test_embeddings() 