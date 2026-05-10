# =============================================================================
# GENERADOR DE REPORTE PDF EJECUTIVO — IED Intelligence Platform
# =============================================================================
# Uso (desde raíz IED/):
#   python reports/generate_pdf.py
# Genera: reports/IED_Intelligence_Report_Mexico.pdf
#
# RUTAS: IED/reports/ → .parent.parent = IED/
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import sys
from pathlib import Path

BASE  = Path(__file__).resolve().parent.parent
PROC  = BASE / "data" / "processed" / "proc_2"
IMG   = BASE / "reports" / "img"
OUT   = BASE / "reports"
IMG.mkdir(parents=True, exist_ok=True)

def _load(name):
    p = PROC / name
    if p.exists(): return pd.read_parquet(p)
    c = PROC / (name + ".csv")
    if c.exists(): return pd.read_csv(c, low_memory=False)
    raise FileNotFoundError(f"{name} no encontrado en {PROC}")

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, HRFlowable
    from reportlab.lib.colors import HexColor
except ImportError:
    print("ERROR: reportlab no instalado. Instalar con: pip install reportlab")
    sys.exit(1)

# Paleta de colores
DARK_BG   = HexColor("#0f1117"); BLUE_PRI = HexColor("#2563EB"); BLUE_LT = HexColor("#3B82F6")
BLUE_ACC  = HexColor("#93C5FD"); GREEN    = HexColor("#10B981"); ORANGE  = HexColor("#F59E0B")
RED       = HexColor("#EF4444"); GRAY_MID = HexColor("#475569"); GRAY_LT = HexColor("#CBD5E1")
WHITE     = HexColor("#FFFFFF"); OFF_WHITE= HexColor("#F8FAFC"); TEXT_MID= HexColor("#334155")
TEXT_DARK = HexColor("#0F172A")
W, H = A4

print("Cargando datos...")
try:
    states   = _load("investment_by_state.parquet")
    ctry     = _load("investment_by_country.parquet")
    types    = _load("investment_types.parquet")
    scores   = _load("state_scores.parquet")
    nodes    = _load("network_nodes.parquet")
    clusters = _load("state_clusters.parquet")
    cs_raw   = _load("country_by_state.parquet")
    with open(PROC / "graph_stats.json", encoding="utf-8") as f: graph_stats = json.load(f)
    with open(PROC / "cluster_summary.json", encoding="utf-8") as f: cluster_summary = json.load(f)
except FileNotFoundError as e:
    print(f"ERROR: {e}")
    print("Ejecuta primero: python pipeline/run_pipeline.py")
    sys.exit(1)

annual       = states.groupby("Year")["IED"].sum()
total_2024   = annual.get(2024, 0)
peak_year    = int(annual.idxmax())
peak_val     = float(annual.max())
recent_avg   = float(annual[annual.index >= 2021].mean())
pre_avg      = float(annual[annual.index.isin(range(2015,2020))].mean())
growth_pct   = (recent_avg - pre_avg) / abs(pre_avg) * 100 if pre_avg else 0
top_state    = scores.nlargest(1,"strategic_score")["estado"].values[0]
top_ns_state = scores.nlargest(1,"nearshoring_score")["estado"].values[0]
top_dep_state= scores.nlargest(1,"dependency_score")["estado"].values[0]
top_dep_ctry = scores.nlargest(1,"dependency_score")["top_country"].values[0]
top_dep_sh   = float(scores.nlargest(1,"dependency_score")["top_country_share"].values[0])
top_country  = ctry[ctry["IED"].notna()].groupby("Origen")["IED"].sum().idxmax()
top_c_share  = ctry[ctry["IED"].notna()].groupby("Origen")["IED"].sum().max() / ctry[ctry["IED"].notna()]["IED"].sum() * 100

# Matplotlib settings
plt.rcParams.update({"font.family":"DejaVu Sans","axes.facecolor":"white","figure.facecolor":"white",
                     "axes.spines.top":False,"axes.spines.right":False,"axes.edgecolor":"#CBD5E1"})
CHART_BLUE="#2563EB"; CHART_ORG="#F59E0B"; CHART_GRN="#10B981"; CHART_RED="#EF4444"
CHART_DARK="#0F172A"; CHART_MID="#334155"; CHART_GRAY="#475569"; CHART_LGRAY="#CBD5E1"

