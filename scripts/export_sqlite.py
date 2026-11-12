#!/usr/bin/env python3
"""Exporta o Data Package validado para SQLite via Frictionless e SQLAlchemy."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from tempfile import TemporaryDirectory
from pathlib import Path
from typing import Any

from frictionless import Package
from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKeyConstraint,
    Integer,
    MetaData,
    PrimaryKeyConstraint,
    Table,
    Text,
    create_engine,
    insert,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = ROOT
DEFAULT_OUTPUT = ROOT / "data" / "exports" / "catalog.sqlite"
STAGING = ROOT / ".local" / "share" / "osint-rondonia"
SQL_TYPES = {"string": Text, "integer": Integer, "number": Float, "boolean": Boolean}


def load_validated_package(package_dir: Path) -> tuple[dict[str, Any], Package]:
    # Project checks cover primary/FK relations and constraints that Frictionless
    # currently does not enforce itself. Frictionless then validates and parses rows.
    from validate_package import validate as validate_project_package

    validate_project_package(package_dir)
    descriptor = json.loads(
        (package_dir / "datapackage.json").read_text(encoding="utf-8")
    )
    package = Package(str(package_dir / "datapackage.json"))
    report = package.validate()
    if not report.valid:
        raise ValueError(
            f"Frictionless rejeitou o Data Package: {report.flatten(['row', 'field', 'code', 'message'])}"
        )
    return descriptor, package


def build_metadata(descriptor: dict[str, Any]) -> tuple[MetaData, dict[str, Table]]:
    metadata = MetaData()
    tables: dict[str, Table] = {}
    for resource in descriptor["resources"]:
        schema = resource["schema"]
        fields = schema["fields"]
        primary_key = schema.get("primaryKey", [])
        if isinstance(primary_key, str):
            primary_key = [primary_key]
        columns = []
        for field in fields:
            name = field["name"]
            kind = field.get("type", "string")
            if kind not in SQL_TYPES:
                raise ValueError(
                    f"Tipo Table Schema não suportado para SQLite: {resource['name']}.{name}: {kind}"
                )
            constraints = field.get("constraints", {})
            columns.append(
                Column(
                    name,
                    SQL_TYPES[kind](),
                    nullable=not constraints.get("required", False)
                    and name not in primary_key,
                    unique=constraints.get("unique", False),
                )
            )
        foreign_keys = []
        for relation in schema.get("foreignKeys", []):
            source_fields = relation["fields"]
            reference = relation["reference"]
            target_fields = reference["fields"]
            if isinstance(source_fields, str):
                source_fields = [source_fields]
            if isinstance(target_fields, str):
                target_fields = [target_fields]
            foreign_keys.append(
                ForeignKeyConstraint(
                    source_fields,
                    [f"{reference['resource']}.{field}" for field in target_fields],
                )
            )
        tables[resource["name"]] = Table(
            resource["name"],
            metadata,
            *columns,
            *foreign_keys,
            PrimaryKeyConstraint(*primary_key),
        )
    return metadata, tables


def export_to_path(package_dir: Path, output_path: Path) -> dict[str, int]:
    package_dir = package_dir.resolve()
    output_path = output_path.resolve()
    descriptor, package = load_validated_package(package_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    if temporary.exists():
        temporary.unlink()
    metadata, tables = build_metadata(descriptor)
    engine = create_engine(f"sqlite:///{temporary}")
    try:
        metadata.create_all(engine)
        counts: dict[str, int] = {}
        with engine.begin() as connection:
            connection.exec_driver_sql("PRAGMA defer_foreign_keys = ON")
            for resource in descriptor["resources"]:
                name = resource["name"]
                rows = package.get_table_resource(name).read_rows()
                records = [dict(row) for row in rows]
                if records:
                    connection.execute(insert(tables[name]), records)
                counts[name] = len(records)
        engine.dispose()
        check = sqlite3.connect(temporary)
        check.row_factory = sqlite3.Row
        try:
            check.execute("PRAGMA foreign_keys = ON")
            fk_errors = check.execute("PRAGMA foreign_key_check").fetchall()
            integrity = check.execute("PRAGMA integrity_check").fetchone()
            if fk_errors or integrity[0] != "ok":
                raise ValueError(
                    f"SQLite inválido: foreign_key_check={fk_errors[:5]!r}; integrity={integrity!r}"
                )
            actual_tables = {
                row[0]
                for row in check.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            }
            if actual_tables != set(tables):
                raise ValueError(
                    f"Conjunto de tabelas diverge: {sorted(actual_tables)} != {sorted(tables)}"
                )
            for resource in descriptor["resources"]:
                name = resource["name"]
                schema = resource["schema"]
                columns = check.execute(f'PRAGMA table_info("{name}")').fetchall()
                expected_columns = [field["name"] for field in schema["fields"]]
                if [column["name"] for column in columns] != expected_columns:
                    raise ValueError(f"Colunas/ordem divergentes em {name}")
                primary_key = schema.get("primaryKey", [])
                if isinstance(primary_key, str):
                    primary_key = [primary_key]
                actual_primary_key = [
                    column["name"]
                    for column in sorted(
                        (col for col in columns if col["pk"]), key=lambda col: col["pk"]
                    )
                ]
                if actual_primary_key != primary_key:
                    raise ValueError(
                        f"Chave primária divergente em {name}: {actual_primary_key} != {primary_key}"
                    )
                expected_foreign_keys: set[tuple[str, str, str]] = set()
                for relation in schema.get("foreignKeys", []):
                    from_fields = relation["fields"]
                    ref = relation["reference"]
                    to_fields = ref["fields"]
                    from_fields = (
                        [from_fields] if isinstance(from_fields, str) else from_fields
                    )
                    to_fields = [to_fields] if isinstance(to_fields, str) else to_fields
                    expected_foreign_keys.update(
                        (field, ref["resource"], target)
                        for field, target in zip(from_fields, to_fields)
                    )
                actual_foreign_keys = {
                    (row["from"], row["table"], row["to"])
                    for row in check.execute(
                        f'PRAGMA foreign_key_list("{name}")'
                    ).fetchall()
                }
                if actual_foreign_keys != expected_foreign_keys:
                    raise ValueError(f"Chaves estrangeiras divergentes em {name}")
                actual = check.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
                if actual != counts[resource["name"]]:
                    raise ValueError(
                        f"Contagem diverge em {resource['name']}: {actual} != {counts[resource['name']]}"
                    )
        finally:
            check.close()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        os.replace(temporary, output_path)
        return counts
    except Exception:
        engine.dispose()
        if temporary.exists():
            temporary.unlink()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        STAGING.mkdir(parents=True, exist_ok=True)
        output = args.output.resolve()
        with TemporaryDirectory(dir=STAGING) as staging:
            staged = Path(staging) / "catalog.sqlite"
            counts = export_to_path(args.package_dir, staged)
            output.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staged, output)
        print(
            json.dumps(
                {
                    "output": str(output),
                    "tables": len(counts),
                    "rows": sum(counts.values()),
                    "rows_by_table": counts,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
