"""Helpers comuns para gerar e validar o catálogo relacional OSINT Rondônia."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

NULL = r"\N"
PROFILE_V2 = "https://datapackage.org/profiles/2.0/datapackage.json"
JSON_SCHEMA_DRAFT = "http://json-schema.org/draft-07/schema#"
DATA_DIR = "data"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_pointer(parts: Iterable[Any]) -> str:
    escaped = [str(p).replace("~", "~0").replace("/", "~1") for p in parts]
    return "/" + "/".join(escaped)


def read_json(path: Path) -> Any:
    # utf-8-sig accepts a BOM when present without changing the original bytes/hash.
    return json.loads(path.read_text(encoding="utf-8-sig"))


def csv_value(value: Any) -> str:
    if value is None:
        return NULL
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return canonical_json(value)
    if isinstance(value, str) and value == NULL:
        raise ValueError(f"O valor literal {NULL!r} é reservado para nulo no CSV")
    return str(value)


def write_csv(path: Path, columns: list[str], rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=columns,
            delimiter=",",
            quotechar='"',
            doublequote=True,
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\r\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({key: csv_value(row.get(key)) for key in columns})
            count += 1
    return count


def stable_id(manifest: dict[str, str], key: str, prefix: str) -> str:
    """Return a persisted, immutable ID; identity is a source path/pointer, not row order."""
    if key not in manifest:
        token = hashlib.sha256(key.encode("utf-8")).hexdigest()[:14]
        candidate = f"{prefix}-{token}"
        # A truncated digest collision is extremely unlikely, but is still rejected.
        if candidate in manifest.values():
            raise ValueError(f"Colisão de ID ao atribuir {key!r}: {candidate}")
        manifest[key] = candidate
    return manifest[key]


def field_type(values: list[Any]) -> str:
    types = {type(value) for value in values if value is not None}
    if not types:
        return "string"
    if types <= {bool}:
        return "boolean"
    if types <= {int, bool}:
        return "integer"
    if types <= {int, float}:
        return "number"
    if types <= {str}:
        return "string"
    return "string"  # Heterogeneous or structured legacy values are JSON-encoded.


def nested_value(values: list[Any]) -> bool:
    non_null = [value for value in values if value is not None]
    return (
        any(isinstance(value, (dict, list)) for value in non_null)
        or len({type(value) for value in non_null}) > 1
    )


def field_descriptor(
    name: str, kind: str, description: str, required: bool = False
) -> dict[str, Any]:
    result: dict[str, Any] = {"name": name, "type": kind, "description": description}
    if required:
        result["constraints"] = {"required": True}
    return result


def resource(
    name: str,
    path: str,
    columns: list[str],
    types: dict[str, str],
    descriptions: dict[str, str],
    primary_key: list[str],
    foreign_keys: list[dict[str, Any]] | None = None,
    required: set[str] | None = None,
) -> dict[str, Any]:
    required = required or set()
    schema: dict[str, Any] = {
        "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
        "fields": [
            field_descriptor(
                col,
                types.get(col, "string"),
                descriptions.get(col, col),
                col in required,
            )
            for col in columns
        ],
        "missingValues": [NULL],
        "primaryKey": primary_key,
    }
    if foreign_keys:
        schema["foreignKeys"] = foreign_keys
    return {
        "name": name,
        "type": "table",
        "path": path,
        "format": "csv",
        "mediatype": "text/csv",
        "dialect": {"delimiter": ",", "header": True, "lineTerminator": "\r\n"},
        "schema": schema,
    }


def fk(
    fields: str | list[str], resource_name: str, ref_fields: str | list[str]
) -> dict[str, Any]:
    fields = [fields] if isinstance(fields, str) else fields
    ref_fields = [ref_fields] if isinstance(ref_fields, str) else ref_fields
    return {
        "fields": fields,
        "reference": {"resource": resource_name, "fields": ref_fields},
    }


def inventory_walk(value: Any, parts: list[Any] | None = None):
    """Yield list locations and descendants for supplementary inventory elements."""
    parts = parts or []
    if isinstance(value, dict):
        for key, child in value.items():
            yield from inventory_walk(child, parts + [key])
    elif isinstance(value, list):
        yield parts, value
        for index, child in enumerate(value):
            if isinstance(child, (dict, list)):
                yield from inventory_walk(child, parts + [index])


def discover_json(root: Path) -> list[Path]:
    generated_data = root / DATA_DIR
    return sorted(
        path
        for path in root.rglob("*.json")
        if ".git" not in path.parts
        and "node_modules" not in path.parts
        and path.name != "datapackage.json"
        and generated_data not in path.parents
    )


def guess_record(data: Any) -> bool:
    return (
        isinstance(data, dict)
        and isinstance(data.get("nome"), str)
        and isinstance(data.get("url"), str)
    )


def load_manifest(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    ids = raw.get("ids", {})
    if not isinstance(ids, dict) or any(
        not isinstance(k, str) or not isinstance(v, str) for k, v in ids.items()
    ):
        raise ValueError(f"Manifesto inválido: {path}")
    if len(set(ids.values())) != len(ids):
        raise ValueError(f"Manifesto contém IDs duplicados: {path}")
    return ids


def type_map(
    rows: list[dict[str, Any]],
    columns: list[str],
    overrides: dict[str, str] | None = None,
) -> dict[str, str]:
    overrides = overrides or {}
    return {
        col: overrides.get(col, field_type([row.get(col) for row in rows]))
        for col in columns
    }


def json_schema_profile() -> str:
    return JSON_SCHEMA_DRAFT
