import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils.styles import DRISHTI_CSS, render_sidebar_toggle

st.set_page_config(
    page_title="DRISHTI — Road Intelligence",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(DRISHTI_CSS, unsafe_allow_html=True)
render_sidebar_toggle()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🛰️ DRISHTI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Road Intelligence System</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Navigate the demo**", help="Each page shows one stage of our pipeline")
    st.markdown("""
    <div style='font-size:0.82rem; color:#475569; line-height:2;'>
    🏠 Home &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ← You are here<br>
    👁️ Occlusion Sim<br>
    🕸️ Road Graph<br>
    🔥 Criticality Map<br>
    ⚡ Stress Test<br>
    📄 Methodology
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#334155; line-height:1.6;'>
    <b style='color:#475569'>ISRO Hackathon 2025</b><br>
    Route Resilience Challenge<br>
    Team DRISHTI
    </div>
    """, unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────
st.markdown("""
<div style='padding: 3rem 0 1rem;'>
  <div style='font-family: Space Mono, monospace; font-size:0.75rem;
              color:#0EA5E9; letter-spacing:0.15em; margin-bottom:1rem;
              text-transform:uppercase;'>
    ISRO · NNRMS · Urban Mobility Intelligence
  </div>
  <div class="drishti-hero-title">Seeing every road.<br>Protecting every route.</div>
  <div class="drishti-tagline" style='margin-top:1rem;'>
    Deep Road Intelligence for Satellite-based Highway &amp; Topology Insights
  </div>
</div>
""", unsafe_allow_html=True)

# Scan-line hero visual
st.markdown("""
<div class="scan-container" style='background: linear-gradient(135deg, #0D1B2A 0%, #020B18 100%);
     border:1px solid rgba(14,165,233,0.15); border-radius:16px;
     padding: 2.5rem; margin: 1.5rem 0; position:relative; min-height:160px;'>
  <div class="scan-line"></div>
  <div style='display:flex; gap:3rem; align-items:center; flex-wrap:wrap;'>
    <div style='text-align:center;'>
      <div style='font-family:Space Mono,monospace; font-size:2.5rem; font-weight:700; color:#0EA5E9;'>18K+</div>
      <div style='font-size:0.72rem; color:#475569; text-transform:uppercase; letter-spacing:0.1em;'>Road nodes analysed</div>
    </div>
    <div style='width:1px; height:60px; background:rgba(14,165,233,0.15);'></div>
    <div style='text-align:center;'>
      <div style='font-family:Space Mono,monospace; font-size:2.5rem; font-weight:700; color:#F59E0B;'>Top 50</div>
      <div style='font-size:0.72rem; color:#475569; text-transform:uppercase; letter-spacing:0.1em;'>Critical gatekeeper nodes</div>
    </div>
    <div style='width:1px; height:60px; background:rgba(14,165,233,0.15);'></div>
    <div style='text-align:center;'>
      <div style='font-family:Space Mono,monospace; font-size:2.5rem; font-weight:700; color:#10B981;'>+34%</div>
      <div style='font-size:0.72rem; color:#475569; text-transform:uppercase; letter-spacing:0.1em;'>Connectivity gain post-healing</div>
    </div>
    <div style='width:1px; height:60px; background:rgba(14,165,233,0.15);'></div>
    <div style='text-align:center;'>
      <div style='font-family:Space Mono,monospace; font-size:2.5rem; font-weight:700; color:#EF4444;'>R &lt; 0.7</div>
      <div style='font-size:0.72rem; color:#475569; text-transform:uppercase; letter-spacing:0.1em;'>Resilience danger threshold</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Problem Statement ─────────────────────────────────────────
st.markdown("---")
c1, c2 = st.columns([1.2, 1])

with c1:
    st.markdown("### The Problem")
    st.markdown("""
    <div class="d-card">
    <div style='font-size:0.9rem; line-height:1.8; color:#94A3B8;'>
    Standard satellite road extraction fails in Indian cities due to
    <b style='color:#F59E0B'>tree canopies, building shadows, and monsoon cloud cover</b>.
    The resulting broken maps are useless for disaster response and traffic simulation
    because they lack topological connectivity.
    </div>
    </div>
    """, unsafe_allow_html=True)

    problems = [
        ("🌿", "Tree canopy occlusion", "Dense urban vegetation hides up to 40% of road pixels"),
        ("🌑", "Building shadow blindness", "Deep shadows cause spectral confusion with road surfaces"),
        ("💧", "Monsoon cloud cover", "Seasonal cloud cover creates systematic data gaps"),
    ]
    for icon, title, desc in problems:
        st.markdown(f"""
        <div class="d-card" style='padding:0.9rem 1.2rem; margin-bottom:0.5rem;'>
        <div style='display:flex; gap:0.8rem; align-items:flex-start;'>
          <span style='font-size:1.3rem;'>{icon}</span>
          <div>
            <div style='font-family:Space Grotesk,sans-serif; font-weight:600;
                        color:#E2E8F0; font-size:0.9rem;'>{title}</div>
            <div style='font-size:0.8rem; color:#475569; margin-top:0.2rem;'>{desc}</div>
          </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

with c2:
    st.markdown("### Our Solution")
    stages = [
        ("#0EA5E9", "01", "Occlusion-Robust Segmentation",
         "CE-RoadNet + P2CNet OSM fusion recovers hidden roads"),
        ("#8B5CF6", "02", "Topological Graph Healing",
         "MST bridging + extended-line projection closes gaps"),
        ("#F59E0B", "03", "Multi-metric Criticality Scoring",
         "Gatekeeper Score = Betweenness + Closeness + Bridge detection"),
        ("#EF4444", "04", "Cascading Failure Simulation",
         "Resilience Index quantifies systemic vulnerability"),
    ]
    for color, num, title, desc in stages:
        st.markdown(f"""
        <div style='display:flex; gap:1rem; align-items:flex-start;
                    padding:0.8rem 0; border-bottom:1px solid rgba(14,165,233,0.08);'>
          <div style='font-family:Space Mono,monospace; font-size:1.1rem;
                      font-weight:700; color:{color}; min-width:2rem;'>{num}</div>
          <div>
            <div style='font-family:Space Grotesk,sans-serif; font-weight:600;
                        color:#E2E8F0; font-size:0.88rem;'>{title}</div>
            <div style='font-size:0.78rem; color:#475569; margin-top:0.2rem;'>{desc}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── How to use ────────────────────────────────────────────────
st.markdown("---")
with st.expander("📖  How to use this demo — read this first", expanded=False):
    st.markdown("""
    <div style='font-size:0.88rem; color:#94A3B8; line-height:1.9;'>
    <b style='color:#E2E8F0'>This demo is a live preview of the DRISHTI pipeline.</b>
    It uses real Bengaluru OSM road data and simulated segmentation outputs
    to showcase every stage of what we are building for the ISRO hackathon.<br><br>
    <b style='color:#0EA5E9'>Suggested walkthrough (takes ~3 minutes):</b><br>
    1. 👁️ <b>Occlusion Simulation</b> — adjust the occlusion slider and see how our model recovers roads<br>
    2. 🕸️ <b>Road Graph</b> — explore the real Bengaluru road network and toggle healing on/off<br>
    3. 🔥 <b>Criticality Heatmap</b> — click nodes to see their Gatekeeper Score and why they matter<br>
    4. ⚡ <b>Stress Test</b> — pick a flood scenario and watch the city's resilience collapse<br>
    5. 📄 <b>Methodology</b> — see the academic papers behind every technique<br><br>
    Every metric has an <b style='color:#0EA5E9'>ℹ info</b> tag — hover or click it for a plain-English explanation.
    </div>
    """, unsafe_allow_html=True)

# ── Tech stack ────────────────────────────────────────────────
st.markdown("### Tech stack")
badges = ["PathMamba", "CE-RoadNet", "P2CNet", "SAM-Road++",
          "clDice Loss", "OSMnx", "NetworkX", "Folium",
          "Streamlit", "PyTorch", "Sentinel-2", "Cartosat-3"]
st.markdown(
    " ".join(f'<span class="tech-badge">{b}</span>' for b in badges),
    unsafe_allow_html=True
)

st.markdown("""
<div style='margin-top:2rem; padding:1rem; background:rgba(14,165,233,0.04);
            border:1px solid rgba(14,165,233,0.1); border-radius:10px;
            font-size:0.78rem; color:#334155; text-align:center;'>
This demo uses real Bengaluru OSM data and simulated segmentation outputs.
The actual hackathon system will run a fully trained PathMamba + P2CNet model
on Cartosat-3 imagery provided by ISRO.
</div>
""", unsafe_allow_html=True)
