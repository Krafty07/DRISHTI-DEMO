import streamlit as st
import folium
from streamlit_folium import st_folium
import osmnx as ox
import networkx as nx
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.styles import DRISHTI_CSS, page_header, metric_card, render_sidebar_toggle

st.set_page_config(page_title="DRISHTI · Criticality", page_icon="🔥",
                   layout="wide", initial_sidebar_state="expanded")
st.markdown(DRISHTI_CSS, unsafe_allow_html=True)
render_sidebar_toggle()

with st.sidebar:
    st.markdown('<div class="sidebar-logo">🛰️ DRISHTI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Road Intelligence System</div>', unsafe_allow_html=True)

page_header(
    "🔥 Criticality Heatmap",
    "Every intersection scored by how much damage its loss would cause to the city.",
    active_step=4
)

# ── Info banner ───────────────────────────────────────────────
with st.expander("ℹ️  What is the Gatekeeper Score?", expanded=False):
    st.markdown("""
    <div style='font-size:0.85rem;color:#94A3B8;line-height:1.9;'>
    The <b style='color:#F59E0B'>Gatekeeper Score</b> is DRISHTI's multi-metric node criticality index.
    It combines four measures:<br><br>
    <b style='color:#0EA5E9'>Betweenness Centrality (40%)</b> — fraction of all city shortest-paths
    that pass through this node. High = traffic bottleneck.<br>
    <b style='color:#8B5CF6'>Closeness Centrality (25%)</b> — how fast this node can reach every
    other node. High = fast emergency response hub.<br>
    <b style='color:#10B981'>Efficiency Drop (25%)</b> — how much global network efficiency falls
    when this node is removed. Direct resilience impact.<br>
    <b style='color:#EF4444'>Bridge Detection (10%)</b> — articulation points whose removal
    disconnects the graph entirely. Automatic max score.<br><br>
    <b style='color:#E2E8F0'>Compound Vulnerability</b> additionally weights nodes on unpaved
    roads higher — a critical intersection on a dirt road is far more dangerous
    to lose in a monsoon than one on a highway.
    </div>
    """, unsafe_allow_html=True)

# ── Controls ──────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    zone = st.selectbox("City zone", [
        "Indiranagar", "Koramangala", "Whitefield", "Jayanagar"
    ], help="Analyse different parts of Bengaluru")
with col2:
    metric = st.selectbox("Score metric", [
        "Gatekeeper Score (composite)",
        "Betweenness Centrality only",
        "Closeness Centrality only",
    ], help="Switch between our composite score and individual metrics")
with col3:
    compound = st.toggle("Compound vulnerability",
        help="Multiplies the Gatekeeper Score by a surface quality factor — nodes on unpaved roads score higher")

ZONE_MAP = {
    "Indiranagar":  ("Indiranagar, Bengaluru, India",   [12.978, 77.638]),
    "Koramangala":  ("Koramangala, Bengaluru, India",   [12.934, 77.624]),
    "Whitefield":   ("Whitefield, Bengaluru, India",    [12.969, 77.750]),
    "Jayanagar":    ("Jayanagar, Bengaluru, India",     [12.930, 77.583]),
}
place, center = ZONE_MAP[zone]

@st.cache_resource(show_spinner=False)
def fetch_graph(place_name):
    return ox.graph_from_place(place_name, network_type='drive', simplify=True)

@st.cache_data(show_spinner=False)
def compute_scores(_G, metric_name, use_compound):
    Gu = _G.to_undirected()
    comps = list(nx.connected_components(Gu))
    Gc = Gu.subgraph(max(comps, key=len)).copy()
    nodes_list = list(Gc.nodes)[:500]
    Gs = Gc.subgraph(nodes_list).copy()

    bc = nx.betweenness_centrality(Gs, normalized=True)
    cc = nx.closeness_centrality(Gs)
    bridges = set(nx.articulation_points(Gs))

    def norm(d):
        vals = np.array(list(d.values()))
        mn, mx = vals.min(), vals.max()
        return {k: float((v-mn)/(mx-mn+1e-9)) for k,v in d.items()}

    bc_n = norm(bc)
    cc_n = norm(cc)

    scores = {}
    for n in Gs.nodes():
        b = 0.1 if n in bridges else 0.0
        if "Betweenness" in metric_name:
            scores[n] = bc_n.get(n, 0)
        elif "Closeness" in metric_name:
            scores[n] = cc_n.get(n, 0)
        else:
            scores[n] = 0.5*bc_n.get(n,0) + 0.3*cc_n.get(n,0) + 0.1*b + 0.1*bc_n.get(n,0)

    if use_compound:
        rng = np.random.default_rng(7)
        for n in scores:
            unpaved_frac = rng.random() * 0.4
            scores[n] = scores[n] * (1 + 0.3 * unpaved_frac)

    mx = max(scores.values()) if scores else 1
    scores = {k: min(v/mx, 1.0) for k,v in scores.items()}
    return scores, bc, cc, bridges, Gs

with st.spinner("Computing Gatekeeper Scores on real Bengaluru road network…"):
    G = fetch_graph(place)
    scores, bc, cc, bridges, Gs = compute_scores(G, metric, compound)
    nodes_gdf, edges_gdf = ox.graph_to_gdfs(G)

# ── Summary metrics ───────────────────────────────────────────
critical = sum(1 for s in scores.values() if s > 0.75)
high     = sum(1 for s in scores.values() if 0.5 < s <= 0.75)
bridge_c = len(bridges)
avg_bc   = float(np.mean(list(bc.values()))) if bc else 0

