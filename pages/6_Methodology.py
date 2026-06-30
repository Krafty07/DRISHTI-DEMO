import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.styles import DRISHTI_CSS, page_header, render_sidebar_toggle

st.set_page_config(page_title="DRISHTI · Methodology", page_icon="📄",
                   layout="wide", initial_sidebar_state="expanded")
st.markdown(DRISHTI_CSS, unsafe_allow_html=True)
render_sidebar_toggle()

with st.sidebar:
    st.markdown('<div class="sidebar-logo">🛰️ DRISHTI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Road Intelligence System</div>', unsafe_allow_html=True)

page_header(
    "📄 Methodology & Sources",
    "What this demo simulates, what the real hackathon system will build, and the research it's based on.",
    active_step=5
)

# ── Disclaimer card ───────────────────────────────────────────
st.markdown("""
<div class="d-card-warning">
<div style='font-family:Space Grotesk,sans-serif; font-weight:700; color:#F59E0B;
            margin-bottom:0.5rem;'>⚠️ About this demo</div>
<div style='font-size:0.88rem; color:#CBD5E1; line-height:1.8;'>
This demo uses <b>real Bengaluru OSM road network data</b> for all graph analysis pages
(Road Graph, Criticality, Stress Test) — the betweenness centrality, closeness centrality,
and resilience simulations are mathematically real computations on real city data.<br><br>
The <b>Occlusion Simulation</b> page uses synthetic/simulated imagery to illustrate the
concept, since training a full segmentation model was out of scope for a selection demo.
The actual hackathon submission will run a fully trained model on real Cartosat-3 /
Sentinel-2 imagery provided during the event.
</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="d-divider">', unsafe_allow_html=True)

# ── Pipeline diagram (text-based, clean) ──────────────────────
st.markdown("### The full DRISHTI pipeline")

stages = [
    ("🛰️", "Satellite Input", "Cartosat-3, Sentinel-2, Resourcesat LISS-IV imagery", "#0EA5E9"),
    ("👁️", "Occlusion-Robust Segmentation", "CE-RoadNet cascade + P2CNet OSM fusion + multi-task heads", "#8B5CF6"),
    ("🕸️", "Topological Healing", "MST bridging + extended-line projection + junction smoothing", "#F59E0B"),
    ("🔥", "Criticality Scoring", "Gatekeeper Score: betweenness + closeness + bridges + surface quality", "#EF4444"),
    ("⚡", "Stress Testing", "Cascading failure simulation + Resilience Index", "#10B981"),
]

for icon, title, desc, color in stages:
    st.markdown(f"""
    <div style='display:flex; gap:1rem; align-items:center; padding:0.9rem 1.2rem;
                background:#0D1B2A; border:1px solid rgba(14,165,233,0.1);
                border-left:3px solid {color}; border-radius:8px; margin-bottom:0.6rem;'>
      <span style='font-size:1.6rem;'>{icon}</span>
      <div>
        <div style='font-family:Space Grotesk,sans-serif; font-weight:600;
                    color:#E2E8F0; font-size:0.95rem;'>{title}</div>
        <div style='font-size:0.8rem; color:#64748B; margin-top:0.2rem;'>{desc}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="d-divider">', unsafe_allow_html=True)

# ── Research papers ────────────────────────────────────────────
st.markdown("### Research foundations")
st.markdown(
    '<div style="font-size:0.85rem;color:#475569;margin-bottom:1rem;">'
    'Every technique in DRISHTI is grounded in peer-reviewed or arXiv research — not invented from scratch.'
    '</div>', unsafe_allow_html=True
)

papers = [
    ("CE-RoadNet", "Remote Sensing, 2025",
     "Cascaded encoder-decoder with smoothed dilated convolutions. 2.78M params — lighter than D-LinkNet (31M) yet better APLS.",
     "Cascade architecture, AGFF fusion module"),
    ("P2CNet", "Xu et al., NTU Singapore, 2023",
     "Two-branch network fusing satellite images with partial OSM road maps. +20% IoU gain from OSM fusion alone.",
     "OSM fusion branch, Missing Part (MP) loss"),
    ("BrightEarth Roads", "LuxCarta Technology, 2024",
     "Production pipeline with orientation + distance map heads, geometric junction smoothing via collinearity constraints.",
     "Multi-task decoder heads, road smoothing"),
    ("clDice", "Shit et al., CVPR 2021",
     "Topology-preserving loss computed on morphological skeleton overlap — directly penalises broken connectivity.",
     "Training loss + evaluation metric"),
    ("SAM-Road", "Hetang et al., CVPRW 2024 (Best Paper)",
     "Graph-direct road extraction using SAM as backbone with lightweight GNN head. Pretrained checkpoints available.",
     "Fallback inference pipeline"),
]

for name, source, desc, used_for in papers:
    st.markdown(f"""
    <div class="d-card">
      <div style='display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.5rem;'>
        <div>
          <span class="paper-badge">{name}</span>
          <span style='font-size:0.75rem; color:#475569;'>{source}</span>
        </div>
      </div>
      <div style='font-size:0.85rem; color:#94A3B8; margin-top:0.6rem; line-height:1.7;'>{desc}</div>
      <div style='font-size:0.75rem; color:#0EA5E9; margin-top:0.5rem;'>
        Used for: {used_for}
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="d-divider">', unsafe_allow_html=True)

# ── What's real vs simulated table ────────────────────────────
st.markdown("### What's real vs. simulated in this demo")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="d-card-safe">
    <div style='font-family:Space Grotesk,sans-serif; font-weight:700; color:#10B981;
                margin-bottom:0.6rem;'>✅ Real computation</div>
    <div style='font-size:0.85rem; color:#CBD5E1; line-height:1.9;'>
    • Bengaluru road network (live OSMnx pull)<br>
    • Betweenness &amp; closeness centrality<br>
    • Articulation point (bridge) detection<br>
    • Global efficiency calculations<br>
    • Cascading failure simulation<br>
    • Resilience Index computation
    </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="d-card-warning">
    <div style='font-family:Space Grotesk,sans-serif; font-weight:700; color:#F59E0B;
                margin-bottom:0.6rem;'>🧪 Simulated for demo</div>
    <div style='font-size:0.85rem; color:#CBD5E1; line-height:1.9;'>
    • Satellite tile imagery (synthetic)<br>
    • Occlusion recovery visuals<br>
    • IoU / clDice metric values<br>
    • Road surface quality classification<br>
    • Scenario severity bias factors
    </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="d-divider">', unsafe_allow_html=True)

# ── Team note ──────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding:2rem 0;'>
  <div style='font-family:Space Grotesk,sans-serif; font-size:1.3rem; font-weight:700; color:#E2E8F0;'>
    Team DRISHTI
  </div>
  <div style='font-size:0.85rem; color:#475569; margin-top:0.5rem; max-width:600px; margin-left:auto; margin-right:auto; line-height:1.8;'>
    Built for the ISRO Hackathon — Route Resilience: Occlusion-Robust Road Extraction
    &amp; Graph-Theoretic Criticality Analysis for Urban Mobility.<br><br>
    This demo showcases our complete system design. Given full hackathon access to
    Cartosat-3 imagery and 30 hours of build time, we will deliver the fully trained
    pipeline described above with real segmentation outputs on Bengaluru satellite data.
  </div>
</div>
""", unsafe_allow_html=True)
