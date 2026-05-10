# =============================================================================
# PASO 3 DEL PIPELINE — SCORING ECONÓMICO E INDICADORES ESTRUCTURALES
# IED Intelligence Platform · México
# =============================================================================
# Calcula 5 índices por estado + Score Estratégico compuesto.
# RUTAS: IED/pipeline/ → .parent.parent = IED/
# =============================================================================

import pandas as pd
import numpy as np
import json
from pathlib import Path

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

print("="*70); print("PASO 3 — SCORING ECONÓMICO E INDICADORES ESTRUCTURALES"); print("="*70)

print("Cargando datos...")
df_cs_raw  = _load("country_by_state.parquet")
df_states  = _load("investment_by_state.parquet")
df_types_s = _load("types_by_state.parquet")
df_sc_raw  = _load("state_by_country.parquet")

all_states = [s for s in df_states["Entidad federativa"].unique() if s not in ["Total general"]]
print(f"  {len(all_states)} estados")

def hhi(shares: np.ndarray) -> float:
    """HHI normalizado [0,1]. 0=diversificado, 1=concentrado."""
    s = shares[shares > 0]
    if len(s) == 0: return np.nan
    s = s / s.sum()
    raw = (s ** 2).sum()
    n = len(s)
    if n == 1: return 1.0
    return (raw - 1/n) / (1 - 1/n)

# ── 1. Dependency Score ───────────────────────────────────────────────────────
print("Calculando Dependency Score...")
dep_data = df_cs_raw[df_cs_raw["IED"].notna() & (df_cs_raw["IED"] > 0)].copy()
dep_scores = []
for state in all_states:
    sub = dep_data[dep_data["Estado"] == state]
    if len(sub) == 0:
        dep_scores.append({"estado": state, "dependency_score": np.nan, "top_country": None, "top_country_share": np.nan, "n_active_countries": 0}); continue
    by_country = sub.groupby("País_origen")["IED"].sum()
    total = by_country.sum()
    if total <= 0:
        dep_scores.append({"estado": state, "dependency_score": np.nan, "top_country": None, "top_country_share": np.nan, "n_active_countries": 0}); continue
    top_c   = by_country.idxmax()
    top_sh  = by_country.max() / total
    score   = hhi(by_country.values)
    dep_scores.append({"estado": state, "dependency_score": round(score*100,2), "top_country": top_c, "top_country_share": round(top_sh*100,2), "n_active_countries": int((by_country>0).sum())})
df_dep = pd.DataFrame(dep_scores)
print(f"  ✓ {len(df_dep)} estados")

# ── 2. Diversification Score ──────────────────────────────────────────────────
print("Calculando Diversification Score...")
excl_tipos = ["Total general","Total general por estado","Total general por tipo"]
type_data  = df_types_s[df_types_s["IED"].notna() & ~df_types_s["Tipo de Inversión"].isin(excl_tipos)].copy()
div_scores = []
for state in all_states:
    sub = type_data[type_data["Estado"] == state].sort_values("Fecha").tail(24)
    by_type = sub.groupby("Tipo de Inversión")["IED"].sum()
    by_type = by_type[by_type > 0]
    if len(by_type) == 0:
        div_scores.append({"estado": state, "diversification_score": np.nan, "dominant_type": None, "n_investment_types": 0}); continue
    score = 1 - hhi(by_type.values)
    div_scores.append({"estado": state, "diversification_score": round(score*100,2), "dominant_type": by_type.idxmax(), "n_investment_types": int(len(by_type))})
df_div = pd.DataFrame(div_scores)
print(f"  ✓ {len(df_div)} estados")

# ── 3. Observability Risk ─────────────────────────────────────────────────────
print("Calculando Observability Risk...")
obs_scores = []
for state in all_states:
    sub = df_sc_raw[df_sc_raw["Estado"] == state]
    if len(sub) == 0:
        obs_scores.append({"estado": state, "observability_risk": np.nan, "pct_confidential": np.nan}); continue
    n_total = len(sub)
    n_conf  = sub["is_confidential"].sum()
    pct     = (n_conf / n_total * 100) if n_total > 0 else 0
    obs_scores.append({"estado": state, "observability_risk": round(pct,2), "pct_confidential": round(pct,2), "n_total_records": n_total, "n_confidential_records": int(n_conf)})
df_obs = pd.DataFrame(obs_scores)
print(f"  ✓ {len(df_obs)} estados")

# ── 4. Stability Index ────────────────────────────────────────────────────────
print("Calculando Stability Index...")
stab_scores = []
for state in all_states:
    sub = df_states[df_states["Entidad federativa"] == state].sort_values("Fecha")
    ied_vals = sub["IED"].dropna().values
    if len(ied_vals) < 4:
        stab_scores.append({"estado": state, "stability_index": np.nan, "cv": np.nan}); continue
    mean_v = np.mean(ied_vals)
    std_v  = np.std(ied_vals)
    cv     = (std_v / abs(mean_v)) if abs(mean_v) > 1e-6 else 999
    stab_scores.append({"estado": state, "stability_index": round(100/(1+cv),2), "cv": round(cv,4), "mean_ied": round(mean_v,2), "std_ied": round(std_v,2)})
