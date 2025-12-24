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
        self.edge_to_cycle_map = {}
        self.edge_to_nodes_map = {}

    def _build_graph(self, df):
        """
        Build a directed graph from transaction data.
        Nodes: accounts (unique senders and receivers)
        Edges: transactions with weights based on amount and frequency
        """
        self.graph = nx.DiGraph()

        # Identify columns (assume 'sender', 'receiver', 'amount' or fallback to first three columns)
        # Identify columns (Smart detection)
        possible_senders = ['user_id', 'sender', 'source', 'origin_account']
        possible_receivers = ['recipient_id', 'receiver', 'recipient', 'target', 'destination_account']
        
        sender_col = next((c for c in possible_senders if c in df.columns), df.columns[0])
        # If receiver column not found, try to find a column that isn't sender, amount, tx_id, time
        receiver_col = next((c for c in possible_receivers if c in df.columns), None)
        
        if receiver_col is None:
             # Fallback: using column 1 if it's not sender, else column 2
             if len(df.columns) > 1 and df.columns[1] != sender_col:
                 receiver_col = df.columns[1]
             elif len(df.columns) > 2:
                 receiver_col = df.columns[2]
             else:
                 receiver_col = df.columns[-1] # Desperate fallback

        amount_col = 'amount' if 'amount' in df.columns else (df.columns[2] if len(df.columns) > 2 else None)

        # Add nodes
        all_accounts = set(df[sender_col].dropna()) | set(df[receiver_col].dropna())
        self.graph.add_nodes_from(all_accounts)

        # Add edges with weights
        # Add edges with weights
        edge_counts = defaultdict(int)
        self.edge_amounts = defaultdict(float)

        for _, row in df.iterrows():
            sender = str(row[sender_col]).strip().lower() # Case-insensitive demo
            receiver = str(row[receiver_col]).strip().lower()
            amount = float(row[amount_col]) if amount_col and pd.notna(row[amount_col]) else 1.0

            if sender and receiver:
                edge_counts[(sender, receiver)] += 1
                self.edge_amounts[(sender, receiver)] += amount

        for (sender, receiver), count in edge_counts.items():
            total_amount = self.edge_amounts[(sender, receiver)]
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
        # Ensure case-insensitive matching
        sender = str(sender).strip().lower()
        receiver = str(receiver).strip().lower()
        
        score = 0.0
        reasons = []

        # REMOVED: Centrality-based anomaly (Interaction between isolated accounts) per user request
        # REMOVED: Edge weight anomaly (Unusually high value) per user request

        # Community-based anomaly: transactions between different communities are suspicious
        sender_comm = self.communities.get(sender, -1)
        receiver_comm = self.communities.get(receiver, -1)
        if sender_comm != receiver_comm:
            score += 0.3  # Cross-community transaction penalty
            reasons.append("Unrelated Network Transfer")

        # Cycle Detection Check
        if (sender, receiver) in self.edge_to_cycle_map:
            score += 0.9
            cycle_desc = self.edge_to_cycle_map[(sender, receiver)]
            reasons.append("Circular Money Loop Detected")

        return min(score, 1.0), reasons

    def detect_anomalies(self, df):
        """
        Detect anomalies in transaction data using graph-based methods.
        Returns: (scores_list, reasons_list_of_lists, node_paths_list)
        """
        if df.empty:
            return [], [], []

        # Build graph
        self._build_graph(df)
        self._compute_centrality()
        self._detect_communities()

        # DETECT CYCLES (Money Laundering Loops)
        self.edge_to_cycle_map = {}
        self.edge_to_nodes_map = {} 
        try:
            # Only run on reasonable size graphs to avoid hanging
            if self.graph.number_of_nodes() < 2000:
                # nx.simple_cycles is an iterator - do NOT use list() on it for large graphs
                cycles_iter = nx.simple_cycles(self.graph)
                limit = 0
                for cycle in cycles_iter:
                    limit += 1
                    if limit > 5000: break # Early exit for performance

                    if 2 <= len(cycle) <= 6: 
                        cycle_amounts = []
                        for i in range(len(cycle)):
                            u = cycle[i]
                            v = cycle[(i + 1) % len(cycle)]
                            amt = self.edge_amounts.get((u, v), 0.0)
                            cycle_amounts.append(amt)
                        
                        if not cycle_amounts: continue
                        min_amt = min(cycle_amounts)
                        max_amt = max(cycle_amounts)
                        
                        if min_amt > 0 and (min_amt / max_amt) > 0.3:
                            avg_amt = sum(cycle_amounts) / len(cycle_amounts)
                            cycle_str = " -> ".join(str(n) for n in cycle) + " -> " + str(cycle[0])
                            cycle_str += f" (Avg Amount: {int(avg_amt)})"
                            
                            for i in range(len(cycle)):
                                u = cycle[i]
                                v = cycle[(i + 1) % len(cycle)]
                                self.edge_to_cycle_map[(u, v)] = cycle_str
                                self.edge_to_nodes_map[(u, v)] = [str(n) for n in cycle]
        except Exception:
            pass

        # Identify columns
        possible_senders = ['user_id', 'sender', 'source', 'origin_account']
        possible_receivers = ['recipient_id', 'receiver', 'recipient', 'target', 'destination_account']
        
        sender_col = next((c for c in possible_senders if c in df.columns), df.columns[0])
        receiver_col = next((c for c in possible_receivers if c in df.columns), None)
        
        if receiver_col is None:
             receiver_col = df.columns[1] if len(df.columns) > 1 else df.columns[-1]

        amount_col = 'amount' if 'amount' in df.columns else (df.columns[2] if len(df.columns) > 2 else None)

        scores = []
        all_reasons = []
        node_paths = []
        
        for _, row in df.iterrows():
            sender = str(row[sender_col]).strip().lower()
            receiver = str(row[receiver_col]).strip().lower()
            amount = float(row[amount_col]) if amount_col and pd.notna(row[amount_col]) else 1.0

            if pd.notna(sender) and pd.notna(receiver):
                score, reasons = self._compute_anomaly_score(sender, receiver, amount)
                # Pull raw cycle nodes for the WOW feature
                nodes = self.edge_to_nodes_map.get((sender, receiver))
                node_paths.append(nodes)
            else:
                score = 0.5 
                reasons = ["Incomplete transaction data"]
                node_paths.append(None)

            scores.append(score)
            all_reasons.append(reasons)
                
        return scores, all_reasons, node_paths
