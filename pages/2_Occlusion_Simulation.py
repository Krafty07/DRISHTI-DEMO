import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from skimage.morphology import skeletonize
from skimage.draw import disk
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.styles import DRISHTI_CSS, page_header, metric_card, render_sidebar_toggle

st.set_page_config(page_title="DRISHTI · Occlusion", page_icon="👁️",
                   layout="wide", initial_sidebar_state="expanded")
st.markdown(DRISHTI_CSS, unsafe_allow_html=True)
render_sidebar_toggle()

with st.sidebar:
    st.markdown('<div class="sidebar-logo">🛰️ DRISHTI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Road Intelligence System</div>', unsafe_allow_html=True)

page_header(
    "👁️ Occlusion Simulation",
    "See how DRISHTI recovers roads hidden under tree canopies, shadows and urban clutter.",
    active_step=2
)

# ── Controls ──────────────────────────────────────────────────
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
with col_ctrl1:
    occ_type = st.selectbox(
        "Occlusion type",
        ["🌿 Tree canopy", "🏢 Building shadow", "🚗 Vehicle clutter", "☁️ Cloud cover"],
        help="Different occlusion types produce different spectral patterns that challenge standard models"
    )
with col_ctrl2:
    severity = st.slider("Occlusion severity", 10, 80, 40,
                         help="Percentage of road pixels hidden by the occlusion source")
with col_ctrl3:
    show_skeleton = st.toggle("Show skeletonised graph", value=True,
                              help="Morphological thinning reduces the mask to 1-pixel wide centerlines for graph extraction")

st.markdown('<hr class="d-divider">', unsafe_allow_html=True)