def save_fig(fig, name, dpi=150):
    path = IMG / f"{name}.png"
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path

print("Generando charts...")
annual_df = states.groupby("Year")["IED"].sum().reset_index()
fig, ax = plt.subplots(figsize=(10,3.8))
ax.bar(annual_df["Year"], annual_df["IED"], color=CHART_BLUE, alpha=0.75, width=0.7, zorder=2)
ax.plot(annual_df["Year"], annual_df["IED"].rolling(3).mean(), color=CHART_ORG, linewidth=2.2, zorder=3, label="Media móvil 3 años")
ax.axvspan(2020.5, 2024.5, alpha=0.06, color=CHART_BLUE, zorder=1)
ax.text(2022.5, annual_df["IED"].max()*0.92, "Nearshoring", fontsize=9, color=CHART_BLUE, ha="center", style="italic")
ax.set_xlabel("Año",fontsize=10); ax.set_ylabel("USD Millones",fontsize=10)
ax.set_title("IED Total México — Serie Anual 2006–2024",fontsize=12,fontweight="bold",color=CHART_DARK,pad=12)
ax.legend(fontsize=9); ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_:f"${x:,.0f}"))
ax.grid(axis="y",linestyle="--",alpha=0.4); fig.tight_layout()
chart1_path = save_fig(fig,"chart1_national")

state_recent = states[states["Year"].isin([2023,2024])].groupby("Entidad federativa")["IED"].sum().nlargest(12).sort_values()
fig, ax = plt.subplots(figsize=(9,4.5))
colors_bar = [CHART_BLUE if v>state_recent.median() else "#93C5FD" for v in state_recent.values]
bars = ax.barh(state_recent.index, state_recent.values, color=colors_bar, height=0.65)
for bar,val in zip(bars,state_recent.values): ax.text(val+state_recent.max()*0.01,bar.get_y()+bar.get_height()/2,f"${val:,.0f}M",va="center",fontsize=8,color=CHART_MID)
ax.set_xlabel("USD M (2023-2024)",fontsize=10); ax.set_title("Top 12 Estados por IED — 2023-2024",fontsize=12,fontweight="bold",color=CHART_DARK,pad=12)
ax.set_xlim(0,state_recent.max()*1.18); ax.grid(axis="x",linestyle="--",alpha=0.4); fig.tight_layout()
chart2_path = save_fig(fig,"chart2_states")

top_c2 = ctry[ctry["IED"].notna()].groupby("Origen")["IED"].sum().nlargest(8)
other = ctry[ctry["IED"].notna()]["IED"].sum() - top_c2.sum()
if other > 0: top_c2["Otros"] = other
pie_colors=[CHART_BLUE,"#3B82F6","#60A5FA","#93C5FD","#BFDBFE",CHART_ORG,CHART_GRN,CHART_RED,"#64748B"]
fig, ax = plt.subplots(figsize=(7,4))
wedges,texts,autotexts = ax.pie(top_c2.values,labels=None,autopct="%1.1f%%",colors=pie_colors[:len(top_c2)],startangle=140,pctdistance=0.75,wedgeprops=dict(linewidth=1.5,edgecolor="white"))
for at in autotexts: at.set_fontsize(8)
ax.legend(top_c2.index,loc="center left",bbox_to_anchor=(1,0.5),fontsize=8.5,frameon=False)
ax.set_title("Participación por País de Origen\n(IED Acumulada)",fontsize=11,fontweight="bold",color=CHART_DARK,pad=10)
fig.tight_layout(); chart3_path = save_fig(fig,"chart3_countries")

sc_cols=["dependency_score","diversification_score","stability_index","nearshoring_score","strategic_score"]
lb_hm=["Dependencia","Diversificación","Estabilidad","Nearshoring","Score\nEstratégico"]
hm = scores.set_index("estado")[sc_cols].sort_values("strategic_score",ascending=False).head(18)
fig, ax = plt.subplots(figsize=(9,5.5))
im = ax.imshow(hm.values,aspect="auto",cmap="RdYlGn",vmin=0,vmax=100)
ax.set_xticks(range(len(lb_hm))); ax.set_xticklabels(lb_hm,fontsize=9,fontweight="bold")
ax.set_yticks(range(len(hm))); ax.set_yticklabels(hm.index,fontsize=8.5)
ax.xaxis.set_ticks_position("top"); ax.xaxis.set_label_position("top")
for i in range(len(hm)):
    for j in range(len(sc_cols)):
        val=hm.values[i,j]; color="white" if val<30 or val>70 else CHART_DARK
        ax.text(j,i,f"{val:.0f}",ha="center",va="center",fontsize=7.5,color=color,fontweight="bold")
