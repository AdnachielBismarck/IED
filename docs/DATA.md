# Datos y artefactos

## Fuente

Secretaría de Economía, Dirección General de Inversión Extranjera. La fecha de corte exacta se registra en `data/processed/proc_2/metadata.json`.

Las cifras se expresan en millones de dólares corrientes.

## Artefactos principales

| Archivo | Granularidad | Uso |
|---|---|---|
| `investment_by_state.parquet` | estado, trimestre | Series y rankings territoriales |
| `investment_by_country.parquet` | país, trimestre | Composición por origen |
| `country_by_state.parquet` | país, estado, trimestre | Dependencia y red bipartita |
| `investment_types.parquet` | tipo, trimestre | Composición nacional |
| `types_by_state.parquet` | tipo, estado, trimestre | Diversificación estatal |
| `sector_by_state.parquet` | sector, estado, trimestre | Extensión sectorial |
| `sector_by_country.parquet` | sector, país, trimestre | Extensión sectorial por origen |
| `network_nodes.parquet` | nodo | Centralidades y Hub Score |
| `network_edges.parquet` | país, estado | Peso y distancia económica |
| `state_scores.parquet` | estado | Indicadores comparables |
| `state_clusters.parquet` | estado | Tipología y coordenadas PCA |
| `metadata.json` | conjunto | Fuente, moneda y cobertura |
| `clustering_diagnostics.json` | modelo | Selección de `k` y validación interna |

## Convenciones

- `Fecha`: cierre del trimestre reportado.
- `Year`, `Q`, `YQ`: campos derivados para agregación temporal.
- `IED`: flujo reportado; puede ser negativo por desinversión o revisión.
- `is_confidential`: identifica registros publicados como `C`.
- Los renglones de totales institucionales se excluyen antes de construir artefactos analíticos.

## Reproducción

Los archivos originales deben colocarse en `data/raw/`. Después se ejecuta:

```bash
python pipeline/run_pipeline.py
```

La reconstrucción sobrescribe los artefactos de `proc_2`. Antes de confirmar cambios debe ejecutarse la suite de pruebas para detectar modificaciones inesperadas en cobertura, esquemas o rangos.

## Restricciones de interpretación

- Los valores confidenciales no son faltantes aleatorios.
- Los acumulados no sustituyen análisis de flujo reciente.
- La asociación posterior a 2021 no demuestra un efecto causal de nearshoring.
- Los scores son herramientas comparativas y no recomendaciones de inversión.
