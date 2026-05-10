# =============================================================================
# EJECUTOR MAESTRO DEL PIPELINE — IED Intelligence Platform
# =============================================================================
# Uso: desde la raíz IED/ ejecutar:
#   python pipeline/run_pipeline.py
# =============================================================================

import subprocess, sys, time
from pathlib import Path

BASE         = Path(__file__).resolve().parent.parent
PIPELINE_DIR = Path(__file__).resolve().parent

steps = [
    ("00_cleaning_data.py",   "Limpieza de datos originales (Excel → CSV)"),
    ("01_data_preparation.py","Preparación y normalización (CSV → Parquet)"),
    ("02_graph_analytics.py", "Análisis de redes y comunidades"),
    ("03_economic_scoring.py","Scoring económico e indicadores estructurales"),
    ("04_clustering.py",      "Clustering estructural de estados"),
]

print("=" * 70)
print("  IED Intelligence Platform — Pipeline Completo")
print("=" * 70)
print(f"  Raíz del proyecto: {BASE}")
print()

total_start = time.time()
failed = False

for script, description in steps:
    script_path = PIPELINE_DIR / script
    print(f"{'─'*70}")
    print(f"  EJECUTANDO: {description}")
    print(f"  Script:     {script_path.name}")
    print(f"{'─'*70}")
    t0 = time.time()
    result = subprocess.run([sys.executable, str(script_path)], capture_output=False)
    elapsed = time.time() - t0
    if result.returncode != 0:
        print(f"\n  ✗ FALLÓ en {elapsed:.1f}s — Pipeline detenido")
        failed = True
        break
    print(f"\n  ✓ Completado en {elapsed:.1f}s\n")

total_elapsed = time.time() - total_start
print("=" * 70)
if failed:
    print("  PIPELINE FALLIDO — Revisa el error arriba")
    sys.exit(1)
else:
    print(f"  PIPELINE COMPLETO en {total_elapsed:.0f}s")
    print()
    print("  Para lanzar la aplicación:")
    print("      streamlit run app/main.py")
print("=" * 70)
