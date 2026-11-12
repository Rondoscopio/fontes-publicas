#!/usr/bin/env python3
"""Valida os CSV, schemas e relações do Data Package."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from geografia import validar_geografia

NULL = r"\N"
PROFILE_V2 = "https://datapackage.org/profiles/2.0/datapackage.json"


def fail(message: str) -> None:
    raise ValueError(message)


def decode(value: str, kind: str) -> Any:
    if value == NULL:
        return None
    if kind in {"object", "array"}:
        return json.loads(value)
    if kind == "boolean":
        if value not in {"true", "false"}:
            fail(f"boolean inválido: {value!r}")
        return value == "true"
    if kind == "integer":
        return int(value)
    if kind == "number":
        return float(value)
    return value


def validate(package_dir: Path) -> dict[str, int]:
    descriptor_path = package_dir / "datapackage.json"
    if not descriptor_path.exists():
        fail(f"Descritor ausente: {descriptor_path}")
    descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
    if descriptor.get("$schema") != PROFILE_V2:
        fail(
            f"O descritor não aponta para o perfil Data Package 2.0: {descriptor.get('$schema')!r}"
        )
    if not isinstance(descriptor.get("resources"), list) or not descriptor["resources"]:
        fail("O descritor precisa conter resources não vazio")

    resources: dict[str, dict[str, Any]] = {}
    tables: dict[str, list[dict[str, str]]] = {}
    total_rows = 0
    for item in descriptor["resources"]:
        name = item.get("name")
        if not isinstance(name, str) or name in resources:
            fail(f"Nome de recurso ausente ou duplicado: {name!r}")
        if item.get("type") != "table" or item.get("format") != "csv":
            fail(f"Recurso {name} deve ser uma tabela CSV")
        schema = item.get("schema", {})
        fields = schema.get("fields", [])
        columns = [field.get("name") for field in fields]
        if (
            len(columns) != len(set(columns))
            or not columns
            or any(not isinstance(col, str) for col in columns)
        ):
            fail(f"Schema de colunas inválido em {name}")
        path = package_dir / item["path"]
        if not path.is_file():
            fail(f"CSV ausente para {name}: {path}")
        with path.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream, delimiter=",")
            if reader.fieldnames != columns:
                fail(
                    f"Cabeçalho divergente em {name}: {reader.fieldnames!r} != {columns!r}"
                )
            rows = list(reader)
        declared_types = {field["name"]: field.get("type", "any") for field in fields}
        for index, row in enumerate(rows, start=2):
            for field in fields:
                column = field["name"]
                value = row[column]
                if value == NULL:
                    if field.get("constraints", {}).get("required"):
                        fail(f"{name}:{index}: {column} é obrigatório")
                    continue
                kind = declared_types[column]
                try:
                    decode(value, kind)
                except (ValueError, TypeError, json.JSONDecodeError) as exc:
                    fail(
                        f"{name}:{index}: valor {column} incompatível com {kind}: {value!r} ({exc})"
                    )
        pk = schema.get("primaryKey", [])
        if isinstance(pk, str):
            pk = [pk]
        if not pk or any(col not in columns for col in pk):
            fail(f"Chave primária inválida em {name}: {pk}")
        seen: set[tuple[str, ...]] = set()
        for index, row in enumerate(rows, start=2):
            key = tuple(row[col] for col in pk)
            if any(part == NULL for part in key):
                fail(f"{name}:{index}: chave primária nula")
            if key in seen:
                fail(f"{name}:{index}: chave primária duplicada {key}")
            seen.add(key)
        resources[name] = item
        tables[name] = rows
        total_rows += len(rows)

    # Foreign keys are checked by logical values; a fully null optional reference is allowed.
    for name, item in resources.items():
        for relation in item.get("schema", {}).get("foreignKeys", []):
            from_fields = relation.get("fields")
            reference = relation.get("reference", {})
            target = reference.get("resource")
            target_fields = reference.get("fields")
            if isinstance(from_fields, str):
                from_fields = [from_fields]
            if isinstance(target_fields, str):
                target_fields = [target_fields]
            if (
                target not in tables
                or not from_fields
                or len(from_fields) != len(target_fields or [])
            ):
                fail(f"Chave estrangeira declarada inválida em {name}: {relation}")
            target_keys = {
                tuple(row[col] for col in target_fields) for row in tables[target]
            }
            for index, row in enumerate(tables[name], start=2):
                key = tuple(row[col] for col in from_fields)
                if all(value == NULL for value in key):
                    continue
                if any(value == NULL for value in key) or key not in target_keys:
                    fail(f"FK órfã em {name}:{index} -> {target}: {key}")

    validar_geografia(tables)
    counts = {name: len(rows) for name, rows in tables.items()}
    return {
        "resources": len(resources),
        "rows": total_rows,
        **{f"rows_{k}": v for k, v in counts.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package-dir", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    try:
        result = validate(args.package_dir.resolve())
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
