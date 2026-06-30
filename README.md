# DRISHTI — Road Intelligence System
### ISRO Hackathon · Route Resilience Demo

## What this is
A 6-page Streamlit demo showcasing the DRISHTI pipeline for occlusion-robust
road extraction and graph-theoretic criticality analysis.

- Pages 1, 2, 6 — fully simulated/hardcoded visuals (no ML needed)
- Pages 3, 4, 5 — REAL Bengaluru OSM data + REAL NetworkX graph analysis
  (betweenness centrality, closeness centrality, articulation points,
  global efficiency, cascading failure simulation)

## How to run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501

## How to deploy (free, 5 minutes)

1. Push this folder to a public GitHub repo
2. Go to https://share.streamlit.io
3. Click "New app" → select your repo → main file path: `app.py`
4. Click Deploy
5. Copy the public URL (e.g. `https://yourname-drishti.streamlit.app`)
6. Paste that URL in your hackathon selection PPT

## Notes

- First load of pages 3/4/5 may take 10-20 seconds (live OSM data fetch).
  This is cached after first load — subsequent navigation is instant.
- If OSMnx fetch fails (rare, Nominatim server hiccup), just refresh —
  it retries automatically via Streamlit's cache.
- Tested with Python 3.11/3.12.

## File structure

```
drishti/
├── app.py                          # Home page
├── pages/
│   ├── 2_Occlusion_Simulation.py   # Synthetic occlusion recovery demo
│   ├── 3_Road_Graph.py             # Real Bengaluru graph + healing toggle
│   ├── 4_Criticality_Heatmap.py    # Real Gatekeeper Score on OSM data
│   ├── 5_Stress_Test.py            # Real cascading failure simulation
│   └── 6_Methodology.py            # Papers, sources, what's real vs simulated
├── utils/
│   ├── styles.py                   # Global CSS, pipeline stepper, cards
│   └── graph_utils.py              # Shared graph analysis functions
├── .streamlit/config.toml          # Dark theme config
└── requirements.txt
```

— Team DRISHTI
