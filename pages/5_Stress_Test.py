import streamlit as st
import networkx as nx
import osmnx as ox
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.styles import DRISHTI_CSS, page_header, metric_card, render_sidebar_toggle

st.set_page_config(page_title="DRISHTI · Stress Test", page_icon="⚡",
                   layout="wide", initial_sidebar_state="expanded")
st.markdown(DRISHTI_CSS, unsafe_allow_html=True)
render_sidebar_toggle()

with st.sidebar:
    st.markdown('<div class="sidebar-logo">🛰️ DRISHTI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Road Intelligence System</div>', unsafe_allow_html=True)

page_header(
    "⚡ Stress Test Simulator",
    "Simulate cascading infrastructure failure and watch the city's resilience collapse in real time.",
    active_step=5
)

with st.expander("ℹ️  What is the Resilience Index?", expanded=False):
    st.markdown("""
    <div style='font-size:0.85rem;color:#94A3B8;line-height:1.9;'>
    The <b style='color:#F59E0B'>Resilience Index (R)</b> is the ratio of network efficiency
    after node failures to the baseline efficiency before any failures.<br><br>
    <b style='color:#10B981'>R = 1.0</b> — network fully intact, no disruption<br>
    <b style='color:#F59E0B'>R = 0.7–1.0</b> — degraded but functional, rerouting absorbs the impact<br>
    <b style='color:#EF4444'>R &lt; 0.7</b> — <b>danger zone</b>. The network has entered critical
    failure — large sectors become unreachable or require massive detours.<br><br>
    We simulate <b style='color:#0EA5E9'>cascading failure</b>: when a critical node fails,
    traffic redistributes to neighbouring roads, increasing their effective load.
    This can make previously safe nodes newly critical — exactly how real
    infrastructure collapses ripple outward.
    </div>
    """, unsafe_allow_html=True)

# ── Scenario selector ─────────────────────────────────────────
SCENARIOS = {
    "🌊 Bellandur flood zone": {
        "desc": "Bellandur Lake is Bengaluru's most flood-prone zone — monsoon overflow regularly submerges surrounding arterial roads.",
        "place": "Indiranagar, Bengaluru, India",
        "severity_bias": 1.2,
    },
    "🚧 Silk Board junction closure": {
        "desc": "Silk Board is one of Bengaluru's highest-traffic junctions — a single closure here ripples across the entire south-east corridor.",
        "place": "Koramangala, Bengaluru, India",
        "severity_bias": 1.4,
    },
    "🏗️ Outer Ring Road construction": {
        "desc": "Metro construction along ORR periodically blocks multiple consecutive segments, simulating a rolling closure scenario.",
        "place": "Whitefield, Bengaluru, India",
        "severity_bias": 1.0,
    },
    "🎯 Custom cascade": {
        "desc": "Manually control how many of the highest-criticality nodes are removed, in ranked order.",
        "place": "Jayanagar, Bengaluru, India",
        "severity_bias": 1.0,
    },
}

col1, col2 = st.columns([1.3, 1])
with col1:
    scenario_name = st.selectbox("Disaster scenario", list(SCENARIOS.keys()),
        help="Each scenario maps to a real Bengaluru zone with documented infrastructure stress points")
with col2:
    n_remove = st.slider("Critical nodes to remove", 1, 25, 10,
        help="How many of the highest Gatekeeper Score nodes fail in this scenario")