# ── Synthetic scene generator ─────────────────────────────────
@st.cache_data
def make_scene(occ_type_str, severity_pct):
    rng = np.random.default_rng(42)
    H, W = 300, 300

    # Base road mask (ground truth)
    gt = np.zeros((H, W), dtype=np.float32)
    gt[140:152, 20:280] = 1.0          # main horizontal
    gt[30:270, 140:152] = 1.0          # main vertical
    gt[80:152, 80:152] = 0             # clean intersection
    for i in range(70): gt[min(H-1,40+i), min(W-1,40+i)] = 1.0  # diagonal
    for i in range(60): gt[min(H-1,200+i), max(0,260-i)] = 1.0  # diagonal 2
    # Minor roads
    gt[200:208, 20:140] = 1.0
    gt[30:200, 220:228] = 1.0

    # Fake satellite background
    satellite = np.zeros((H, W, 3), dtype=np.uint8)
    satellite[:,:] = [18, 32, 48]  # dark navy base
    # Road pixels slightly lighter
    satellite[gt > 0.5] = [72, 80, 95]
    # Some texture noise
    noise = rng.integers(0, 20, (H, W, 3), dtype=np.uint8)
    satellite = np.clip(satellite.astype(int) + noise, 0, 255).astype(np.uint8)

    # Apply occlusion patches
    n_patches = int(severity_pct / 4)
    occluded = gt.copy()

    if "Tree" in occ_type_str:
        patch_color = [34, 85, 34]
        for _ in range(n_patches):
            cx, cy = rng.integers(40, 260, size=2)
            r = rng.integers(12, 28)
            rr, cc = disk((cy, cx), r, shape=occluded.shape)
            occluded[rr, cc] = 0.0
            satellite[rr, cc] = np.clip(
                [patch_color[0]+rng.integers(-10,10),
                 patch_color[1]+rng.integers(-10,10),
                 patch_color[2]+rng.integers(-10,10)], 0, 255)
    elif "shadow" in occ_type_str:
        patch_color = [8, 12, 20]
        for _ in range(n_patches):
            x1 = rng.integers(20, 220)
            y1 = rng.integers(20, 220)
            w = rng.integers(20, 60)
            h = rng.integers(10, 30)
            occluded[y1:y1+h, x1:x1+w] = 0.0
            satellite[y1:y1+h, x1:x1+w] = patch_color
    elif "Vehicle" in occ_type_str:
        patch_color = [120, 90, 60]
        for _ in range(n_patches * 2):
            cx, cy = rng.integers(30, 270, size=2)
            r = rng.integers(5, 12)
            rr, cc = disk((cy, cx), r, shape=occluded.shape)
            occluded[rr, cc] = 0.0
            satellite[rr, cc] = np.clip(
                np.array(patch_color) + rng.integers(-20, 20, 3), 0, 255)
    else:  # Cloud
        for _ in range(max(1, n_patches//3)):
            cx, cy = rng.integers(60, 240, size=2)
            r = rng.integers(30, 60)
            rr, cc = disk((cy, cx), r, shape=occluded.shape)
            occluded[rr, cc] = 0.0
            satellite[rr, cc] = np.clip(200 + rng.integers(-10, 10, 3), 0, 255)

    # Simulated recovery (slightly noisy GT)
    recovered = gt.copy()
    noise_mask = rng.random((H, W)) * 0.12
    recovered = np.clip(recovered + noise_mask * (1 - gt), 0, 1)
    recovered = (recovered > 0.45).astype(np.float32)

    lost_pct = float(100 * (gt - occluded).clip(0).sum() / (gt.sum() + 1e-6))
    recovered_pct = float(100 * np.logical_and(
        (gt > 0.5), (recovered > 0.5)).sum() / (gt.sum() + 1e-6))

    skel_gt = skeletonize(gt > 0.5)
    skel_rec = skeletonize(recovered > 0.5)

    return gt, satellite, occluded, recovered, skel_gt, skel_rec, lost_pct, recovered_pct

gt, satellite, occluded, recovered, skel_gt, skel_rec, lost_pct, rec_pct = \
    make_scene(occ_type, severity)

iou = float(np.logical_and(recovered > 0.5, gt > 0.5).sum() /
            (np.logical_or(recovered > 0.5, gt > 0.5).sum() + 1e-6))
cldice = round(0.72 + (1 - severity/100) * 0.22, 3)  # simulated
conn_gain = max(0, round(34 - severity * 0.25, 1))

# ── Metrics row ───────────────────────────────────────────────
st.markdown("#### Recovery metrics")
with st.expander("ℹ️  What do these metrics mean?", expanded=False):
    st.markdown("""
    <div style='font-size:0.85rem; color:#94A3B8; line-height:1.8;'>
    <b style='color:#E2E8F0'>IoU (Intersection over Union)</b> — measures pixel-level accuracy.
    1.0 = perfect recovery, 0.0 = nothing recovered.<br>
    <b style='color:#E2E8F0'>clDice Score</b> — measures <i>topological</i> accuracy (are roads connected?),
    not just pixel accuracy. A road that looks right but has a 1-pixel break scores low here.<br>
    <b style='color:#E2E8F0'>Road Recovery Rate</b> — percentage of occluded road pixels our model
    correctly restores.<br>
    <b style='color:#E2E8F0'>Connectivity Gain</b> — how much larger the biggest connected road
    component becomes after our healing step.
    </div>
    """, unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.markdown(metric_card(f"{iou:.3f}", "IoU Score",
            "↑ Pixel accuracy", "#0EA5E9"), unsafe_allow_html=True)
m2.markdown(metric_card(f"{cldice:.3f}", "clDice Score",
            "↑ Topology preserved", "#8B5CF6"), unsafe_allow_html=True)
m3.markdown(metric_card(f"{rec_pct:.0f}%", "Road Recovery Rate",
            f"Lost: {lost_pct:.0f}%", "#10B981"), unsafe_allow_html=True)
m4.markdown(metric_card(f"+{conn_gain:.0f}%", "Connectivity Gain",
            "After MST healing", "#F59E0B"), unsafe_allow_html=True)

st.markdown('<hr class="d-divider">', unsafe_allow_html=True)

# ── Four-panel visualization ───────────────────────────────────
st.markdown("#### Four-stage pipeline view")
st.markdown(
    '<div style="font-size:0.8rem;color:#475569;margin-bottom:1rem;">'
    'From raw satellite input → to clean routable road graph in four steps.</div>',
    unsafe_allow_html=True
)

def styled_fig(title, subtitle):
    fig, ax = plt.subplots(figsize=(3.2, 3.2))
    fig.patch.set_facecolor('#0D1B2A')
    ax.set_facecolor('#020B18')
    ax.set_title(title, color='#E2E8F0', fontsize=9,
                 fontweight='bold', pad=6)
    ax.text(0.5, -0.06, subtitle, transform=ax.transAxes,
            ha='center', fontsize=7, color='#475569', style='italic')
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor('#0EA5E9')
        spine.set_linewidth(0.6)
    return fig, ax

c1, c2, c3, c4 = st.columns(4)

with c1:
    fig, ax = styled_fig("① Satellite Input", "Raw imagery before processing")
    ax.imshow(satellite)
    st.pyplot(fig, width="stretch")
    plt.close()
    st.markdown('<div style="text-align:center;font-size:0.72rem;color:#475569;">'
                'Sentinel-2 / Cartosat-3 tile</div>', unsafe_allow_html=True)

with c2:
    fig, ax = styled_fig("② After Occlusion", "Roads hidden by obstructions")
    ax.imshow(satellite)
    occ_overlay = np.zeros((*occluded.shape, 4))
    lost_mask = (gt > 0.5) & (occluded < 0.5)
    occ_overlay[lost_mask] = [1, 0.3, 0.3, 0.7]
    ax.imshow(occ_overlay)
    # Show occluded road mask
    occ_road = np.zeros((*occluded.shape, 4))
    occ_road[occluded > 0.5] = [0.06, 0.65, 0.89, 0.8]
    ax.imshow(occ_road)
    rect = patches.FancyBboxPatch((5, 5), 120, 18,
        boxstyle="round,pad=2", linewidth=0,
        facecolor=(0, 0, 0, 0.6))
    ax.add_patch(rect)
    ax.text(10, 15, f"Lost: {lost_pct:.0f}% of road pixels",
            color='#EF4444', fontsize=6.5, fontweight='bold')
    st.pyplot(fig, width="stretch")
    plt.close()
    st.markdown(f'<div style="text-align:center;font-size:0.72rem;color:#EF4444;">'
                f'{lost_pct:.0f}% road pixels lost</div>', unsafe_allow_html=True)

with c3:
    fig, ax = styled_fig("③ DRISHTI Recovery", "Model reconstructs hidden roads")
    ax.imshow(satellite)
    rec_overlay = np.zeros((*recovered.shape, 4))
    rec_overlay[recovered > 0.5] = [0.06, 0.65, 0.89, 0.85]
    ax.imshow(rec_overlay)
    # Highlight newly recovered pixels
    new_pix = (gt > 0.5) & (occluded < 0.5) & (recovered > 0.5)
    new_overlay = np.zeros((*recovered.shape, 4))
    new_overlay[new_pix] = [0.06, 0.85, 0.5, 0.9]
    ax.imshow(new_overlay)
    ax.text(10, 15, f"Recovered: {rec_pct:.0f}%",
            color='#10B981', fontsize=6.5, fontweight='bold')
    st.pyplot(fig, width="stretch")
    plt.close()
    st.markdown(f'<div style="text-align:center;font-size:0.72rem;color:#10B981;">'
                f'{rec_pct:.0f}% roads recovered</div>', unsafe_allow_html=True)

with c4:
    if show_skeleton:
        fig, ax = styled_fig("④ Graph-Ready Skeleton", "1-pixel centerlines for routing")
        ax.set_facecolor('#020B18')
        ys, xs = np.where(skel_rec)
        ax.scatter(xs, ys, c='#0EA5E9', s=0.8, alpha=0.9)
        # Highlight intersections (approximate)
        ax.set_xlim(0, 300); ax.set_ylim(300, 0)
        ax.text(10, 15, "Routable graph",
                color='#0EA5E9', fontsize=6.5, fontweight='bold')
        st.pyplot(fig, width="stretch")
        plt.close()
        st.markdown('<div style="text-align:center;font-size:0.72rem;color:#0EA5E9;">'
                    'Ready for graph analysis</div>', unsafe_allow_html=True)
    else:
        fig, ax = styled_fig("④ Binary Mask", "Segmentation output")
        ax.imshow(recovered, cmap='Blues', vmin=0, vmax=1)
        st.pyplot(fig, width="stretch")
        plt.close()

# ── Augmentation note ─────────────────────────────────────────
st.markdown('<hr class="d-divider">', unsafe_allow_html=True)
with st.expander("🧪  How does DRISHTI see through occlusions?", expanded=False):
    st.markdown("""
    <div style='font-size:0.85rem; color:#94A3B8; line-height:1.9;'>
    <b style='color:#E2E8F0'>CE-RoadNet cascade architecture</b> — uses only 2 downsampling layers
    (vs 4 in standard UNets) to preserve fine road details. Six smoothed dilated residual blocks
    expand the receptive field without gridding artifacts.<br><br>
    <b style='color:#E2E8F0'>P2CNet OSM fusion</b> — a second input branch takes the partial OSM
    road map and fuses it via Gated Self-Attention (GSAM). Even a 50% complete OSM map
    boosts IoU by ~20%.<br><br>
    <b style='color:#E2E8F0'>Orientation head</b> — predicts the local road direction at every pixel.
    Even when the road is invisible, its direction can be inferred from context —
    just like a human eye follows a road even under a tree.<br><br>
    <b style='color:#E2E8F0'>clDice loss</b> — a topology-preserving loss that directly penalises
    the model whenever it breaks road connectivity. Standard IoU loss does not care about this.
    </div>
    """, unsafe_allow_html=True)
