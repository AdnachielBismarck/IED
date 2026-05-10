import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE / "data" / "raw"
PROCESSED_DATA_DIR = BASE / "data" / "processed" / "proc_1"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("PASO 0 — LIMPIEZA DE DATOS ORIGINALES")
print("=" * 70)
print(f"  Leyendo desde : {RAW_DATA_DIR}")
print(f"  Guardando en  : {PROCESSED_DATA_DIR}")
print()

ESTADOS = [
    "Aguascalientes", "Baja California", "Baja California Sur", "Campeche",
    "Chiapas", "Chihuahua", "Ciudad de México", "Coahuila de Zaragoza",
    "Colima", "Durango", "Estado de México", "Guanajuato", "Guerrero",
    "Hidalgo", "Jalisco", "Michoacán de Ocampo", "Morelos", "Nayarit",
    "Nuevo León", "Oaxaca", "Puebla", "Querétaro", "Quintana Roo",
    "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco", "Tamaulipas",
    "Tlaxcala", "Veracruz de Ignacio de la Llave", "Yucatán", "Zacatecas"
]

def limpiar_encabezados(df, n_drop_top, n_drop_bot, id_col):
    df = df.copy()
    df = df.iloc[n_drop_top:, :].reset_index(drop=True)
    df = df.iloc[:-n_drop_bot, :].reset_index(drop=True)
    df.iloc[0, 1:] = df.iloc[0, 1:].ffill()
    años       = df.iloc[0, 1:].astype(int).tolist()
    trimestres = df.iloc[1, 1:].astype(int).tolist()
    fechas = [f"{a}Q{t}" for a, t in zip(años, trimestres)]
    df.columns = [id_col] + fechas
    df = df.iloc[2:, :].reset_index(drop=True)
    return df

def a_formato_largo(df, id_vars, value_name="IED"):
    df_largo = pd.melt(df, id_vars=id_vars, var_name="Año_Trimestre", value_name=value_name)
    df_largo["Fecha"] = (
        pd.PeriodIndex(df_largo["Año_Trimestre"], freq="Q")
        .to_timestamp(how="end").normalize()
    )
    df_largo = df_largo.drop(columns=["Año_Trimestre"])
    return df_largo

def agregar_columna_estado(df, col_origen, valor_total_fila=0):
    df = df.copy()
    df["Estado"] = ""
    df.loc[valor_total_fila, "Estado"] = "Total general"
    mask_estado = df[col_origen].isin(ESTADOS)
    df.loc[mask_estado, "Estado"] = df.loc[mask_estado, col_origen]
    df["Estado"] = df["Estado"].replace(["", False], np.nan)
    df["Estado"] = df["Estado"].ffill()
    df.loc[mask_estado, col_origen] = "Total general por estado"
    return df

def jerarquizar_scian(df, col_origen):
    df = df.copy()
    df[["Código", "Concepto"]] = df[col_origen].str.split(r"\s+", n=1, expand=True)
    df["Nivel"]    = df["Código"].apply(lambda x: 2 if "-" in str(x) else len(str(x)))
    df["Sector"]   = df["Código"].apply(lambda x: x if "-" in str(x) else str(x)[:2])
    df["Subsector"]= df["Código"].apply(lambda x: None if "-" in str(x) or len(str(x)) < 3 else str(x)[:3])
    df["Rama"]     = df["Código"].apply(lambda x: None if "-" in str(x) or len(str(x)) < 4 else str(x)[:4])
    return df

def _fix_nivel(hoja):
    for _col in ["Nivel", "Sector", "Subsector", "Rama"]:
        hoja[_col] = hoja[_col].astype(object)
        hoja.loc[0, _col] = 1
    return hoja

CONCEPTOS_NO_PAIS = ["Total general","Nuevas inversiones","Cuentas entre compañías","Reinversión de utilidades"]

def agregar_columna_pais(df, col_origen):
    df = df.copy()
    df["País"] = ""
    df.loc[0, "País"] = "Total general"
    todos = df[col_origen].unique()
    lista_paises = [v for v in todos if v not in CONCEPTOS_NO_PAIS]
    mask_pais = df[col_origen].isin(lista_paises)
    df.loc[mask_pais, "País"] = df.loc[mask_pais, col_origen]
    df["País"] = df["País"].replace(["", False], np.nan).ffill()
    df.loc[mask_pais, col_origen] = "Total general por país"
    return df, lista_paises

