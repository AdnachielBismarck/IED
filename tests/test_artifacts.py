import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed" / "proc_2"


def load_parquet(name: str) -> pd.DataFrame:
    return pd.read_parquet(PROC / name)


def test_required_artifacts_exist():
    required = {
        "investment_by_state.parquet",
        "investment_by_country.parquet",
        "country_by_state.parquet",
        "network_nodes.parquet",
        "network_edges.parquet",
        "state_scores.parquet",
        "state_clusters.parquet",
        "graph_stats.json",
        "cluster_summary.json",
        "clustering_diagnostics.json",
        "metadata.json",
    }
    missing = sorted(name for name in required if not (PROC / name).exists())
    assert not missing, f"Faltan artefactos: {missing}"


def test_state_coverage_and_period_metadata():
    states = load_parquet("investment_by_state.parquet")
    assert states["Entidad federativa"].nunique() == 32
    assert states["Fecha"].notna().all()

    with open(PROC / "metadata.json", encoding="utf-8") as file:
        metadata = json.load(file)
    assert metadata["states"] == 32
    assert (
        metadata["period_end"] == pd.Timestamp(states["Fecha"].max()).date().isoformat()
    )


def test_score_ranges_and_unique_states():
    scores = load_parquet("state_scores.parquet")
    assert scores["estado"].is_unique
    assert len(scores) == 32
    score_columns = [
        "dependency_score",
        "diversification_score",
        "observability_risk",
        "stability_index",
        "nearshoring_score",
        "nearshoring_strategic_score",
        "strategic_score",
    ]
    for column in score_columns:
        values = scores[column].dropna()
        assert values.between(0, 100).all(), column


def test_network_uses_inverse_distance():
    edges = load_parquet("network_edges.parquet")
    assert (edges["weight"] > 0).all()
    expected = 1 / edges["weight"]
    assert (edges["distance"].sub(expected).abs() < 1e-12).all()


def test_cluster_solution_is_interpretable():
    clusters = load_parquet("state_clusters.parquet")
    counts = clusters.groupby("cluster_id")["estado"].count()
    assert counts.min() >= 3
    assert clusters["estado"].nunique() == 32

    with open(PROC / "clustering_diagnostics.json", encoding="utf-8") as file:
        diagnostics = json.load(file)
    assert diagnostics["selected_k"] == len(counts)
