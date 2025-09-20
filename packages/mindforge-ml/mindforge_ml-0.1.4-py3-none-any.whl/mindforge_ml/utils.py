import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from transformers import AutoTokenizer

def scale_data(X):
    scaler = StandardScaler()
    scaler = scaler.fit_transform(X)
    scaler = pd.DataFrame(scaler).fillna(0).values
    return scaler

def cluster_kmeans(X, n_clusters=3, random_state=42):
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    return kmeans.fit_predict(X)

def reduce_pca(X, n_components=2):
    pca = PCA(n_components=n_components)
    return pca.fit_transform(X)

def reduce_tsne(X, n_components=2, random_state=42, perplexity=30, lr=200):
    tsne = TSNE(n_components=n_components, random_state=random_state, perplexity=perplexity, learning_rate=lr)
    return tsne.fit_transform(X)

def detect_anomalies(errors, threshold=None):
    if threshold is None:
        threshold = errors.mean() + 2 * errors.std()
    anomalies = errors > threshold
    return anomalies, threshold

# TRANSFORMER MODEL UTILITIES 
tokenizer = AutoTokenizer.from_pretrained("t5-base") #t5-base

def ml_vocab_size():
    return tokenizer.vocab_size

def pad_token_id():
    return tokenizer.pad_token_id

def tokenize(query):
    token = tokenizer(query, return_tensors='pt')
    return token

def smart_tokenizer(query, target, max_len=512, stride=128):
    query_tokens = tokenizer(query, add_special_tokens=False)['input_ids']
    target_tokens = tokenizer(target, add_special_tokens=False)['input_ids']

    querylen = len(query_tokens)
    targetlen = len(target_tokens)

    if querylen <= max_len and targetlen <= max_len:
        inputs = tokenizer(
            query,
            text_target=target,
            max_length=max_len,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )
        
    else:
        # Handle overflow (e.g., truncate or split into chunks)
        inputs = tokenizer(
            query,
            text_target=target,
            return_overflowing_tokens=True,
            max_length=max_len,
            stride=stride,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )
    
    input_ids=inputs['input_ids']
    attention_mask=inputs['attention_mask']
    labels=inputs['labels']
    return input_ids, attention_mask, labels
