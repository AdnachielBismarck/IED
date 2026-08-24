# Arquitectura técnica

## Objetivo

La aplicación separa la transformación de datos del consumo interactivo. Streamlit no ejecuta el pipeline durante el arranque: lee artefactos Parquet y JSON versionados, lo que reduce latencia y evita depender de los libros originales en producción.

```text
Libros de la Secretaría de Economía
                 |
                 v
        00_cleaning_data.py
                 |
                 v
       CSV normalizado (proc_1)
                 |
                 v
     01_data_preparation.py
                 |
       +---------+----------+
       |                    |
       v                    v
02_graph_analytics.py  03_economic_scoring.py
       |                    |
       +---------+----------+
                 |
                 v
          04_clustering.py
                 |
                 v
       Parquet y JSON (proc_2)
                 |
          +------+------+
          |             |
          v             v
     Streamlit       Reporte PDF
```

## Componentes

### Pipeline

Cada etapa es ejecutable de forma independiente y devuelve un código distinto de cero ante una falla. `pipeline/run_pipeline.py` coordina las etapas en orden y detiene la ejecución si alguna no concluye correctamente.

### Capa de datos

- `data/raw/`: archivos originales; no se versionan.
- `data/processed/proc_1/`: CSV intermedios; no se versionan.
- `data/processed/proc_2/`: artefactos optimizados requeridos por la aplicación; sí se versionan.
- `metadata.json`: fuente, moneda y período de cobertura consumidos por la interfaz y el reporte.

Los artefactos tabulares usan Parquet. La red interactiva se reconstruye a partir de `network_edges.parquet`; no se distribuyen objetos Python serializados.

### Aplicación

`app/shared.py` concentra identidad visual, navegación, procedencia y carga de metadatos. Las páginas contienen únicamente su carga analítica y componentes específicos.

La navegación nativa de Streamlit está desactivada para mantener etiquetas de negocio estables sin acoplarlas a nombres físicos de archivos.

### Pruebas

Las pruebas se dividen en dos grupos:

- Integridad de artefactos: cobertura estatal, período, rangos, distancia de red y tipologías.
- Smoke tests de Streamlit: ejecución de la portada y cada página dentro del contexto multipágina.

GitHub Actions ejecuta instalación, compilación y pruebas en Python 3.11 para cada push y pull request.

## Decisiones técnicas

### Artefactos versionados

El repositorio conserva `proc_2` porque Streamlit Community Cloud necesita esos archivos al iniciar. Los datos crudos y los intermedios, de mayor tamaño, se excluyen porque pueden reconstruirse desde la fuente.

### Distancia de red

NetworkX interpreta el peso de caminos mínimos como distancia. Una relación con más IED debe ser económicamente más cercana, por lo que betweenness y closeness usan `distance = 1 / IED`. El monto original permanece como `weight`.

### Tipología de estados

KMeans evalúa `k=2` a `k=6`. La selección maximiza silhouette entre soluciones cuyo grupo más pequeño contiene al menos tres estados. Las variables de escala y centralidad se usan para describir los grupos, no para formarlos, evitando que Ciudad de México se convierta en un grupo unitario.

### Valores confidenciales

Los registros `C` se conservan mediante `is_confidential` y su valor monetario se representa como nulo. No se imputan como cero porque la ausencia es producto de una regla institucional de confidencialidad.

## Despliegue

Comando de entrada:

```bash
streamlit run app/main.py
```

Versión objetivo: Python 3.11. Las dependencias de producción están en `requirements.txt`; las herramientas de prueba se declaran en `requirements-dev.txt`.
