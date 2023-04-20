""" Visualizations for Riddle Me This. """

# TODO FIX THIS CODE AND ADD TO FRONTEND. NOT MUCH LONGER NOW.

import stanza
import pandas as pd
import networkx as nx
import numpy as np
from pyvis.network import Network

def download_stanza_pipeline(lang="en"):
    stanza.download(lang)
    nlp = stanza.Pipeline(lang, processors="tokenize,ner")
    return nlp

def perform_ner(nlp, text):
    doc = nlp(text)
    named_entities = [ent.text for ent in doc.ents]
    return doc, named_entities

def build_cooccurrence_graph(doc, named_entities, window_size=7):
    G = nx.Graph()
    G.add_nodes_from(named_entities)

    for sent in doc.sentences:
        for idx, word in enumerate(sent.words):
            if word.text in named_entities:
                for neighbor_idx in range(idx + 1, min(idx + 1 + window_size, len(sent.words))):
                    neighbor = sent.words[neighbor_idx]
                    if neighbor.text in named_entities:
                        G.add_edge(word.text, neighbor.text)

    return G

def extract_important_entities(G):
    pagerank = nx.pagerank(G)
    threshold = np.mean(list(pagerank.values()))
    important_entities = [entity for entity, score in pagerank.items() if score > threshold]
    return important_entities

def build_relationship_dataframe(G):
    relationships = [(src, "co-occurs", tgt) for src, tgt in G.edges()]
    df = pd.DataFrame(relationships, columns=["Source", "Relationship", "Target"])
    return df

def visualize_and_save_network(G, important_entities, file_name="graph.html"):
    subgraph = G.subgraph(important_entities)
    net = Network(notebook=True)

    for node in subgraph.nodes():
        net.add_node(node, label=node, color="lightblue")

    for src, tgt in subgraph.edges():
        net.add_edge(src, tgt, label="co-occurs")

    net.show(file_name)
    net.save_graph(file_name)

# Usage example:
text = "Your input text here"
nlp = download_stanza_pipeline()
doc, named_entities = perform_ner(nlp, text)
G = build_cooccurrence_graph(doc, named_entities)
important_entities = extract_important_entities(G)
df = build_relationship_dataframe(G)
display(df)
visualize_and_save_network(G, important_entities, "graph.html")


import stanza
import spacy
import pandas as pd
import networkx as nx
from sklearn.cluster import KMeans
from pyvis.network import Network
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score

def download_pipelines(lang="en"):
    stanza.download(lang)
    nlp_stanza = stanza.Pipeline(lang, processors="tokenize,ner")
    nlp_spacy = spacy.load("en_core_web_sm")
    return nlp_stanza, nlp_spacy

def perform_ner(nlp, text):
    doc = nlp(text)
    named_entities = [ent.text for ent in doc.ents if ent.type in {"PERSON", "ORG", "PRODUCT", "GPE", "EVENT", "FAC", "LANGUAGE", "LAW"}]
    return named_entities

def create_entity_embeddings(nlp, named_entities):
    embeddings = [nlp(entity).vector for entity in named_entities]
    return embeddings

def find_optimal_clusters(data, max_k):
    iters = range(2, max_k+1, 2)
    s_scores = []
    for k in iters:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        kmeans.fit(data)
        s_scores.append(silhouette_score(data, kmeans.labels_))

    optimal_k = iters[s_scores.index(max(s_scores))]
    return optimal_k

def apply_kmeans_clustering(embeddings, n_clusters):
    kmeans = KMeans(n_clusters=n_clusters)
    labels = kmeans.fit_predict(embeddings)
    return labels

def create_clustered_graph(named_entities, labels, n_clusters):
    G = nx.Graph()
    G.add_nodes_from(named_entities)

    for i in range(n_clusters):
        cluster_entities = [named_entities[j] for j in range(len(named_entities)) if labels[j] == i]
        G.add_edges_from([(src, tgt) for src in cluster_entities for tgt in cluster_entities if src != tgt])

    return G

def visualize_and_save_network(G, file_name="graph.html"):
    net = Network(notebook=True)

    for node in G.nodes():
        net.add_node(node, label=node, color="lightblue")

    for src, tgt in G.edges():
        net.add_edge(src, tgt)

    net.show(file_name)
    net.save_graph(file_name)

# Usage example:
text = "Your input text here"
nlp_stanza, nlp_spacy = download_pipelines()
named_entities = perform_ner(nlp_stanza, text)
embeddings = create_entity_embeddings(nlp_spacy, named_entities)
n_clusters = find_optimal_clusters(embeddings, 10)
labels = apply_kmeans_clustering(embeddings, n_clusters)
G = create_clustered_graph(named_entities, labels, n_clusters)
visualize_and_save_network(G, "graph.html")
