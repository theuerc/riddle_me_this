import stanza
import spacy
import pandas as pd
import networkx as nx
from pyvis.network import Network
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
import numpy as np
from spacy.cli import download
import logging


def download_stanza_pipeline(lang):
    """
    Download and return a Stanza pipeline for a given language.

    Args:
        lang (str): The language of the pipeline to download.

    Returns:
        stanza.Pipeline: The downloaded pipeline.
    """
    try:
        nlp = stanza.Pipeline(lang, processors="tokenize,ner")
    except OSError:
        logging.info(f"Model not found. Downloading {lang}..")
        stanza.download(lang)
        nlp = stanza.Pipeline(lang, processors="tokenize,ner")
    return nlp


class CoOccurrenceVisualizer:
    """
    A class for visualizing co-occurring named entities in a text.

    Attributes:
        nlp (stanza.Pipeline): A pipeline for performing named entity recognition.
    """
    def __init__(self, lang="en"):
        """
        Initialize a CoOccurrenceVisualizer object.

        Args:
            lang (str, optional): The language of the text. Defaults to "en".
        """
        self.nlp = download_stanza_pipeline(lang)

    def perform_ner(self, text):
        """
        Perform named entity recognition on a given text.

        Args:
            text (str): The text to perform named entity recognition on.

        Returns:
            tuple: A tuple containing a Stanza document and a list of named entities.
        """
        doc = self.nlp(text)
        named_entities = [ent.text for ent in doc.ents]
        return doc, named_entities

    @staticmethod
    def build_cooccurrence_graph(doc, named_entities, window_size=7):
        """
        Build a co-occurrence graph from a Stanza document and a list of named entities.

        Args:
            doc (stanza.Document): The Stanza document to build the graph from.
            named_entities (list): The list of named entities in the document.
            window_size (int, optional): The size of the window to use for co-occurrence. Defaults to 7.

        Returns:
            networkx.Graph: The co-occurrence graph.
        """
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

    @staticmethod
    def extract_important_entities(G):
        """
        Extract the important entities from a co-occurrence graph.

        Args:
            G (networkx.Graph): The co-occurrence graph.

        Returns:
            list: The list of important entities.
        """
        pagerank = nx.pagerank(G)
        threshold = np.mean(list(pagerank.values()))
        important_entities = [entity for entity, score in pagerank.items() if score > threshold]
        return important_entities

    def visualize_and_save(self, G, important_entities, file_name="graph.html"):
        """
               Visualize a co-occurrence graph and save it to a file.

               Args:
                   G (networkx.Graph): The co-occurrence graph to visualize.
                   important_entities (list): The list of important entities to include in the visualization.
                   file_name (str, optional): The name of the file to save the visualization to. Defaults to "graph.html".
        """
        subgraph = G.subgraph(important_entities)
        net = Network(notebook=True)

        for node in subgraph.nodes():
            net.add_node(node, label=node, color="lightblue")

        for src, tgt in subgraph.edges():
            net.add_edge(src, tgt, label="co-occurs")

        net.save_graph(file_name)

    def run(self, text, file_name="graph.html"):
        """
        Run the co-occurrence visualizer on a given text.

        Args:
            text (str): The text to perform co-occurrence visualization on.
            file_name (str, optional): The name of the file to save the visualization to. Defaults to "graph.html".
        """
        doc, named_entities = self.perform_ner(text)
        G = self.build_cooccurrence_graph(doc, named_entities)
        important_entities = self.extract_important_entities(G)
        self.visualize_and_save(G, important_entities, file_name)


def download_en_core_web_(model="en_core_web_sm"):
    """
    Download and return the English core web pipeline for Spacy.

    Args:
    model (str, optional): The name of the Spacy model to download. Defaults to "en_core_web_sm".

    Returns:
        spacy.language.Language: The downloaded Spacy pipeline.
    """
    try:
        nlp = spacy.load(model)
    except OSError:
        logging.info(f"Model not found. Downloading {model}..")
        download(model)
        nlp = spacy.load(model)
    return nlp