plt.colorbar(im,ax=ax,shrink=0.8,label="Score (0-100)")
ax.set_title("Indicadores Estructurales — Top 18 Estados",fontsize=12,fontweight="bold",color=CHART_DARK,pad=30)
fig.tight_layout(); chart4_path = save_fig(fig,"chart4_heatmap")

ns = scores.sort_values("nearshoring_score",ascending=True).tail(14)
zone_c={"frontera":CHART_ORG,"bajio":CHART_BLUE,"centro/sur":"#94A3B8"}
fig, ax = plt.subplots(figsize=(9,4.2))
bars = ax.barh(ns["estado"], ns["nearshoring_score"], color=[zone_c.get(z,"#94A3B8") for z in ns["zone"]], height=0.65)
for bar,val in zip(bars,ns["nearshoring_score"]): ax.text(val+0.5,bar.get_y()+bar.get_height()/2,f"{val:.1f}",va="center",fontsize=8,color=CHART_MID)
ax.set_xlabel("Nearshoring Score",fontsize=10); ax.set_title("Señal Nearshoring por Estado (Top 14)",fontsize=12,fontweight="bold",color=CHART_DARK,pad=12)
patches=[mpatches.Patch(color=CHART_ORG,label="Frontera Norte"),mpatches.Patch(color=CHART_BLUE,label="Bajío"),mpatches.Patch(color="#94A3B8",label="Centro/Sur")]
ax.legend(handles=patches,fontsize=8.5,frameon=False,loc="lower right"); ax.grid(axis="x",linestyle="--",alpha=0.4); ax.set_xlim(0,ns["nearshoring_score"].max()*1.15)
fig.tight_layout(); chart5_path = save_fig(fig,"chart5_nearshoring")

sc2 = scores.dropna(subset=["dependency_score","diversification_score"])
fig, ax = plt.subplots(figsize=(9,5.5))
scatter = ax.scatter(sc2["dependency_score"],sc2["diversification_score"],c=sc2["nearshoring_score"].fillna(0),cmap="Blues",s=sc2["strategic_score"].fillna(20)*3,alpha=0.8,edgecolors=CHART_BLUE,linewidth=0.8,vmin=0,vmax=60,zorder=3)
for _,row in sc2.iterrows(): ax.annotate(row["estado"],(row["dependency_score"],row["diversification_score"]),fontsize=6.5,ha="center",va="bottom",color=CHART_MID,xytext=(0,4),textcoords="offset points")
ax.axhline(sc2["diversification_score"].median(),color=CHART_LGRAY,linestyle="--",alpha=0.7,zorder=2)
ax.axvline(sc2["dependency_score"].median(),color=CHART_LGRAY,linestyle="--",alpha=0.7,zorder=2)
ax.text(5,95,"✓ Diversificado\nBaja dep.",fontsize=8,color=CHART_GRN,alpha=0.7)
ax.text(65,95,"⚠ Diversificado\nAlta dep.",fontsize=8,color=CHART_ORG,alpha=0.7)
ax.text(65,5,"✗ Concentrado\nAlta dep.",fontsize=8,color=CHART_RED,alpha=0.7)
ax.text(5,5,"~ Concentrado\nBaja dep.",fontsize=8,color=CHART_GRAY,alpha=0.7)
plt.colorbar(scatter,ax=ax,label="Nearshoring Score",shrink=0.8)
ax.set_xlabel("Índice de Dependencia",fontsize=10); ax.set_ylabel("Índice de Diversificación",fontsize=10)
ax.set_title("Matriz Estratégica",fontsize=11,fontweight="bold",color=CHART_DARK,pad=12)
ax.set_xlim(-5,100); ax.set_ylim(-5,105); ax.grid(linestyle="--",alpha=0.3,zorder=0); fig.tight_layout()
chart6_path = save_fig(fig,"chart6_matrix")
print("  ✓ 6 charts generados")