# ── Archivo 1 ──────────────────────────────────────────────────────────────
print("Procesando archivo 1: Flujos por tipo de inversión...")
a1 = pd.read_excel(RAW_DATA_DIR / "2025_3T_Flujosportipodeinversion_actu__3_.xlsx", sheet_name=None, header=None)
print(f"  Hojas: {list(a1.keys())}")

hoja = limpiar_encabezados(a1["Por tipo de inversión"], 2, 3, "Tipo de Inversión")
df_out = a_formato_largo(hoja, ["Tipo de Inversión"])
df_out.to_csv(PROCESSED_DATA_DIR / "Investment_Types.csv", index=False, encoding="utf-8-sig")
print(f"    ✓ Investment_Types.csv — {len(df_out):,} filas")

hoja = limpiar_encabezados(a1["Por origen"], 2, 3, "Origen")
df_out = a_formato_largo(hoja, ["Origen"])
df_out.to_csv(PROCESSED_DATA_DIR / "Origin_of_Investment.csv", index=False, encoding="utf-8-sig")
print(f"    ✓ Origin_of_Investment.csv — {len(df_out):,} filas")

hoja = limpiar_encabezados(a1["Por sector"], 2, 5, "Sector, subsector y rama")
hoja = jerarquizar_scian(hoja, "Sector, subsector y rama")
hoja.loc[0, "Concepto"] = "Total general"
hoja = _fix_nivel(hoja)
hoja = hoja.drop(columns=["Sector, subsector y rama", "Código"])
df_out = a_formato_largo(hoja, ["Concepto", "Nivel", "Sector", "Subsector", "Rama"])
df_out["Nivel"] = df_out["Nivel"].astype(int)
df_out.to_csv(PROCESSED_DATA_DIR / "Investment_by_Sector.csv", index=False, encoding="utf-8-sig")
print(f"    ✓ Investment_by_Sector.csv — {len(df_out):,} filas")

hoja = limpiar_encabezados(a1["Por entidad federativa"], 2, 3, "Entidad federativa")
df_out = a_formato_largo(hoja, ["Entidad federativa"])
df_out.to_csv(PROCESSED_DATA_DIR / "Investment_by_State.csv", index=False, encoding="utf-8-sig")
print(f"    ✓ Investment_by_State.csv — {len(df_out):,} filas")

# ── Archivo 2 ──────────────────────────────────────────────────────────────
print("\nProcesando archivo 2: Flujos por entidad federativa...")
a2 = pd.read_excel(RAW_DATA_DIR / "2025_3T_Flujosporentidadfederativa_actu__5__.xlsx", sheet_name=None, header=None)
print(f"  Hojas: {list(a2.keys())}")

hoja = limpiar_encabezados(a2["Tipo de inversión"], 2, 3, "Entidad Federativa / Tipo de Inversión ")
hoja = agregar_columna_estado(hoja, "Entidad Federativa / Tipo de Inversión ")
hoja = hoja.rename(columns={"Entidad Federativa / Tipo de Inversión ": "Tipo de Inversión"})
df_out = a_formato_largo(hoja, ["Tipo de Inversión", "Estado"])
df_out.to_csv(PROCESSED_DATA_DIR / "Investment_Type_by_State.csv", index=False, encoding="utf-8-sig")
print(f"    ✓ Investment_Type_by_State.csv — {len(df_out):,} filas")

hoja = limpiar_encabezados(a2["Origen"], 2, 3, "Entidad Federativa / Origen")
hoja = agregar_columna_estado(hoja, "Entidad Federativa / Origen")
hoja = hoja.rename(columns={"Entidad Federativa / Origen": "Inversión por país en cada estado"})
df_out = a_formato_largo(hoja, ["Inversión por país en cada estado", "Estado"])
df_out.to_csv(PROCESSED_DATA_DIR / "Investment_from_the_Countries_by_State.csv", index=False, encoding="utf-8-sig")
print(f"    ✓ Investment_from_the_Countries_by_State.csv — {len(df_out):,} filas")

