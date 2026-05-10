import pandas as pd, numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW  = BASE / "data" / "processed" / "proc_1"
OUT  = BASE / "data" / "processed" / "proc_2"
OUT.mkdir(parents=True, exist_ok=True)

print("="*70); print("PASO 1 — PREPARACIÓN Y NORMALIZACIÓN DE DATOS"); print("="*70)

def parse_ied(s):
    return pd.to_numeric(s.replace("C", np.nan), errors="coerce")

def load_dates(df):
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Year"]  = df["Fecha"].dt.year
    df["Q"]     = df["Fecha"].dt.quarter
    df["YQ"]    = df["Year"].astype(str) + "Q" + df["Q"].astype(str)
    return df

def save_parquet(df, name):
    path = OUT / name
    df.to_csv(str(path).replace(".parquet",".csv.tmp"), index=False)
    # Use CSV as fallback when pyarrow unavailable
    import shutil
    shutil.move(str(path).replace(".parquet",".csv.tmp"), str(path).replace(".parquet",".parquet.csv"))
    return df

# Try parquet, fall back to CSV with .parquet extension marker
try:
    import pyarrow
    USE_PARQUET = True
except ImportError:
    USE_PARQUET = False

def save(df, name):
    if USE_PARQUET:
        df.to_parquet(OUT / name, index=False)
    else:
        df.to_csv(OUT / (name + ".csv"), index=False)
    return df

def load(name):
    if USE_PARQUET and (OUT / name).exists():
        return pd.read_parquet(OUT / name)
    csv_path = OUT / (name + ".csv")
    if csv_path.exists():
        return pd.read_csv(csv_path)
    raise FileNotFoundError(f"Neither {name} nor {name}.csv found in {OUT}")

print("1. Investment Types...")
df = pd.read_csv(RAW / "Investment_Types.csv")
df = load_dates(df)
df = df[df["Tipo de Inversión"] != "Total general"].copy()
df["IED"] = df["IED"].astype(float)
save(df, "investment_types.parquet"); print(f"   ✓ {len(df):,} filas")

print("2. Investment by State...")
df = pd.read_csv(RAW / "Investment_by_State.csv")
df = load_dates(df)
df = df[df["Entidad federativa"] != "Total general"].copy()
df["IED"] = df["IED"].astype(float)
save(df, "investment_by_state.parquet"); print(f"   ✓ {len(df):,} filas, {df['Entidad federativa'].nunique()} estados")

print("3. Origin of Investment...")
df = pd.read_csv(RAW / "Origin_of_Investment.csv")
df = load_dates(df)
df = df[df["Origen"] != "Total general"].copy()
df["is_confidential"] = df["IED"] == "C"
df["IED"] = parse_ied(df["IED"])
save(df, "investment_by_country.parquet"); print(f"   ✓ {len(df):,} filas, {df['Origen'].nunique()} países")
raw_origin = df.copy()

print("4. Country x State...")
df = pd.read_csv(RAW / "Investment_from_the_Countries_by_State.csv")
df = load_dates(df)
df.rename(columns={"Inversión por país en cada estado": "País_origen"}, inplace=True)
df = df[~df["País_origen"].isin(["Total general","Total general por estado"]) & ~df["Estado"].isin(["Total general"])].copy()
df["is_confidential"] = df["IED"] == "C"
df["IED"] = parse_ied(df["IED"])
save(df, "country_by_state.parquet"); print(f"   ✓ {len(df):,} filas")
df_cs = df.copy()

print("5. State x Country (alias)...")
save(df_cs.copy(), "state_by_country.parquet"); print(f"   ✓ {len(df_cs):,} filas")

print("6. Types x Country...")
df = pd.read_csv(RAW / "Investment_Types_by_Country.csv")
df = load_dates(df)
df = df[~df["Tipo de Inversión"].isin(["Total general","Total general por país"]) & ~df["País"].isin(["Total general"])].copy()
df["is_confidential"] = df["IED"] == "C"; df["IED"] = parse_ied(df["IED"])
save(df, "types_by_country.parquet"); print(f"   ✓ {len(df):,} filas")

