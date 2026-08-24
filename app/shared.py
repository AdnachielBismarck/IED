import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed" / "proc_2"


@st.cache_data
def load_metadata() -> dict:
    with open(PROC / "metadata.json", encoding="utf-8") as file:
        return json.load(file)


def apply_product_styles() -> None:
    st.markdown(
        """
        <style>
          [data-testid="stAppViewContainer"] > .main {
            background:
              radial-gradient(circle at 85% -10%, rgba(59,130,246,.10), transparent 26rem),
              #0b1220;
          }
          [data-testid="stMainBlockContainer"] {
            max-width: 1380px;
            padding-top: 2.1rem;
            padding-bottom: 3rem;
          }
          [data-testid="stSidebar"] {
            background: #0e1728 !important;
            border-right: 1px solid #22304a !important;
          }
          [data-testid="stSidebar"] [data-testid="stPageLink"] a {
            border-radius: 6px;
            padding: .46rem .65rem;
          }
          [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
            background: #17233a;
          }
          [data-testid="stMetric"] {
            background: #111c30;
            border: 1px solid #22304a;
            border-radius: 8px;
            padding: 1rem 1.1rem;
          }
          [data-testid="stMetricLabel"] { color: #94a3b8; }
          [data-testid="stMetricValue"] { color: #f8fafc; }
          [data-testid="stTabs"] button { font-weight: 500; }
          [data-testid="stDataFrame"] {
            border: 1px solid #22304a;
            border-radius: 8px;
            overflow: hidden;
          }
          .product-eyebrow {
            color: #60a5fa;
            font-size: .72rem;
            font-weight: 600;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin-bottom: .4rem;
          }
          .product-title {
            color: #f8fafc;
            font-size: clamp(1.65rem, 3vw, 2.35rem);
            font-weight: 600;
            letter-spacing: -.025em;
            line-height: 1.16;
            margin: 0;
            max-width: 980px;
          }
          .product-subtitle {
            color: #94a3b8;
            font-size: .96rem;
            line-height: 1.65;
            margin: .7rem 0 1.35rem;
            max-width: 920px;
          }
          .brand-mark {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2.3rem;
            height: 2.3rem;
            border: 1px solid #3b82f6;
            border-radius: 7px;
            color: #93c5fd;
            font: 600 .72rem 'IBM Plex Mono', monospace;
            letter-spacing: .06em;
            margin-bottom: .7rem;
          }
          .sidebar-product { color:#f8fafc; font-weight:600; font-size:1rem; margin:0; }
          .sidebar-period { color:#64748b; font-size:.74rem; margin:.2rem 0 1rem; }
          .section-label {
            color:#64748b;
            font-size:.67rem;
            font-weight:600;
            letter-spacing:.10em;
            text-transform:uppercase;
            margin:.9rem 0 .4rem;
          }
          .provenance-bar {
            border-top: 1px solid #22304a;
            color: #64748b;
            font-size: .72rem;
            line-height: 1.55;
            margin-top: 2rem;
            padding-top: .75rem;
          }
          .decision-note {
            background: linear-gradient(135deg, #111c30, #101a2b);
            border: 1px solid #29446f;
            border-left: 3px solid #3b82f6;
            border-radius: 8px;
            padding: 1rem 1.15rem;
            margin: .5rem 0 1.25rem;
          }
          .decision-note strong { color:#f8fafc; }
          .decision-note p { color:#a8b4c7; margin:.3rem 0 0; font-size:.86rem; line-height:1.55; }
          [data-testid="stAppDeployButton"] { display: none; }
          button[data-testid="stBaseButton-header"][aria-label=""] { display: none; }
          header[data-testid="stHeader"] { background: transparent; }
          #MainMenu, footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    metadata = load_metadata()
    with st.sidebar:
        st.markdown('<div class="brand-mark">IED</div>', unsafe_allow_html=True)
        st.markdown(
            '<p class="sidebar-product">IED Intelligence Platform</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="sidebar-period">México · {metadata["period_label"]}</p>',
            unsafe_allow_html=True,
        )
        st.markdown('<p class="section-label">Análisis</p>', unsafe_allow_html=True)
        st.page_link("main.py", label="Panorama nacional")
        st.page_link("pages/1_Network_Graph.py", label="Red de inversión")
        st.page_link("pages/2_Regional_Profiles.py", label="Perfiles estatales")
        st.page_link("pages/3_Risk_Analysis.py", label="Riesgo y dependencia")
        st.page_link("pages/4_Temporal_Dynamics.py", label="Dinámica temporal")
        st.markdown(
            '<p class="section-label">Transparencia</p>', unsafe_allow_html=True
        )
        st.page_link("pages/5_Methodology.py", label="Metodología")
        st.markdown(
            '<div class="provenance-bar">Fuente: Secretaría de Economía, DGIE<br>'
            "Millones de USD corrientes<br><br>Desarrollado por Adnachiel Avendaño</div>",
            unsafe_allow_html=True,
        )


def render_header(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="product-eyebrow">{eyebrow}</div>'
        f'<h1 class="product-title">{title}</h1>'
        f'<p class="product-subtitle">{subtitle}</p>',
        unsafe_allow_html=True,
    )


def render_provenance() -> None:
    metadata = load_metadata()
    st.markdown(
        f'<div class="provenance-bar">{metadata["source"]} · '
        f'{metadata["period_label"]} · {metadata["currency"]} · '
        "Indicadores de elaboración propia</div>",
        unsafe_allow_html=True,
    )
