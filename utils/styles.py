import streamlit as st
import streamlit.components.v1 as components

DRISHTI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #020B18 !important;
    color: #E2E8F0 !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: #0A1628 !important;
    border-right: 1px solid rgba(14,165,233,0.15) !important;
}

[data-testid="stSidebar"] * { color: #CBD5E1 !important; }

/* Hide default Streamlit chrome */
#MainMenu, footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stHeader"] { visibility: visible !important; display: block !important; }
[data-testid="stSidebarCollapsedControl"] { display: flex !important; visibility: visible !important; opacity: 1 !important; }
[data-testid="stSidebarCollapsedControl"] button {
    color: #E2E8F0 !important;
    background: #0D1B2A !important;
    border: 1px solid rgba(14,165,233,0.2) !important;
    border-radius: 8px !important;
}

/* ── Typography ── */
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; }

.drishti-hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2.2rem, 5vw, 3.6rem);
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.1;
    background: linear-gradient(135deg, #E2E8F0 0%, #0EA5E9 50%, #38BDF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}

.drishti-tagline {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem;
    font-weight: 400;
    color: #64748B;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

.drishti-page-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #E2E8F0;
    margin-bottom: 0.1rem;
}

.drishti-page-caption {
    font-size: 0.88rem;
    color: #475569;
    margin-bottom: 1.5rem;
    font-style: italic;
}

/* ── Cards ── */
.d-card {
    background: #0D1B2A;
    border: 1px solid rgba(14,165,233,0.12);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.d-card:hover { border-color: rgba(14,165,233,0.35); }

.d-card-critical {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
}

.d-card-warning {
    background: rgba(245,158,11,0.06);
    border: 1px solid rgba(245,158,11,0.25);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
}

.d-card-safe {
    background: rgba(16,185,129,0.06);
    border: 1px solid rgba(16,185,129,0.25);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
}

/* ── Metric tiles ── */
.d-metric {
    background: #0D1B2A;
    border: 1px solid rgba(14,165,233,0.18);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.d-metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.9rem;
    font-weight: 700;
    color: #0EA5E9;
    line-height: 1;
}
.d-metric-label {
    font-size: 0.75rem;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.4rem;
}
.d-metric-delta {
    font-size: 0.8rem;
    color: #10B981;
    margin-top: 0.25rem;
}

/* ── Pipeline stepper ── */
.pipeline-bar {
    display: flex;
    align-items: center;
    gap: 0;
    background: #0D1B2A;
    border: 1px solid rgba(14,165,233,0.12);
    border-radius: 50px;
    padding: 0.4rem 0.6rem;
    margin-bottom: 1.8rem;
    overflow-x: auto;
}
.pipeline-step {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.3rem 0.75rem;
    border-radius: 50px;
    font-size: 0.78rem;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 500;
    color: #475569;
    white-space: nowrap;
    transition: all 0.2s;
}
.pipeline-step.active {
    background: rgba(14,165,233,0.15);
    color: #0EA5E9;
    border: 1px solid rgba(14,165,233,0.3);
}
.pipeline-step.done {
    color: #10B981;
}
.pipeline-arrow {
    color: #1E293B;
    font-size: 0.8rem;
    flex-shrink: 0;
    padding: 0 0.1rem;
}

/* ── Info tooltip ── */
.info-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: rgba(14,165,233,0.08);
    border: 1px solid rgba(14,165,233,0.2);
    border-radius: 50px;
    padding: 0.15rem 0.6rem;
    font-size: 0.72rem;
    color: #0EA5E9;
    cursor: help;
    margin-left: 0.4rem;
    vertical-align: middle;
}

/* ── Badges ── */
.tech-badge {
    display: inline-block;
    background: rgba(14,165,233,0.1);
    border: 1px solid rgba(14,165,233,0.25);
    color: #38BDF8;
    border-radius: 50px;
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    margin: 0.2rem;
}

.paper-badge {
    display: inline-block;
    background: rgba(139,92,246,0.1);
    border: 1px solid rgba(139,92,246,0.25);
    color: #A78BFA;
    border-radius: 6px;
    padding: 0.2rem 0.6rem;
    font-size: 0.72rem;
    margin: 0.15rem;
}

/* ── Legend items ── */
.legend-dot {
    display: inline-block;
    width: 12px; height: 12px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;
}

/* ── Section divider ── */
.d-divider {
    border: none;
    border-top: 1px solid rgba(14,165,233,0.1);
    margin: 1.5rem 0;
}

/* ── Scan line animation (home page signature) ── */
.scan-container {
    position: relative;
    overflow: hidden;
    border-radius: 12px;
}
.scan-line {
    position: absolute;
    left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #0EA5E9, transparent);
    animation: scan 3s linear infinite;
    z-index: 10;
    box-shadow: 0 0 8px #0EA5E9;
}
@keyframes scan {
    0%  { top: 0%; opacity: 0; }
    5%  { opacity: 1; }
    95% { opacity: 1; }
    100%{ top: 100%; opacity: 0; }
}

/* ── Sidebar nav ── */
.sidebar-logo {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #0EA5E9 !important;
    letter-spacing: -0.01em;
    padding: 0.5rem 0 1rem;
}
.sidebar-sub {
    font-size: 0.7rem;
    color: #334155 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 1rem;
}

/* ── Streamlit widget overrides ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stSlider"] { color: #E2E8F0 !important; }

div[data-baseweb="select"] {
    background: #0D1B2A !important;
    border-color: rgba(14,165,233,0.3) !important;
}

[data-testid="stExpander"] {
    background: #0D1B2A !important;
    border: 1px solid rgba(14,165,233,0.12) !important;
    border-radius: 10px !important;
}

/* Progress bar color */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #0EA5E9, #38BDF8) !important;
}