print("7. Types x State...")
df = pd.read_csv(RAW / "Investment_Type_by_State.csv")
df = load_dates(df)
df = df[~df["Tipo de Inversión"].isin(["Total general","Total general por estado"]) & ~df["Estado"].isin(["Total general"])].copy()
df["is_confidential"] = df["IED"] == "C"; df["IED"] = parse_ied(df["IED"])
save(df, "types_by_state.parquet"); print(f"   ✓ {len(df):,} filas")

print("8. Sector (national)...")
df = pd.read_csv(RAW / "Investment_by_Sector.csv")
df = load_dates(df)
df = df[df["Nivel"] >= 2].copy()
df["is_confidential"] = df["IED"] == "C"; df["IED"] = parse_ied(df["IED"])
save(df, "investment_by_sector.parquet"); print(f"   ✓ {len(df):,} filas")

print("9. Sector x State...")
df = pd.read_csv(RAW / "Investment_by_Sector_from_the_States.csv")
df = load_dates(df)
df = df[~df["Concepto"].isin(["Total general","Total general por estado"])].copy()
for c in ["Nivel","Sector","Subsector","Rama"]: df[c] = pd.to_numeric(df[c], errors="coerce")
df["is_confidential"] = df["IED"] == "C"; df["IED"] = parse_ied(df["IED"])
save(df, "sector_by_state.parquet"); print(f"   ✓ {len(df):,} filas")

print("10. Sector x Country...")
df = pd.read_csv(RAW / "Investment_by_Sector_from_the_Countries.csv")
df = load_dates(df)
df = df[~df["Concepto"].isin(["Total general","Total general por país"])].copy()
for c in ["Nivel","Sector","Subsector","Rama"]: df[c] = pd.to_numeric(df[c], errors="coerce")
df["is_confidential"] = df["IED"] == "C"; df["IED"] = parse_ied(df["IED"])
save(df, "sector_by_country.parquet"); print(f"   ✓ {len(df):,} filas")

print("\nMatrices derivadas...")
df_states = load("investment_by_state.parquet")

cs_2024 = df_cs[df_cs["Year"] == 2024].copy()
matrix = cs_2024.groupby(["País_origen","Estado"])["IED"].sum().reset_index()
matrix = matrix[matrix["IED"].notna() & (matrix["IED"] != 0)]
top_c = (raw_origin[raw_origin["Year"] == 2024].groupby("Origen")["IED"].sum().nlargest(30).index.tolist())
top_s = (df_states[df_states["Year"] == 2024].groupby("Entidad federativa")["IED"].sum().nlargest(32).index.tolist())
mf = matrix[matrix["País_origen"].isin(top_c) & matrix["Estado"].isin(top_s)]
save(mf, "country_state_matrix_2024.parquet")
print(f"   ✓ matrix {mf['País_origen'].nunique()} países × {mf['Estado'].nunique()} estados")

annual = df_states.groupby(["Entidad federativa","Year"])["IED"].sum().reset_index()
save(annual, "annual_by_state.parquet"); print("   ✓ annual_by_state")

recent = df_cs[df_cs["Fecha"] >= "2023-01-01"].copy()
top_inv = (recent[recent["IED"].notna()].groupby(["Estado","País_origen"])["IED"].sum().reset_index().sort_values(["Estado","IED"],ascending=[True,False]))
save(top_inv, "top_investors_per_state.parquet"); print("   ✓ top_investors_per_state")

ct = (raw_origin[raw_origin["IED"].notna()].groupby("Origen")["IED"].sum().reset_index().rename(columns={"Origen":"País","IED":"IED_total"}).sort_values("IED_total",ascending=False))
save(ct, "country_totals.parquet"); print(f"   ✓ country_totals — {len(ct)} países")

print("\n" + "="*70); print("PASO 1 COMPLETADO"); print("="*70)
print("\nSiguiente paso: python pipeline/02_graph_analytics.py")
