# =============================================================================
# PASO 2 DEL PIPELINE — ANÁLISIS DE REDES Y CIENCIA DE GRAFOS
# IED Intelligence Platform · México
# =============================================================================
# Construye la red bipartita País ↔ Estado ponderada por IED y aplica:
#   - Métricas de centralidad (grado, betweenness, eigenvector, closeness)
#   - Hub Score compuesto
#   - Detección de comunidades (Louvain)
#
# RUTAS: Este script está en IED/pipeline/
#   .parent.parent sube dos niveles → IED/
# =============================================================================

import pandas as pd
import numpy as np
import networkx as nx
import json
import pickle
from pathlib import Path
from community import community_louvain

# ── Rutas ────────────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent
PROC = BASE / "data" / "processed" / "proc_2"
PROC.mkdir(parents=True, exist_ok=True)

def _load(name):
    """Carga parquet si existe, sino cae en CSV con sufijo .csv"""
    p = PROC / name
    if p.exists():
        return pd.read_parquet(p)
    c = PROC / (name + ".csv")
    if c.exists():
        return pd.read_csv(c, low_memory=False)
    raise FileNotFoundError(f"No se encontró {name} ni {name}.csv en {PROC}")

def _save(df, name):
    """Guarda como parquet; si falla (sin pyarrow) guarda como CSV."""
    try:
        df.to_parquet(PROC / name, index=False)
    except Exception:
        df.to_csv(PROC / (name + ".csv"), index=False)

print("=" * 70)
print("PASO 2 — ANÁLISIS DE REDES Y COMUNIDADES")
print("=" * 70)

# ── Carga de datos ────────────────────────────────────────────────────────────
print("Cargando datos...")
df_cs       = _load("country_by_state.parquet")
df_states   = _load("investment_by_state.parquet")
df_countries= _load("investment_by_country.parquet")

# ── Red bipartita País ↔ Estado ───────────────────────────────────────────────
print("Construyendo red País ↔ Estado...")
edge_data = (
    df_cs[df_cs["IED"].notna() & (df_cs["IED"] > 0)]
    .groupby(["País_origen", "Estado"])["IED"].sum().reset_index()
)

top_countries_40 = (
    df_countries[df_countries["IED"].notna()]
    .groupby("Origen")["IED"].sum().nlargest(40).index.tolist()
)
edge_filtered = edge_data[edge_data["País_origen"].isin(top_countries_40)].copy()

G = nx.Graph()
for c in top_countries_40:
    total = df_countries[df_countries["Origen"] == c]["IED"].sum(skipna=True)
    G.add_node(c, node_type="country", total_ied=float(total) if pd.notna(total) else 0.0)

all_states = df_states["Entidad federativa"].unique().tolist()
for s in all_states:
    total = df_states[df_states["Entidad federativa"] == s]["IED"].sum()
    G.add_node(s, node_type="state", total_ied=float(total))

for _, row in edge_filtered.iterrows():
    if row["IED"] > 0:
        G.add_edge(row["País_origen"], row["Estado"], weight=float(row["IED"]))

print(f"  ✓ Red: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")

# ── Métricas de centralidad ───────────────────────────────────────────────────
print("Calculando métricas de centralidad...")
weighted_degree = dict(G.degree(weight="weight"))
betweenness     = nx.betweenness_centrality(G, weight="weight", normalized=True)
try:
    eigenvector = nx.eigenvector_centrality(G, weight="weight", max_iter=1000)
except Exception:
    eigenvector = {n: 0.0 for n in G.nodes()}
closeness = nx.closeness_centrality(G, distance="weight")

for node in G.nodes():
    G.nodes[node]["weighted_degree"] = weighted_degree.get(node, 0)
    G.nodes[node]["betweenness"]     = betweenness.get(node, 0)
    G.nodes[node]["eigenvector"]     = eigenvector.get(node, 0)
    G.nodes[node]["closeness"]       = closeness.get(node, 0)

# ── Comunidades (Louvain) ─────────────────────────────────────────────────────
print("Ejecutando Louvain...")
partition  = community_louvain.best_partition(G, weight="weight", random_state=42)
modularity = community_louvain.modularity(partition, G, weight="weight")
n_comm     = len(set(partition.values()))
for node, comm in partition.items():
    G.nodes[node]["community"] = comm