df_stab = pd.DataFrame(stab_scores)
print(f"  ✓ {len(df_stab)} estados")

# ── 5. Nearshoring Score ──────────────────────────────────────────────────────
print("Calculando Nearshoring Score...")
border_states = ["Baja California","Sonora","Chihuahua","Coahuila de Zaragoza","Nuevo León","Tamaulipas"]
bajio_states  = ["Guanajuato","Querétaro","San Luis Potosí","Aguascalientes","Jalisco","Michoacán de Ocampo"]
nearshoring_zone = {s: "frontera" for s in border_states}
nearshoring_zone.update({s: "bajio" for s in bajio_states})

ns_scores = []
for state in all_states:
    sub  = df_states[df_states["Entidad federativa"] == state].copy()
    pre  = sub[sub["Year"].between(2016, 2020)]["IED"].mean()
    post = sub[sub["Year"].between(2021, 2024)]["IED"].mean()
    growth_ratio = 0 if (pd.isna(pre) or pre == 0) else (post - pre) / abs(pre)
    us_data    = df_cs_raw[(df_cs_raw["Estado"] == state) & (df_cs_raw["País_origen"] == "Estados Unidos de América") & (df_cs_raw["IED"].notna())]
    state_total= df_cs_raw[(df_cs_raw["Estado"] == state) & (df_cs_raw["IED"].notna())]["IED"].sum()
    us_total   = us_data["IED"].sum()
    us_share   = us_total / state_total if state_total > 0 else 0
    recent_share = sub[sub["Year"] >= 2021]["IED"].sum() / (sub["IED"].sum() + 1e-6)
    geo_bonus  = 0.2 if state in border_states else (0.1 if state in bajio_states else 0)
    raw_score  = (0.35 * min(growth_ratio, 3) / 3 + 0.30 * min(us_share, 1) + 0.20 * min(recent_share, 1) + 0.15 * geo_bonus / 0.2)
    ns_scores.append({"estado": state, "nearshoring_score": round(raw_score*100,2), "growth_ratio_2021_24": round(growth_ratio*100,2), "us_share_pct": round(us_share*100,2), "zone": nearshoring_zone.get(state,"centro/sur")})
df_ns = pd.DataFrame(ns_scores)
print(f"  ✓ {len(df_ns)} estados")

# ── 6. Strategic Score ────────────────────────────────────────────────────────
print("Calculando Strategic Score...")
df_score = df_dep.merge(df_div, on="estado", how="outer")
df_score = df_score.merge(df_obs, on="estado", how="outer")
df_score = df_score.merge(df_stab[["estado","stability_index","cv","mean_ied","std_ied"]], on="estado", how="outer")
df_score = df_score.merge(df_ns[["estado","nearshoring_score","growth_ratio_2021_24","us_share_pct","zone"]], on="estado", how="outer")
df_score["strategic_score"] = (
    0.25 * df_score["diversification_score"].fillna(0) +
    0.20 * (100 - df_score["dependency_score"].fillna(50)) +
    0.20 * df_score["stability_index"].fillna(0) +
    0.20 * df_score["nearshoring_score"].fillna(0) +
    0.15 * (100 - df_score["observability_risk"].fillna(50))
).round(2)
_save(df_score, "state_scores.parquet")
print(f"  ✓ state_scores guardado — {len(df_score)} estados")

# ── Perfiles de países ────────────────────────────────────────────────────────
print("Perfiles de países...")
df_ct = _load("investment_by_country.parquet")
country_conc = []
for country in df_ct["Origen"].unique():
    sub = df_cs_raw[(df_cs_raw["País_origen"] == country) & (df_cs_raw["IED"].notna())]
    if len(sub) == 0: continue
    by_state = sub.groupby("Estado")["IED"].sum()
    pos = by_state[by_state > 0]
    if len(pos) == 0: continue
    h = hhi(pos.values)
    country_conc.append({"country": country, "concentration_hhi": round(h*100,2), "n_states_active": int((pos>0).sum()), "top_state": pos.idxmax(), "total_ied": round(pos.sum(),2)})
df_cp = pd.DataFrame(country_conc).sort_values("total_ied", ascending=False)
_save(df_cp, "country_profiles.parquet")
print(f"  ✓ country_profiles — {len(df_cp)} países")

print("\n" + "="*70); print("PASO 3 COMPLETADO"); print("="*70)
print("\nTop 5 por Strategic Score:")
print(df_score.nlargest(5,"strategic_score")[["estado","strategic_score","diversification_score","dependency_score","nearshoring_score"]].to_string(index=False))
print("\nTop 5 por Nearshoring:")
print(df_score.nlargest(5,"nearshoring_score")[["estado","nearshoring_score","zone","us_share_pct","growth_ratio_2021_24"]].to_string(index=False))
print("\nSiguiente paso: python pipeline/04_clustering.py")
