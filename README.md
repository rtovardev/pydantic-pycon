# pydantic-pycon

Material de la charla **«Agentes de IA con Pydantic AI: de cero a producción con menos magia y más ingeniería»**, presentada en PyCon Panamá 2026.

Aquí hay un agente de triage de soporte con salida tipada, un servicio FastAPI que lo expone y las pruebas que corren sin llamar a ningún modelo. Todos los datos son sintéticos.

## Contenido

| Ruta | Qué es |
|---|---|
| `examples/agente.py` | Agente de Pydantic AI con `output_type`, una tool y dependencias tipadas |
| `examples/servicio.py` | Servicio FastAPI con plazo total y concurrencia acotada |
| `examples/postgres.py` | Acceso a PostgreSQL con asyncpg |
| `tests/` | Pruebas con `TestModel` y `agent.override`, sin red |
| `docs/resumen-charla.pdf` | Resumen del material de la charla |
| `docs/recursos-y-siguientes-pasos.pdf` | Referencias, temas para profundizar y siguientes pasos |

El agente de la demostración en vivo se añadirá a este repositorio después de la charla.

## Probarlo

Necesitas Python 3.11 o superior y [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest
```

Las pruebas bloquean las peticiones a modelos (`ALLOW_MODEL_REQUESTS = False`), así que no necesitan claves ni red.

Para correr el servicio con un modelo real, define el modelo y la base de datos:

```bash
export DATABASE_URL="postgresql://usuario:clave@localhost/soporte"
uv run uvicorn --factory examples.servicio:create_app
```

`create_app()` recibe el modelo como argumento (`create_app(model="proveedor:modelo")`). No hay un modelo fijado en el código. La tabla que consulta la tool es `customers(id, plan)`.

## Versiones

Pydantic AI 2.56.0, fijada en `pyproject.toml`. Los ejemplos usan `output_type`, no la API antigua `result_type`.

## Una advertencia

Una salida validada cumple un contrato de forma. No garantiza que el contenido sea verdadero ni que cada ejecución tenga éxito. Para eso están las pruebas, los límites y la revisión.

## Licencia

El código se publica bajo [MIT](LICENSE). Los documentos de `docs/` se publican bajo [CC BY 4.0](LICENSE-docs).
