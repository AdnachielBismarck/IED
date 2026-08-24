# Contribución y desarrollo

## Preparación del entorno

```bash
python -m venv .venv
python -m pip install -r requirements-dev.txt
```

Activa el entorno virtual con el comando correspondiente a tu sistema operativo.

## Validaciones requeridas

Antes de proponer un cambio:

```bash
python -m compileall -q app pipeline reports tests
python -m pytest -q
```

Los cambios en metodología deben incluir:

- justificación de la decisión;
- actualización de la documentación correspondiente;
- actualización o incorporación de pruebas;
- regeneración de los artefactos afectados.

## Convenciones

- Python 3.11 y archivos UTF-8 con finales de línea LF.
- Cuatro espacios de indentación.
- Nombres técnicos en inglés cuando correspondan a conceptos estándar; texto de interfaz en español.
- Rutas relativas al proyecto mediante `pathlib.Path`.
- Semillas explícitas en algoritmos estocásticos.
- No incluir datos crudos, secretos, cachés ni reportes generados.

## Pull requests

Un pull request debe describir el problema, la solución, los artefactos modificados y las validaciones ejecutadas. Los cambios visuales deben incluir una captura de la página afectada.