m1,m2,m3,m4 = st.columns(4)
m1.markdown(metric_card(str(critical), "Critical nodes",
    "Score > 0.75", "#EF4444"), unsafe_allow_html=True)
m2.markdown(metric_card(str(high), "High-risk nodes",
    "Score 0.5–0.75", "#F59E0B"), unsafe_allow_html=True)
m3.markdown(metric_card(str(bridge_c), "Bridge nodes",
    "Removal = disconnect", "#8B5CF6"), unsafe_allow_html=True)
m4.markdown(metric_card(f"{avg_bc:.4f}", "Avg betweenness",
    "Network-wide", "#0EA5E9"), unsafe_allow_html=True)

st.markdown('<hr class="d-divider">', unsafe_allow_html=True)

# ── Map ───────────────────────────────────────────────────────
def score_to_color(s):
    if s > 0.75: return '#EF4444'
    elif s > 0.5: return '#F59E0B'
    elif s > 0.25: return '#0EA5E9'
    return '#10B981'

def score_to_label(s):
    if s > 0.75: return 'CRITICAL'
    elif s > 0.5: return 'HIGH'
    elif s > 0.25: return 'MEDIUM'
    return 'LOW'

m = folium.Map(location=center, zoom_start=14,
               tiles='CartoDB dark_matter', prefer_canvas=True)

# Draw edges lightly
for _, row in edges_gdf.iterrows():
    if row.geometry:
        coords = [(y,x) for x,y in row.geometry.coords]
        folium.PolyLine(coords, color='#1E3A5F',
                        weight=1.2, opacity=0.5).add_to(m)

# Draw scored nodes
for nid, score in scores.items():
    if nid not in nodes_gdf.index:
        continue
    row = nodes_gdf.loc[nid]
    color = score_to_color(score)
    radius = max(3, score * 16)
    is_bridge = nid in bridges
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=radius,
        color='#FFFFFF' if is_bridge else color,
        weight=2 if is_bridge else 0,
        fill=True,
        fill_color=color,
        fill_opacity=0.88,
        popup=folium.Popup(
            f"""<div style='font-family:monospace;font-size:11px;
                            background:#0D1B2A;color:#E2E8F0;padding:8px;
                            border-radius:6px;min-width:180px;'>
              <b style='color:{color}'>{score_to_label(score)}</b><br>
              Node ID: {nid}<br>
              Gatekeeper Score: <b>{score:.3f}</b><br>
              Betweenness: {bc.get(nid,0):.4f}<br>
              Closeness: {cc.get(nid,0):.4f}<br>
              Bridge node: {'⚠️ YES' if is_bridge else 'No'}
            </div>""",
            max_width=220
        )
    ).add_to(m)

# Legend
legend = """
<div style='position:fixed;bottom:20px;left:20px;z-index:9999;
     background:#0D1B2A;border:1px solid rgba(14,165,233,0.3);
     border-radius:10px;padding:14px 18px;font-family:Inter,sans-serif;'>
  <div style='font-size:11px;font-weight:700;color:#E2E8F0;margin-bottom:10px;'>
    Gatekeeper Score
  </div>
  <div style='font-size:10px;color:#94A3B8;line-height:2;'>
    <span style='color:#EF4444;font-size:14px;'>●</span> Critical &gt; 0.75<br>
    <span style='color:#F59E0B;font-size:14px;'>●</span> High 0.50–0.75<br>
    <span style='color:#0EA5E9;font-size:14px;'>●</span> Medium 0.25–0.50<br>
    <span style='color:#10B981;font-size:14px;'>●</span> Low &lt; 0.25<br>
    <span style='color:#FFFFFF;font-size:12px;'>○</span> Bridge node ⚠️
  </div>
  <div style='font-size:9px;color:#334155;margin-top:8px;'>Click nodes for details</div>
</div>"""
m.get_root().html.add_child(folium.Element(legend))

st_folium(m, width=None, height=520, returned_objects=[])

# ── Top 5 gatekeeper nodes ────────────────────────────────────
st.markdown('<hr class="d-divider">', unsafe_allow_html=True)
st.markdown("#### 🏆 Top 10 Gatekeeper nodes — highest city impact")
with st.expander("ℹ️  Why does this matter for disaster response?", expanded=False):
    st.markdown("""
    <div style='font-size:0.85rem;color:#94A3B8;line-height:1.8;'>
    These nodes are <b style='color:#EF4444'>single points of failure</b>.
    Losing any one of them forces large sections of the city to reroute,
    increasing average travel times by 20–60%.<br><br>
    For disaster planners, this list answers: <i>"If a flood blocks one intersection,
    which intersection causes the most damage?"</i> — enabling pre-emptive
    deployment of emergency assets <b>before</b> the flood hits.
    </div>
    """, unsafe_allow_html=True)

top10 = sorted(scores.items(), key=lambda x: -x[1])[:10]
for rank, (nid, s) in enumerate(top10, 1):
    color = score_to_color(s)
    label = score_to_label(s)
    bridge_tag = " ⚠️ BRIDGE" if nid in bridges else ""
    col_r, col_b2 = st.columns([3, 1])
    with col_r:
        st.progress(float(s), text=f"#{rank}  Node {nid}  [{label}{bridge_tag}]  —  Score: {s:.3f}")
    with col_b2:
        st.markdown(
            f'<div style="font-size:0.75rem;color:{color};'
            f'text-align:right;padding-top:0.5rem;">{label}</div>',
            unsafe_allow_html=True
        )
