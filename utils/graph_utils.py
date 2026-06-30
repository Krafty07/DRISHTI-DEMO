import streamlit as st
import networkx as nx
import numpy as np
import osmnx as ox

BENGALURU_PLACE = "Indiranagar, Bengaluru, India"
BENGALURU_CENTER = [12.978, 77.638]

@st.cache_resource(show_spinner=False)
def load_graph():
    G = ox.graph_from_place(BENGALURU_PLACE, network_type='drive', simplify=True)
    return G

def get_graph_gdfs(G):
    nodes_gdf, edges_gdf = ox.graph_to_gdfs(G)
    return nodes_gdf, edges_gdf

@st.cache_data(show_spinner=False)
def compute_scores(_G):
    Gu = _G.to_undirected() if _G.is_directed() else _G
    # Sample for speed — use largest component
    Gc = Gu.subgraph(max(nx.connected_components(Gu), key=len)).copy()
    sample = list(Gc.nodes)[:600]
    Gs = Gc.subgraph(sample).copy()

    bc = nx.betweenness_centrality(Gs, normalized=True)
    cc = nx.closeness_centrality(Gs)
    bridges = set(nx.articulation_points(Gs))

    def norm(d):
        vals = np.array(list(d.values()))
        mn, mx = vals.min(), vals.max()
        return {k: float((v-mn)/(mx-mn+1e-9)) for k, v in d.items()}

    bc_n = norm(bc)
    cc_n = norm(cc)

    scores = {}
    for node in Gs.nodes():
        bridge_bonus = 0.1 if node in bridges else 0.0
        scores[node] = 0.5*bc_n.get(node,0) + 0.3*cc_n.get(node,0) + 0.2*bridge_bonus

    # Normalize final scores
    mx = max(scores.values()) if scores else 1
    scores = {k: v/mx for k, v in scores.items()}
    return scores, bc, cc, bridges, Gs

def score_color(s):
    if s > 0.75: return '#EF4444'
    elif s > 0.50: return '#F59E0B'
    elif s > 0.25: return '#0EA5E9'
    return '#10B981'

def score_label(s):
    if s > 0.75: return '🔴 Critical'
    elif s > 0.50: return '🟠 High'
    elif s > 0.25: return '🔵 Medium'
    return '🟢 Low'

def run_cascade(Gs, scores, n_steps=15):
    G_sim = Gs.copy()
    sorted_nodes = sorted(scores, key=lambda x: -scores[x])
    baseline_eff = nx.global_efficiency(G_sim)
    results = []
    for step in range(min(n_steps, len(sorted_nodes))):
        node = sorted_nodes[step]
        if node in G_sim:
            G_sim.remove_node(node)
        eff = nx.global_efficiency(G_sim)
        ri = eff / baseline_eff if baseline_eff > 0 else 0
        comps = list(nx.connected_components(G_sim))
        lcc = len(max(comps, key=len)) if comps else 0
        results.append({
            'step': step+1,
            'resilience_index': round(ri, 4),
            'lcc_pct': round(100*lcc/max(len(Gs.nodes),1), 1),
            'efficiency': round(eff, 5),
        })
    return results, baseline_eff