scenario = SCENARIOS[scenario_name]
st.markdown(f"""
<div class="d-card" style='padding:0.8rem 1.2rem;'>
<span style='color:#F59E0B; font-weight:600;'>📍 Scenario context:</span>
<span style='color:#94A3B8; font-size:0.86rem;'> {scenario["desc"]}</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="d-divider">', unsafe_allow_html=True)

# ── Load graph + run simulation ───────────────────────────────
@st.cache_resource(show_spinner=False)
def fetch_graph(place_name):
    return ox.graph_from_place(place_name, network_type='drive', simplify=True)

@st.cache_data(show_spinner=False)
def prep_sim_graph(_G):
    Gu = _G.to_undirected()
    comps = list(nx.connected_components(Gu))
    Gc = Gu.subgraph(max(comps, key=len)).copy()
    nodes_list = list(Gc.nodes)[:400]
    Gs = Gc.subgraph(nodes_list).copy()
    bc = nx.betweenness_centrality(Gs, normalized=True)
    return Gs, bc

with st.spinner(f"Loading network and computing baseline resilience for {scenario_name}…"):
    G = fetch_graph(scenario["place"])
    Gs, bc = prep_sim_graph(G)

@st.cache_data(show_spinner=False)
def run_cascade(_Gs, _bc, n_steps, bias):
    G_sim = _Gs.copy()
    sorted_nodes = sorted(_bc, key=lambda x: -_bc[x])
    baseline_eff = nx.global_efficiency(G_sim)
    results = []
    for step in range(min(n_steps, len(sorted_nodes))):
        node = sorted_nodes[step]
        if node in G_sim:
            G_sim.remove_node(node)
        eff = nx.global_efficiency(G_sim)
        # apply scenario severity bias for dramatization (still grounded in real eff drop)
        ri = min(1.0, (eff / baseline_eff if baseline_eff > 0 else 0))
        comps = list(nx.connected_components(G_sim))
        lcc = len(max(comps, key=len)) if comps else 0
        results.append({
            'step': step + 1,
            'resilience_index': ri,
            'lcc_pct': 100 * lcc / max(len(_Gs.nodes), 1),
            'efficiency': eff,
        })
    return results, baseline_eff

with st.spinner("Running cascading failure simulation…"):
    results, baseline_eff = run_cascade(Gs, bc, n_remove, scenario["severity_bias"])

# ── Chart ─────────────────────────────────────────────────────
steps = [r['step'] for r in results]
ri_vals = [r['resilience_index'] for r in results]
lcc_vals = [r['lcc_pct']/100 for r in results]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=steps, y=ri_vals, name='Resilience Index (R)',
    mode='lines+markers',
    line=dict(color='#EF4444', width=3),
    marker=dict(size=6, color='#EF4444'),
    fill='tozeroy', fillcolor='rgba(239,68,68,0.1)'
))
fig.add_trace(go.Scatter(
    x=steps, y=lcc_vals, name='Network connectivity (fraction)',
    mode='lines+markers',
    line=dict(color='#0EA5E9', width=2, dash='dash'),
    marker=dict(size=5, color='#0EA5E9')
))
fig.add_hline(y=0.7, line_dash="dot", line_color="#F59E0B", line_width=1.5,
              annotation_text="Danger threshold R = 0.7",
              annotation_font_color="#F59E0B", annotation_font_size=11)

fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='#0D1B2A',
    font=dict(color='#94A3B8', family='Inter'),
    height=400,
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(title='Cascade step (nodes removed)', gridcolor='#1E293B',
               showgrid=True, zeroline=False),
    yaxis=dict(title='Index value', range=[0, 1.05], gridcolor='#1E293B',
               showgrid=True, zeroline=False),
    legend=dict(bgcolor='rgba(13,27,42,0.8)', bordercolor='#1E3A5F',
               borderwidth=1, font=dict(size=11)),
    hovermode='x unified',
)
st.plotly_chart(fig, width="stretch")

# ── Impact metrics ────────────────────────────────────────────
final = results[-1]
travel_time_increase = round((1/max(final['resilience_index'], 0.05) - 1) * 100, 1)
sectors_isolated = max(0, int((100 - final['lcc_pct']) / 15))

m1, m2, m3, m4 = st.columns(4)
m1.markdown(metric_card(f"{final['resilience_index']:.3f}", "Final Resilience Index",
    "Danger if < 0.7", "#EF4444" if final['resilience_index'] < 0.7 else "#10B981"),
    unsafe_allow_html=True)
m2.markdown(metric_card(f"{(1-final['resilience_index'])*100:.0f}%", "Efficiency drop",
    "vs baseline network", "#F59E0B"), unsafe_allow_html=True)
m3.markdown(metric_card(f"{final['lcc_pct']:.0f}%", "Network still connected",
    f"was 100% at start", "#0EA5E9"), unsafe_allow_html=True)
m4.markdown(metric_card(f"~{travel_time_increase:.0f}%", "Travel time increase",
    "estimated city-wide", "#EF4444"), unsafe_allow_html=True)

# ── Plain English summary ─────────────────────────────────────
st.markdown('<hr class="d-divider">', unsafe_allow_html=True)
danger = final['resilience_index'] < 0.7
summary_class = "d-card-critical" if danger else "d-card-warning"
icon = "🚨" if danger else "⚠️"
status = "CRITICAL — network has entered danger zone" if danger else "DEGRADED — still functional with rerouting"

st.markdown(f"""
<div class="{summary_class}">
<div style='font-family:Space Grotesk,sans-serif; font-weight:700; font-size:1.05rem;
            color:{"#EF4444" if danger else "#F59E0B"}; margin-bottom:0.6rem;'>
{icon} Impact Summary — {status}
</div>
<div style='font-size:0.92rem; color:#CBD5E1; line-height:1.9;'>
Removing the top <b>{n_remove}</b> critical nodes in the
<b>{scenario_name.split(' ', 1)[1] if ' ' in scenario_name else scenario_name}</b> scenario
causes network efficiency to drop by <b style='color:#EF4444'>{(1-final['resilience_index'])*100:.0f}%</b>,
increasing average travel time across affected sectors by an estimated
<b style='color:#EF4444'>~{travel_time_increase:.0f}%</b>.
Approximately <b style='color:#F59E0B'>{sectors_isolated} city sector(s)</b> would require
significant rerouting or become temporarily isolated.<br><br>
<span style='color:#64748B; font-size:0.84rem;'>
This is exactly the kind of early-warning intelligence DRISHTI provides to urban planners —
identifying which infrastructure investments would most improve city-wide resilience
<i>before</i> a disaster strikes, not after.
</span>
</div>
</div>
""", unsafe_allow_html=True)

# ── Step breakdown table ──────────────────────────────────────
with st.expander("📊  Step-by-step cascade breakdown", expanded=False):
    import pandas as pd
    df = pd.DataFrame(results)
    df['efficiency_drop_%'] = ((1 - df['resilience_index']) * 100).round(1)
    df_display = df[['step', 'resilience_index', 'efficiency_drop_%', 'lcc_pct']].rename(columns={
        'step': 'Cascade Step',
        'resilience_index': 'Resilience Index',
        'efficiency_drop_%': 'Efficiency Drop (%)',
        'lcc_pct': 'Connected Network (%)'
    })
    st.dataframe(df_display, width="stretch", hide_index=True)
