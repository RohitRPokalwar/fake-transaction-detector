import networkx as nx
import community as community_louvain
import numpy as np
import pandas as pd
from collections import defaultdict

class GraphAnomalyDetector:
    """
    Graph-based anomaly detection for transactions.
    Models transactions as directed graphs where accounts are nodes and transactions are edges.
    Uses centrality measures and community detection to identify anomalous transactions.
    """

    def __init__(self):
        self.graph = None
        self.centrality_scores = {}
        self.edge_weights = {}
        self.communities = {}

    def _build_graph(self, df):
        """
        Build a directed graph from transaction data.
        Nodes: accounts (unique senders and receivers)
        Edges: transactions with weights based on amount and frequency
        """
        self.graph = nx.DiGraph()

        # Identify columns (assume 'sender', 'receiver', 'amount' or fallback to first three columns)
        sender_col = 'sender' if 'sender' in df.columns else df.columns[0]
        receiver_col = 'receiver' if 'receiver' in df.columns else df.columns[1]
        amount_col = 'amount' if 'amount' in df.columns else (df.columns[2] if len(df.columns) > 2 else None)

        # Add nodes
        all_accounts = set(df[sender_col].dropna()) | set(df[receiver_col].dropna())
        self.graph.add_nodes_from(all_accounts)

        # Add edges with weights
        edge_counts = defaultdict(int)
        edge_amounts = defaultdict(float)

        for _, row in df.iterrows():
            sender = row[sender_col]
            receiver = row[receiver_col]
            amount = float(row[amount_col]) if amount_col and pd.notna(row[amount_col]) else 1.0

            if pd.notna(sender) and pd.notna(receiver):
                edge_counts[(sender, receiver)] += 1
                edge_amounts[(sender, receiver)] += amount

        for (sender, receiver), count in edge_counts.items():
            total_amount = edge_amounts[(sender, receiver)]
            # Weight combines frequency and total amount (normalized)
            weight = count * np.log1p(abs(total_amount))
            self.graph.add_edge(sender, receiver, weight=weight)
            self.edge_weights[(sender, receiver)] = weight

    def _compute_centrality(self):
        """
        Compute centrality measures for nodes.
        """
        try:
            degree_cent = nx.degree_centrality(self.graph)
            betweenness_cent = nx.betweenness_centrality(self.graph, weight='weight')
            eigenvector_cent = nx.eigenvector_centrality_numpy(self.graph, weight='weight')
        except:
            # Fallback if centrality computation fails (e.g., disconnected graph)
            degree_cent = nx.degree_centrality(self.graph)
            betweenness_cent = {node: 0.0 for node in self.graph.nodes()}
            eigenvector_cent = {node: 0.0 for node in self.graph.nodes()}

        # Combine centrality measures
        self.centrality_scores = {}
        for node in self.graph.nodes():
            combined_cent = (degree_cent.get(node, 0) +
                           betweenness_cent.get(node, 0) +
                           eigenvector_cent.get(node, 0)) / 3.0
            self.centrality_scores[node] = combined_cent

    def _detect_communities(self):
        """
        Detect communities using Louvain method.
        """
        try:
            # Convert to undirected for community detection
            undirected_graph = self.graph.to_undirected()
            partition = community_louvain.best_partition(undirected_graph, weight='weight')
            self.communities = partition
        except:
            # Fallback: assign all nodes to one community
            self.communities = {node: 0 for node in self.graph.nodes()}

    def _compute_anomaly_score(self, sender, receiver, amount):
        """
        Compute anomaly score for a single transaction.
        Returns: (score, reasons_list)
        """
        score = 0.0
        reasons = []

        # Centrality-based anomaly: transactions between low-centrality nodes are more suspicious
        sender_cent = self.centrality_scores.get(sender, 0.0)
        receiver_cent = self.centrality_scores.get(receiver, 0.0)
        
        # Contribution from low centrality
        centrality_contribution = (1 - (sender_cent + receiver_cent) / 2.0) * 0.5
        score += centrality_contribution
        
        if centrality_contribution > 0.3:
            reasons.append("Interaction between isolated/low-activity accounts")

        # Community-based anomaly: transactions between different communities are suspicious
        sender_comm = self.communities.get(sender, -1)
        receiver_comm = self.communities.get(receiver, -1)
        if sender_comm != receiver_comm:
            score += 0.3  # Cross-community transaction penalty
            reasons.append("Cross-Community Transaction (Unusual Group Interaction)")

        # Edge weight anomaly: unusual transaction amounts/frequencies
        edge_weight = self.edge_weights.get((sender, receiver), 0.0)
        if edge_weight > 0:
            # Normalize amount by edge weight (higher weight means more normal)
            normalized_amount = amount / edge_weight
            weight_contrib = min(normalized_amount, 1.0) * 0.2
            score += weight_contrib 
            
            if normalized_amount > 2.0:
                reasons.append("Unusually high value for this connection history")
        else:
            # New edge (not in training set? or just logic fallthrough)
            # In this self-built graph, edge exists if we just built it from df.
            # But if df is large, weight should be > 0.
            pass

        return min(score, 1.0), reasons

    def detect_anomalies(self, df):
        """
        Detect anomalies in transaction data using graph-based methods.

        Args:
            df (pd.DataFrame): Transaction data

        Returns:
            tuple: (scores_list, reasons_list_of_lists)
        """
        if df.empty:
            return [], []

        # Build graph
        self._build_graph(df)

        # Compute centrality
        self._compute_centrality()

        # Detect communities
        self._detect_communities()

        # Identify columns
        sender_col = 'sender' if 'sender' in df.columns else df.columns[0]
        receiver_col = 'receiver' if 'receiver' in df.columns else df.columns[1]
        amount_col = 'amount' if 'amount' in df.columns else (df.columns[2] if len(df.columns) > 2 else None)

        # Compute scores for each transaction
        scores = []
        all_reasons = []
        
        for _, row in df.iterrows():
            sender = row[sender_col]
            receiver = row[receiver_col]
            amount = float(row[amount_col]) if amount_col and pd.notna(row[amount_col]) else 1.0

            if pd.notna(sender) and pd.notna(receiver):
                score, reasons = self._compute_anomaly_score(sender, receiver, amount)
            else:
                score = 0.5 
                reasons = ["Incomplete transaction data"]

            scores.append(score)
            all_reasons.append(reasons)

        # Normalize scores to 0-1 range
        if scores:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                scores = [(s - min_score) / (max_score - min_score) for s in scores]
            else:
                scores = [0.5] * len(scores)  # All same, set to 0.5
                
        return scores, all_reasons