# Build PDF
print("Construyendo PDF...")
OUTPUT_PDF = OUT / "IED_Intelligence_Report_Mexico.pdf"
doc = SimpleDocTemplate(str(OUTPUT_PDF),pagesize=A4,leftMargin=2*cm,rightMargin=2*cm,topMargin=1.5*cm,bottomMargin=1.5*cm)
styles = getSampleStyleSheet()

def S(name, **kw): return ParagraphStyle(name, **kw)
sH1   = S("sH1",   fontSize=18,textColor=BLUE_PRI,fontName="Helvetica-Bold",spaceBefore=18,spaceAfter=8,leading=22)
sH2   = S("sH2",   fontSize=13,textColor=TEXT_DARK,fontName="Helvetica-Bold",spaceBefore=12,spaceAfter=5,leading=17)
sBody = S("sBody", fontSize=9.5,textColor=TEXT_MID,fontName="Helvetica",leading=15,spaceAfter=6,alignment=TA_JUSTIFY)
sCap  = S("sCap",  fontSize=8,textColor=GRAY_MID,fontName="Helvetica-Oblique",alignment=TA_CENTER,spaceAfter=8)
sMetric = S("sMetric",fontSize=20,textColor=BLUE_PRI,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=24)
sMetricL= S("sMetricL",fontSize=8,textColor=GRAY_MID,fontName="Helvetica",alignment=TA_CENTER,leading=11)

story = []

# Cover
cover_rows = [
    Paragraph("REPORTE EJECUTIVO", S("ce",fontSize=9,textColor=BLUE_ACC,fontName="Helvetica-Bold")),
    Spacer(1,0.4*cm),
    Paragraph("IED Intelligence<br/>Platform", S("ct",fontSize=28,textColor=WHITE,fontName="Helvetica-Bold",alignment=TA_LEFT,leading=34)),
    Paragraph("México · Análisis Estructural de la<br/>Inversión Extranjera Directa", S("cs",fontSize=13,textColor=BLUE_ACC,fontName="Helvetica",alignment=TA_LEFT,leading=18)),
    Spacer(1,0.6*cm),
    HRFlowable(width="100%",thickness=1,color=BLUE_LT),
    Spacer(1,0.4*cm),
    Paragraph("Análisis de Redes · Clustering Estructural · Scoring Económico · Nearshoring", S("sa",fontSize=10,textColor=GRAY_LT,fontName="Helvetica",alignment=TA_LEFT)),
    Spacer(1,4*cm),
    Paragraph("Período: Q1 2006 — Q2 2025", S("sa2",fontSize=10,textColor=GRAY_LT,fontName="Helvetica")),
    Paragraph("Fuente: Secretaría de Economía · DGIE", S("sa3",fontSize=10,textColor=GRAY_LT,fontName="Helvetica")),
]
cover_table = Table([[r] for r in cover_rows], colWidths=[W-4*cm])
cover_table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),DARK_BG),("LEFTPADDING",(0,0),(-1,-1),28),("TOPPADDING",(0,0),(0,0),60),("BOTTOMPADDING",(0,-1),(-1,-1),30)]))
story.append(cover_table); story.append(PageBreak())

# Executive Summary
story.append(Paragraph("Executive Summary", sH1))
story.append(HRFlowable(width="100%",thickness=1.5,color=BLUE_PRI,spaceAfter=10))
story.append(Paragraph(f"Plataforma de inteligencia económica territorial para el análisis estructural de la IED en México (2006–2025). Procesa datos oficiales de la SE/DGIE en 8 dimensiones mediante análisis de redes, clustering e indicadores estructurales.", sBody))

