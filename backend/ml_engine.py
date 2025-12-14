import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
import numpy as np

# Load the model once when the server starts
print("Loading BERT model... this might take a moment.")
model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract text from paragraphs
        text = ' '.join([p.text for p in soup.find_all('p')])
        return text
    except Exception as e:
        print(f"Error scraping: {e}")
        return None

def summarize_article(url, num_sentences=3):
    full_text = extract_text(url)
    if not full_text:
        return "Error: Could not fetch article content."

    sentences = full_text.split('. ')
    if len(sentences) < num_sentences:
        return full_text

    # 1. Convert sentences to vector embeddings
    embeddings = model.encode(sentences)

    # 2. Use K-Means to find clusters (themes)
    n_clusters = min(num_sentences, len(sentences))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(embeddings)

    # 3. Find the sentence closest to each cluster center
    summary_sentences = []
    for i in range(n_clusters):
        center = kmeans.cluster_centers_[i]
        closest_idx, _ = pairwise_distances_argmin_min([center], embeddings)
        summary_sentences.append(sentences[closest_idx[0]])

    return ". ".join(summary_sentences) + "."