/* Metric overrides */
[data-testid="stMetricValue"] {
    font-family: 'Space Mono', monospace !important;
    color: #0EA5E9 !important;
}

/* Button */
[data-testid="stButton"] button {
    background: linear-gradient(135deg, #0EA5E9, #0284C7) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: opacity 0.2s !important;
}
[data-testid="stButton"] button:hover { opacity: 0.85 !important; }
</style>
"""

def render_sidebar_toggle():
    """Render a fallback button to reopen the collapsed sidebar."""
    if st.button("☰ Show sidebar", key="sidebar_toggle_fallback", use_container_width=False):
        st.session_state["sidebar_toggle_requested"] = True

    if st.session_state.get("sidebar_toggle_requested", False):
        components.html(
            """
            <script>
            function openSidebar() {
                const sidebarControl = document.querySelector('[data-testid="stSidebarCollapsedControl"]');
                if (sidebarControl) {
                    sidebarControl.click();
                    return;
                }
                const buttons = Array.from(document.querySelectorAll('button'));
                const fallback = buttons.find((button) => {
                    const label = (button.getAttribute('aria-label') || '').toLowerCase();
                    const title = (button.title || '').toLowerCase();
                    return label.includes('sidebar') || title.includes('sidebar');
                });
                if (fallback) {
                    fallback.click();
                }
            }
            setTimeout(openSidebar, 120);
            </script>
            """,
            height=0,
        )
        st.session_state["sidebar_toggle_requested"] = False


def pipeline_bar(active_step: int):
    """Render pipeline progress stepper. active_step = 1..5"""
    steps = [
        ("🛰️", "Satellite Input"),
        ("👁️", "Occlusion Recovery"),
        ("🕸️", "Graph Healing"),
        ("🔥", "Criticality Map"),
        ("⚡", "Stress Test"),
    ]
    html = '<div class="pipeline-bar">'
    for i, (icon, label) in enumerate(steps, 1):
        cls = "active" if i == active_step else ("done" if i < active_step else "")
        prefix = "✓ " if i < active_step else ""
        html += f'<div class="pipeline-step {cls}">{icon} {prefix}{label}</div>'
        if i < len(steps):
            html += '<span class="pipeline-arrow">›</span>'
    html += "</div>"
    return html

def info_icon(tooltip: str) -> str:
    return f'<span class="info-pill" title="{tooltip}">ℹ info</span>'

def metric_card(value: str, label: str, delta: str = "", color: str = "#0EA5E9") -> str:
    delta_html = f'<div class="d-metric-delta">{delta}</div>' if delta else ""
    return f"""
    <div class="d-metric">
        <div class="d-metric-value" style="color:{color}">{value}</div>
        <div class="d-metric-label">{label}</div>
        {delta_html}
    </div>"""

def page_header(title: str, caption: str, active_step: int):
    import streamlit as st
    st.markdown(pipeline_bar(active_step), unsafe_allow_html=True)
    st.markdown(f'<div class="drishti-page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="drishti-page-caption">{caption}</div>', unsafe_allow_html=True)