km_data = [
    [Paragraph(f"${total_2024:,.0f}M",sMetric), Paragraph(f"{peak_year}",sMetric), Paragraph("152",sMetric), Paragraph(f"{graph_stats['n_communities']}",sMetric)],
    [Paragraph("IED 2024",sMetricL), Paragraph("Año pico",sMetricL), Paragraph("Países inversionistas",sMetricL), Paragraph("Comunidades económicas",sMetricL)],
]
km_t = Table(km_data,colWidths=[(W-4*cm)/4]*4)
km_t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),HexColor("#EFF6FF")),("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),8),("GRID",(0,0),(-1,-1),0.5,HexColor("#DBEAFE"))]))
story.append(Spacer(1,0.3*cm)); story.append(km_t); story.append(Spacer(1,0.4*cm)); story.append(PageBreak())

# Charts pages
for chart_path, title, caption, text in [
    (chart1_path, "Evolución Histórica de la IED", f"IED total México 2006–2024. Crecimiento post-COVID: {growth_pct:+.1f}% vs 2015-2019.", f"La IED en México alcanzó su pico histórico en {peak_year} (${peak_val:,.0f}M). El promedio 2021-2024 (${recent_avg:,.0f}M) supera al período pre-COVID en {growth_pct:.1f}%."),
    (chart2_path, "Distribución Territorial", "Top 12 estados por IED acumulada 2023-2024.", "La concentración geográfica muestra al norte industrial y CDMX como destinos dominantes."),
    (chart3_path, "Origen del Capital Extranjero", f"Participación por país. {top_country} domina con {top_c_share:.1f}% del total.", f"{top_country} aporta {top_c_share:.1f}% de la IED acumulada, reflejando integración T-MEC y riesgo de concentración."),
    (chart4_path, "Indicadores Estructurales", "Heatmap top 18 estados por Score Estratégico. Verde=favorable, rojo=desfavorable.", "Los estados muestran perfiles estructurales muy heterogéneos en las 5 dimensiones analizadas."),
    (chart5_path, "Señal Nearshoring", f"{top_ns_state} encabeza el índice con aceleración sostenida post-2021.", "La zona fronteriza norte y el Bajío concentran la señal de nearshoring más intensa."),
    (chart6_path, "Matriz Estratégica de Estados", "Posicionamiento estratégico de los 32 estados. Superior-izquierdo = perfil más resiliente.", "Los cuadrantes revelan grupos diferenciados que requieren estrategias de atracción distintas."),
]:
    story.append(Paragraph(title, sH1))
    story.append(HRFlowable(width="100%",thickness=1.5,color=BLUE_PRI,spaceAfter=10))
    story.append(Image(str(chart_path), width=W-4*cm, height=9*cm))
    story.append(Paragraph(f"Figura. {caption}", sCap))
    story.append(Paragraph(text, sBody))
    story.append(PageBreak())

# Conclusions
story.append(Paragraph("Conclusiones Estratégicas", sH1))
story.append(HRFlowable(width="100%",thickness=1.5,color=BLUE_PRI,spaceAfter=10))
for title, text in [
    ("México como plataforma de nearshoring", f"{top_ns_state} y la frontera norte lideran la aceleración post-2021, consistente con reconfiguración de cadenas de suministro globales."),
    ("Riesgo de concentración de capital", f"{top_country} representa {top_c_share:.0f}% del capital. Diversificar el origen es una prioridad estratégica de mediano plazo."),
    ("Heterogeneidad estructural entre estados", "Los 32 estados se agrupan en 4 tipologías económicas diferenciadas que requieren estrategias de atracción segmentadas."),
    ("Observabilidad parcial sistémica", "Los valores confidenciales son MNAR (no aleatorios). Los índices de concentración pueden estar subestimados en estados con alta confidencialidad."),
]:
    ct = Table([[Paragraph(f"<b>{title}</b><br/><font size='9' color='#475569'>{text}</font>",S("ct",fontSize=10,textColor=TEXT_DARK,fontName="Helvetica-Bold",leading=16))]], colWidths=[W-4*cm])
    ct.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),OFF_WHITE),("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),("LEFTPADDING",(0,0),(-1,-1),16),("LINEBEFORE",(0,0),(0,-1),3.5,BLUE_PRI)]))
    story.append(ct); story.append(Spacer(1,0.22*cm))

story.append(Spacer(1,0.8*cm))
story.append(HRFlowable(width="100%",thickness=0.5,color=HexColor("#CBD5E1")))
story.append(Spacer(1,0.3*cm))
story.append(Paragraph("IED Intelligence Platform · Secretaría de Economía · Período Q1 2006 — Q2 2025 · USD Millones corrientes", S("footer",fontSize=7.5,textColor=GRAY_MID,fontName="Helvetica",alignment=TA_CENTER)))

doc.build(story)
print(f"\n✅ PDF generado: {OUTPUT_PDF}")