class EntityClusterVisualizer:
    """
    A class for visualizing clusters of named entities in a text.

    Attributes:
        nlp_stanza (stanza.Pipeline): A pipeline for performing named entity recognition with Stanza.
        nlp_spacy (spacy.language.Language): A pipeline for processing text with Spacy.
    """

    def __init__(self, lang="en"):
        """
        Initialize an EntityClusterVisualizer object.

        Args:
            lang (str, optional): The language of the text. Defaults to "en".
        """
        self.nlp_stanza, self.nlp_spacy = self.download_pipelines(lang)

    @staticmethod
    def download_pipelines(lang):
        """
        Download and return Stanza and Spacy pipelines for a given language.

        Args:
            lang (str): The language of the pipelines to download.

        Returns:
            tuple: A tuple containing the downloaded Stanza and Spacy pipelines.
        """
        nlp_stanza = download_stanza_pipeline('en')
        nlp_spacy = download_en_core_web_()
        return nlp_stanza, nlp_spacy

    def perform_ner(self, text):
        """
        Perform named entity recognition on a given text.

        Args:
            text (str): The text to perform named entity recognition on.

        Returns:
            list: The list of named entities.
        """
        doc = self.nlp_stanza(text)
        named_entities = [ent.text for ent in doc.ents if ent.type in {"PERSON", "ORG", "PRODUCT", "GPE", "EVENT", "FAC", "LANGUAGE", "LAW"}]
        return named_entities

    def create_entity_embeddings(self, named_entities):
        """
        Create embeddings for a list of named entities.

        Args:
            named_entities (list): The list of named entities to create embeddings for.

        Returns:
            list: The list of entity embeddings.
        """
        embeddings = [self.nlp_spacy(entity).vector for entity in named_entities]
        return embeddings

    @staticmethod
    def find_optimal_clusters(data, max_k):
        """
        Find the optimal number of clusters for a given dataset using the silhouette score.

        Args:
            data (list): The dataset to find the optimal number of clusters for.
            max_k (int): The maximum number of clusters to try.

        Returns:
            int: The optimal number of clusters.
        """
        iters = range(2, max_k + 1, 2)
        s_scores = []
        for k in iters:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
            kmeans.fit(data)
            s_scores.append(silhouette_score(data, kmeans.labels_))

        optimal_k = iters[s_scores.index(max(s_scores))]
        return optimal_k

    def apply_kmeans_clustering(self, embeddings, n_clusters):
        """
        Apply KMeans clustering to a set of embeddings.

        Args:
            embeddings (list): The embeddings to cluster.
            n_clusters (int): The number of clusters to use.

        Returns:
            list: The cluster labels.
        """
        kmeans = KMeans(n_clusters=n_clusters, n_init='auto')
        labels = kmeans.fit_predict(embeddings)
        return labels

    def create_clustered_graph(self, named_entities, labels, n_clusters):
        """
        Create a clustered graph from a set of named entities and their cluster labels.

        Args:
            named_entities (list): The list of named entities to include in the graph.
            labels (list): The cluster labels for the named entities.
            n_clusters (int): The number of clusters to use.

        Returns:
            networkx.Graph: The clustered graph.
        """
        G = nx.Graph()
        G.add_nodes_from(named_entities)

        for i in range(n_clusters):
            cluster_entities = [named_entities[j] for j in range(len(named_entities)) if labels[j] == i]
            G.add_edges_from([(src, tgt) for src in cluster_entities for tgt in cluster_entities if src != tgt])

        return G

    def visualize_and_save(self, G, file_name="graph.html"):
        """
        Visualize a clustered graph and save it to a file.

        Args:
            G (networkx.Graph): The clustered graph to visualize.
            file_name (str, optional): The name of the file to save the visualization to. Defaults to "graph.html".
        """
        net = Network(notebook=True)

        for node in G.nodes():
            net.add_node(node, label=node, color="lightblue")

        for src, tgt in G.edges():
            net.add_edge(src, tgt)

        net.save_graph(file_name)


    def run(self, text, max_k=10, file_name="graph.html"):
        """
        Run the entity cluster visualizer on a given text.

        Args:
            text (str): The text to perform entity clustering on.
            max_k (int, optional): The maximum number of clusters to try. Defaults to 10.
            file_name (str, optional): The name of the file to save the visualization to. Defaults to "graph.html".
        """
        named_entities = self.perform_ner(text)
        embeddings = self.create_entity_embeddings(named_entities)
        n_clusters = self.find_optimal_clusters(embeddings, max_k)
        labels = self.apply_kmeans_clustering(embeddings, n_clusters)
        G = self.create_clustered_graph(named_entities, labels, n_clusters)
        self.visualize_and_save(G, file_name)


def main():
    # load a text file
    with open("../../transcript.txt", "r") as f:
        text = f.read()

    co_occurrence_visualizer = CoOccurrenceVisualizer()
    co_occurrence_visualizer.run(text, "co_occurrence_graph.html")

    entity_cluster_visualizer = EntityClusterVisualizer()
    entity_cluster_visualizer.run(text, 10, "entity_cluster_graph.html")


if __name__ == "__main__":
    main()
