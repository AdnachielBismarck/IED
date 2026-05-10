# =============================================================================
# PASO 4 DEL PIPELINE — CLUSTERING ESTRUCTURAL DE ESTADOS
# IED Intelligence Platform · México
# =============================================================================
# Agrupa los 32 estados en 4 tipologías económicas usando KMeans.
# RUTAS: IED/pipeline/ → .parent.parent = IED/
# =============================================================================

import pandas as pd
import numpy as np
import json
import warnings
from pathlib import Path
warnings.filterwarnings("ignore")

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score

BASE = Path(__file__).resolve().parent.parent
PROC = BASE / "data" / "processed" / "proc_2"

def _load(name):
    p = PROC / name
    if p.exists():
        return pd.read_parquet(p)
    c = PROC / (name + ".csv")
    if c.exists():
        return pd.read_csv(c, low_memory=False)
    raise FileNotFoundError(f"{name} no encontrado en {PROC}")

def _save(df, name):
    try:
        df.to_parquet(PROC / name, index=False)
    except Exception:
        df.to_csv(PROC / (name + ".csv"), index=False)

print("="*70); print("PASO 4 — CLUSTERING ESTRUCTURAL DE ESTADOS"); print("="*70)

print("Cargando datos...")
df_scores = _load("state_scores.parquet")
df_nodes  = _load("network_nodes.parquet")
df_states = _load("investment_by_state.parquet")
df_cs_raw = _load("country_by_state.parquet")

print("Construyendo features...")
state_nodes = df_nodes[df_nodes["node_type"]=="state"][["node","hub_score","betweenness","community"]].rename(columns={"node":"estado"})
df_feat = df_scores.merge(state_nodes, on="estado", how="left")

# IED total histórico (mean_ied ya viene de state_scores)
annual = df_states.groupby("Entidad federativa")["IED"].agg(total_ied_alltime="sum").reset_index().rename(columns={"Entidad federativa":"estado"})
df_feat = df_feat.merge(annual, on="estado", how="left")

country_diversity = (
    df_cs_raw[df_cs_raw["IED"].notna() & (df_cs_raw["IED"] > 0)]
    .groupby("Estado")["País_origen"].nunique()
    .reset_index().rename(columns={"Estado":"estado","País_origen":"n_investing_countries"})
)
df_feat = df_feat.merge(country_diversity, on="estado", how="left")

feature_cols = ["dependency_score","diversification_score","observability_risk","stability_index","nearshoring_score","hub_score","betweenness","n_active_countries","n_investing_countries","mean_ied"]
df_feat_clean = df_feat[["estado"] + feature_cols].copy()
X_raw = df_feat_clean[feature_cols].values

imputer  = SimpleImputer(strategy="median")
X_imputed= imputer.fit_transform(X_raw)
scaler   = StandardScaler()
X_scaled = scaler.fit_transform(X_imputed)

pca      = PCA(n_components=2, random_state=42)
X_pca    = pca.fit_transform(X_scaled)
explained= pca.explained_variance_ratio_
print(f"  PCA varianza explicada: {explained[0]:.1%} + {explained[1]:.1%} = {sum(explained):.1%}")

print("Ejecutando KMeans (k=4)...")
FORCED_K = 4
km     = KMeans(n_clusters=FORCED_K, random_state=42, n_init=20)
labels = km.fit_predict(X_scaled)
probs  = np.ones(len(labels))
sil    = silhouette_score(X_scaled, labels)
print(f"  ✓ {FORCED_K} clusters | Silhouette = {sil:.3f}")

df_feat_clean = df_feat_clean.copy()
df_feat_clean["cluster_id"]   = labels
df_feat_clean["cluster_prob"] = probs
df_feat_clean["pca_x"]        = X_pca[:, 0]
df_feat_clean["pca_y"]        = X_pca[:, 1]

global_means = {c: float(np.nanmean(df_feat_clean[c])) for c in feature_cols}

cluster_names = {}
cluster_descriptions = {}