print(f"  ✓ {n_comm} comunidades, modularidad = {modularity:.4f}")

# ── DataFrame de nodos ────────────────────────────────────────────────────────
node_records = []
for node, data in G.nodes(data=True):
    node_records.append({
        "node":            node,
        "node_type":       data.get("node_type"),
        "total_ied":       data.get("total_ied", 0),
        "weighted_degree": data.get("weighted_degree", 0),
        "betweenness":     data.get("betweenness", 0),
        "eigenvector":     data.get("eigenvector", 0),
        "closeness":       data.get("closeness", 0),
        "community":       data.get("community", -1),
    })
df_nodes = pd.DataFrame(node_records)

# ── Hub Score (0-100) ─────────────────────────────────────────────────────────
print("Calculando Hub Score...")
for col in ["weighted_degree", "betweenness", "eigenvector", "closeness"]:
    mn, mx = df_nodes[col].min(), df_nodes[col].max()
    df_nodes[f"{col}_norm"] = (df_nodes[col] - mn) / (mx - mn + 1e-9)

df_nodes["hub_score"] = (
    0.35 * df_nodes["weighted_degree_norm"] +
    0.25 * df_nodes["betweenness_norm"]     +
    0.25 * df_nodes["eigenvector_norm"]     +
    0.15 * df_nodes["closeness_norm"]
)
df_nodes["hub_score"] = (df_nodes["hub_score"] * 100).round(2)
_save(df_nodes, "network_nodes.parquet")
print("  ✓ network_nodes guardado")

# ── DataFrame de aristas ──────────────────────────────────────────────────────
edge_records = [
    {"source": u, "target": v, "weight": d.get("weight", 0),
     "community_u": partition.get(u, -1), "community_v": partition.get(v, -1)}
    for u, v, d in G.edges(data=True)
]
df_edges = pd.DataFrame(edge_records)
_save(df_edges, "network_edges.parquet")
print("  ✓ network_edges guardado")

# ── Perfiles de comunidades ───────────────────────────────────────────────────
print("Perfiles de comunidades...")
community_profiles = {}
for comm_id in sorted(set(partition.values())):
    members      = [n for n, c in partition.items() if c == comm_id]
    countries_in = [n for n in members if G.nodes[n].get("node_type") == "country"]
    states_in    = [n for n in members if G.nodes[n].get("node_type") == "state"]
    internal     = [(u, v, d["weight"]) for u, v, d in G.edges(data=True)
                    if partition.get(u) == comm_id and partition.get(v) == comm_id]
    community_profiles[comm_id] = {
        "id": comm_id, "countries": countries_in, "states": states_in,
        "n_members": len(members),
        "total_ied_internal": round(sum(w for _, _, w in internal), 2),
        "top_country": sorted(countries_in, key=lambda c: G.nodes[c].get("total_ied", 0), reverse=True)[:3],
        "top_state":   sorted(states_in,    key=lambda s: G.nodes[s].get("total_ied", 0), reverse=True)[:3],
    }

with open(PROC / "community_profiles.json", "w", encoding="utf-8") as f:
    json.dump(community_profiles, f, ensure_ascii=False, indent=2)

with open(PROC / "main_graph.pkl", "wb") as f:
    pickle.dump(G, f)

graph_stats = {
    "n_nodes": G.number_of_nodes(), "n_edges": G.number_of_edges(),
    "n_communities": n_comm, "modularity": round(modularity, 4),
    "density": round(nx.density(G), 4),
    "top_state_hubs":   df_nodes[df_nodes["node_type"]=="state"].nlargest(5,"hub_score")[["node","hub_score"]].to_dict("records"),
    "top_country_hubs": df_nodes[df_nodes["node_type"]=="country"].nlargest(5,"hub_score")[["node","hub_score"]].to_dict("records"),
}
# encoding="utf-8" es obligatorio en Windows para que los acentos
# (nombres de estados/países) se guarden correctamente y puedan
# ser leídos luego por la app con json.load(..., encoding="utf-8")
with open(PROC / "graph_stats.json", "w", encoding="utf-8") as f:
    json.dump(graph_stats, f, ensure_ascii=False, indent=2)

print("\n" + "="*70); print("PASO 2 COMPLETADO")
print("="*70)
print(json.dumps(graph_stats, indent=2, ensure_ascii=False))
print("\nSiguiente paso: python pipeline/03_economic_scoring.py")
