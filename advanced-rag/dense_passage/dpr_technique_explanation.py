# =============================================================================
# DENSE PASSAGE RETRIEVAL (DPR) TECHNIQUE EXPLANATION
# =============================================================================
# DPR is a state-of-the-art technique for dense retrieval that uses two separate
# neural networks: one for encoding questions and another for encoding passages.
# This approach significantly outperforms traditional sparse retrieval methods
# like BM25 by learning semantic representations in a dense vector space.
# =============================================================================

# Import required libraries for DPR implementation
from transformers import (
    DPRQuestionEncoder,      # Neural network for encoding questions into dense vectors
    DPRContextEncoder,       # Neural network for encoding passages/contexts into dense vectors
    DPRQuestionEncoderTokenizer,  # Tokenizer specifically trained for question encoding
    DPRContextEncoderTokenizer,   # Tokenizer specifically trained for context encoding
)
import torch                  # PyTorch for deep learning operations
import numpy as np           # NumPy for numerical computations
from sklearn.metrics.pairwise import cosine_similarity  # For computing similarity between vectors

# =============================================================================
# MODEL LOADING PHASE
# =============================================================================
# Load pre-trained DPR models that have been fine-tuned on Natural Questions dataset
# These models are trained to create embeddings that are semantically meaningful
# for question-answer retrieval tasks

# Load the question encoder - this model converts questions into dense vectors
# The 'single-nq-base' indicates it's trained on Natural Questions dataset with base BERT architecture
question_encoder = DPRQuestionEncoder.from_pretrained(
    "facebook/dpr-question_encoder-single-nq-base"  # Pre-trained model from Facebook AI
)

# Load the context encoder - this model converts passages/contexts into dense vectors
# Both encoders are trained together but serve different purposes
context_encoder = DPRContextEncoder.from_pretrained(
    "facebook/dpr-ctx_encoder-single-nq-base"  # Pre-trained context encoder
)

# Load the question tokenizer - converts text questions into token IDs
# This tokenizer is specifically optimized for question formatting
question_tokenizer = DPRQuestionEncoderTokenizer.from_pretrained(
    "facebook/dpr-question_encoder-single-nq-base"  # Matches the question encoder
)

# Load the context tokenizer - converts text passages into token IDs
# This tokenizer is optimized for longer text passages
context_tokenizer = DPRContextEncoderTokenizer.from_pretrained(
    "facebook/dpr-ctx_encoder-single-nq-base"  # Matches the context encoder
)

# =============================================================================
# QUERY ENCODING PHASE
# =============================================================================
# Convert the user's question into a dense vector representation
# This is the first step in the retrieval pipeline

# Define the query/question we want to find relevant passages for
query = "capital of africa?"  # User's question in natural language

# Tokenize the query - convert text to token IDs that the model can process
# return_tensors="pt" specifies we want PyTorch tensors as output
question_inputs = question_tokenizer(query, return_tensors="pt")

# Encode the tokenized query into a dense vector (embedding)
# The pooler_output is the final representation used for similarity matching
# This creates a 768-dimensional vector that represents the semantic meaning of the question
question_embedding = question_encoder(**question_inputs).pooler_output

# =============================================================================
# PASSAGE ENCODING PHASE
# =============================================================================
# Convert all candidate passages into dense vector representations
# This is done once and can be cached for multiple queries

# Define a collection of passages that we want to search through
# In a real system, this would be a large corpus of documents
passages = [
    "Paris is the capital of France.",                    # European capital
    "Berlin is the capital of Germany.",                  # European capital
    "Madrid is the capital of Spain.",                    # European capital
    "Rome is the capital of Italy.",                      # European capital
    "Maputo is the capital of Mozambique.",               # African capital (RELEVANT!)
    "To be or not to be, that is the question.",          # Shakespeare quote (irrelevant)
    "The quick brown fox jumps over the lazy dog.",       # Pangram (irrelevant)
    "Grace Hopper was an American computer scientist and United States Navy rear admiral. who was a pioneer of computer programming, and one of the first programmers of the Harvard Mark I computer. inventor of the first compiler for a computer programming language.",  # Biography (irrelevant)
]

# Initialize list to store all passage embeddings
context_embeddings = []

# Process each passage individually to create embeddings
for passage in passages:
    # Tokenize the current passage - convert text to token IDs
    context_inputs = context_tokenizer(passage, return_tensors="pt")
    
    # Encode the tokenized passage into a dense vector
    # Each passage gets converted to a 768-dimensional vector
    context_embedding = context_encoder(**context_inputs).pooler_output
    
    # Add the embedding to our collection
    context_embeddings.append(context_embedding)

# =============================================================================
# VECTOR CONSOLIDATION PHASE
# =============================================================================
# Combine all passage embeddings into a single tensor for efficient computation
# This creates a matrix where each row is a passage embedding

# Concatenate all embeddings along dimension 0 (rows)
# Result: shape (num_passages, 768) - each row is one passage embedding
context_embeddings = torch.cat(context_embeddings, dim=0)

# =============================================================================
# SIMILARITY COMPUTATION PHASE
# =============================================================================
# Calculate how similar the question is to each passage using cosine similarity
# This is the core of the retrieval mechanism

# Compute cosine similarity between question embedding and all passage embeddings
# cosine_similarity measures the angle between vectors (1 = identical, 0 = orthogonal, -1 = opposite)
# We convert PyTorch tensors to NumPy arrays for sklearn compatibility
similarities = cosine_similarity(
    question_embedding.detach().numpy(),  # Question vector (1, 768)
    context_embeddings.detach().numpy()   # Passage vectors (8, 768)
)
print("Similarities:", similarities)  # Print similarity scores for each passage

# =============================================================================
# RETRIEVAL PHASE
# =============================================================================
# Find the most relevant passage based on similarity scores
# This is the final step that returns the best matching document

# Find the index of the passage with the highest similarity score
# np.argmax returns the index of the maximum value in the array
most_relevant_idx = np.argmax(similarities)

# Retrieve and display the most relevant passage
print("Most relevant passage:", passages[most_relevant_idx])

# =============================================================================
# EXPECTED OUTPUT ANALYSIS:
# =============================================================================
# The system should identify "Maputo is the capital of Mozambique." as the most relevant
# because it's the only passage that mentions an African capital, which directly
# answers the question "capital of africa?" (even though the question is grammatically
# incorrect, the semantic meaning is clear).
# 
# This demonstrates DPR's ability to understand semantic relationships rather than
# just keyword matching, which is why it's considered a top-tier retrieval technique.
# =============================================================================