for cid in sorted(set(labels)):
    subset    = df_feat_clean[df_feat_clean["cluster_id"] == cid]
    mean_vals = subset[feature_cols].mean()
    high_ns  = mean_vals["nearshoring_score"]     > global_means["nearshoring_score"]     * 1.15
    high_dep = mean_vals["dependency_score"]       > global_means["dependency_score"]      * 1.10
    low_dep  = mean_vals["dependency_score"]       < global_means["dependency_score"]      * 0.90
    high_hub = mean_vals["hub_score"]              > global_means["hub_score"]             * 1.20
    high_div = mean_vals["diversification_score"]  > global_means["diversification_score"] * 1.10
    low_div  = mean_vals["diversification_score"]  < global_means["diversification_score"] * 0.90
    low_sta  = mean_vals["stability_index"]        < global_means["stability_index"]       * 0.90

    if high_hub and high_div:
        name = "Hubs Diversificados"
        desc = "Alta conectividad en red, diversificación elevada. Economías con amplia base inversora."
    elif high_ns and high_hub:
        name = "Frontera Manufacturera"
        desc = "Fuerte señal nearshoring + alta centralidad. Motores del dinamismo post-2021."
    elif high_ns and not high_hub:
        name = "Emergentes Nearshoring"
        desc = "Aceleración reciente de IED. En transición hacia hub manufacturero."
    elif high_dep and low_div:
        name = "Concentrados Vulnerables"
        desc = "Alta dependencia de un país. Baja diversificación. Riesgo ante shocks externos."
    elif low_dep and high_div:
        name = "Diversificados Resilientes"
        desc = "Baja concentración, múltiples fuentes inversoras. Perfil de resiliencia estructural."
    elif low_sta:
        name = "Alta Volatilidad"
        desc = "Flujos de IED inestables. Reflejan ciclos económicos locales o reinversión irregular."
    elif mean_vals["mean_ied"] < global_means["mean_ied"] * 0.5:
        name = "Economías IED Marginal"
        desc = "Bajo volumen histórico de IED. Menor inserción en red internacional de inversión."
    else:
        diffs   = {c: (mean_vals[c] - global_means[c]) / (global_means[c] + 1e-6) for c in feature_cols if global_means[c] > 0}
        top_feat= max(diffs, key=lambda k: abs(diffs[k]))
        feat_labels = {"nearshoring_score":"Nearshoring Activo","dependency_score":"Alta Dependencia","diversification_score":"Alta Diversificación","stability_index":"Alta Estabilidad","hub_score":"Hub Emergente","n_investing_countries":"Amplia Base Inversora"}
        name = feat_labels.get(top_feat, f"Perfil Mixto {cid+1}")
        desc = f"Cluster diferenciado principalmente por {top_feat.replace('_',' ')}."

    cluster_names[cid]        = name
    cluster_descriptions[cid] = desc

df_feat_clean["cluster_name"] = df_feat_clean["cluster_id"].map(cluster_names)
df_feat_clean["cluster_desc"] = df_feat_clean["cluster_id"].map(cluster_descriptions)
_save(df_feat_clean, "state_clusters.parquet")
print("  ✓ state_clusters guardado")

cluster_summary = []
for cid in sorted(set(labels)):
    subset    = df_feat_clean[df_feat_clean["cluster_id"] == cid]
    mean_vals = subset[feature_cols].mean()
    cluster_summary.append({
        "cluster_id": int(cid), "cluster_name": cluster_names[cid],
        "cluster_description": cluster_descriptions[cid],
        "n_states": len(subset), "states": subset["estado"].tolist(),
        "mean_dependency":      round(float(mean_vals["dependency_score"]), 1),
        "mean_diversification": round(float(mean_vals["diversification_score"]), 1),
        "mean_nearshoring":     round(float(mean_vals["nearshoring_score"]), 1),
        "mean_stability":       round(float(mean_vals["stability_index"]), 1),
        "mean_hub_score":       round(float(mean_vals["hub_score"]), 1),
    })

with open(PROC / "cluster_summary.json", "w", encoding="utf-8") as f:
    json.dump(cluster_summary, f, ensure_ascii=False, indent=2)
print("  ✓ cluster_summary.json guardado")

print("\n" + "="*70); print("PASO 4 COMPLETADO"); print("="*70)
for cs in cluster_summary:
    print(f"  [{cs['cluster_id']}] {cs['cluster_name']:<30} — {cs['n_states']} estados")
    print(f"       {', '.join(cs['states'])}")
    print()
print("Siguiente paso: streamlit run app/main.py")