hoja = limpiar_encabezados(a2["Actividad económica"], 2, 4, "Entidad Federativa / Actividad Económica")
hoja = jerarquizar_scian(hoja, "Entidad Federativa / Actividad Económica")
hoja.loc[0, "Concepto"] = "Total general"
hoja = _fix_nivel(hoja)
hoja["Estado"] = ""
hoja.loc[0, "Estado"] = "Total general"
mask_e = hoja["Entidad Federativa / Actividad Económica"].isin(ESTADOS)
hoja.loc[mask_e, "Estado"] = hoja.loc[mask_e, "Entidad Federativa / Actividad Económica"]
hoja["Estado"] = hoja["Estado"].replace(["", False], np.nan).ffill()
hoja.loc[mask_e, ["Entidad Federativa / Actividad Económica", "Concepto"]] = "Total general por estado"
for _col in ["Nivel", "Sector", "Subsector", "Rama"]:
    hoja[_col] = hoja[_col].astype(object)
    hoja.loc[hoja["Concepto"] == "Total general por estado", _col] = 0
hoja = hoja.drop(columns=["Código", "Entidad Federativa / Actividad Económica"])
df_out = a_formato_largo(hoja, ["Concepto", "Estado", "Nivel", "Sector", "Subsector", "Rama"])
df_out.to_csv(PROCESSED_DATA_DIR / "Investment_by_Sector_from_the_States.csv", index=False, encoding="utf-8-sig")
print(f"    ✓ Investment_by_Sector_from_the_States.csv — {len(df_out):,} filas")

# ── Archivo 3 ──────────────────────────────────────────────────────────────
print("\nProcesando archivo 3: Flujos por origen...")
a3 = pd.read_excel(RAW_DATA_DIR / "2025_3T_Flujospororigen_actu__4_.xlsx", sheet_name=None, header=None)
print(f"  Hojas: {list(a3.keys())}")

hoja = limpiar_encabezados(a3["Por tipo de inversión"], 2, 3, "Origen / Tipo de Inversión ")
hoja, _ = agregar_columna_pais(hoja, "Origen / Tipo de Inversión ")
hoja = hoja.rename(columns={"Origen / Tipo de Inversión ": "Tipo de Inversión"})
df_out = a_formato_largo(hoja, ["Tipo de Inversión", "País"])
df_out.to_csv(PROCESSED_DATA_DIR / "Investment_Types_by_Country.csv", index=False, encoding="utf-8-sig")
print(f"    ✓ Investment_Types_by_Country.csv — {len(df_out):,} filas")

hoja = limpiar_encabezados(a3["Por entidad federativa"], 2, 4, "Origen / Entidad Federativa")
hoja, _ = agregar_columna_pais(hoja, "Origen / Entidad Federativa")
hoja = hoja.rename(columns={"Origen / Entidad Federativa": "Inversión en cada estado por país"})
df_out = a_formato_largo(hoja, ["Inversión en cada estado por país", "País"])
df_out.to_csv(PROCESSED_DATA_DIR / "Investment_by_State_from_the_Countries.csv", index=False, encoding="utf-8-sig")
print(f"    ✓ Investment_by_State_from_the_Countries.csv — {len(df_out):,} filas")

hoja = limpiar_encabezados(a3["Por sector"], 2, 4, "Origen / Actividad Económica")
hoja = jerarquizar_scian(hoja, "Origen / Actividad Económica")
mask_no_num = ~hoja["Código"].str.match(r"^\d+$", na=False)
hoja.loc[mask_no_num, "Concepto"] = "Total general por país"
for _col in ["Nivel", "Sector", "Subsector", "Rama"]:
    hoja[_col] = hoja[_col].astype(object)
    hoja.loc[hoja["Concepto"] == "Total general por país", _col] = 0
hoja.loc[0, "Concepto"] = "Total general"
for _col in ["Nivel", "Sector", "Subsector", "Rama"]:
    hoja.loc[0, _col] = 1
hoja = hoja.drop(columns=["Código"])
hoja = hoja.rename(columns={"Origen / Actividad Económica": "País de origen"})
df_out = a_formato_largo(hoja, ["País de origen", "Concepto", "Nivel", "Sector", "Subsector", "Rama"])
df_out.to_csv(PROCESSED_DATA_DIR / "Investment_by_Sector_from_the_Countries.csv", index=False, encoding="utf-8-sig")
print(f"    ✓ Investment_by_Sector_from_the_Countries.csv — {len(df_out):,} filas")

print("\n" + "=" * 70)
print("LIMPIEZA COMPLETADA — 10 archivos CSV generados en proc_1/")
print("=" * 70)
csvs = sorted(PROCESSED_DATA_DIR.glob("*.csv"))
for csv in csvs:
    size_mb = csv.stat().st_size / (1024 * 1024)
    print(f"  {csv.name:<55} {size_mb:.1f} MB")
print("\nSiguiente paso: python pipeline/01_data_preparation.py")
