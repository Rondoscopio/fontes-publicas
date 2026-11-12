#!/usr/bin/env python3
"""Unify legacy inventory item CSV resources into one stable table."""

from __future__ import annotations

import argparse
import copy
import csv
import json
import os
from pathlib import Path
from typing import Any

from catalogo import NULL

BASE_FIELDS = [
    "id",
    "inventario_id",
    "caminho_colecao",
    "json_pointer",
    "arquivo_referenciado",
    "fonte_id",
]
LEGACY_PREFIX = "inventario_itens_"


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames or [], list(reader)


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=fields,
            delimiter=",",
            quotechar='"',
            doublequote=True,
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\r\n",
            extrasaction="raise",
        )
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def consolidate(package_dir: Path) -> dict[str, int]:
    package_dir = package_dir.resolve()
    descriptor_path = package_dir / "datapackage.json"
    descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
    resources = descriptor["resources"]
    legacy = [item for item in resources if item["name"].startswith(LEGACY_PREFIX)]
    if not legacy:
        if any(item["name"] == "inventario_item" for item in resources):
            return {"resources_merged": 0, "rows": 0}
        raise ValueError("Nenhuma tabela antiga de itens de inventário foi encontrada")

    field_descriptors: dict[str, dict[str, Any]] = {}
    rows: list[dict[str, str]] = []
    for resource in legacy:
        resource_path = package_dir / resource["path"]
        columns, resource_rows = read_rows(resource_path)
        declared = [field["name"] for field in resource["schema"]["fields"]]
        if columns != declared:
            raise ValueError(f"Cabeçalho divergente em {resource['path']}")
        if columns[: len(BASE_FIELDS)] != BASE_FIELDS:
            raise ValueError(f"Colunas estruturais inesperadas em {resource['path']}")
        for field in resource["schema"]["fields"][len(BASE_FIELDS) :]:
            name = field["name"]
            previous = field_descriptors.get(name)
            if previous and previous.get("type") != field.get("type"):
                raise ValueError(f"Tipo incompatível para campo de inventário {name}")
            if previous and previous.get("sourceEncoding") != field.get(
                "sourceEncoding"
            ):
                raise ValueError(
                    f"Codificação incompatível para campo de inventário {name}"
                )
            field_descriptors.setdefault(name, copy.deepcopy(field))
        for source_row in resource_rows:
            row = {field: source_row[field] for field in BASE_FIELDS}
            row.update(
                {
                    field: source_row.get(field)
                    if source_row.get(field) is not None
                    else NULL
                    for field in field_descriptors
                }
            )
            rows.append(row)

    payload_fields = sorted(field_descriptors)
    output_fields = BASE_FIELDS + payload_fields
    rows.sort(key=lambda row: row["id"])
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("IDs duplicados entre tabelas de itens de inventário")

    # Rebuild rows after discovering the complete field union, filling absent columns.
    normalized_rows: list[dict[str, str]] = []
    for resource in legacy:
        _, resource_rows = read_rows(package_dir / resource["path"])
        for source_row in resource_rows:
            row = {
                field: source_row.get(field)
                if source_row.get(field) is not None
                else NULL
                for field in BASE_FIELDS
            }
            row.update(
                {
                    field: source_row.get(field)
                    if source_row.get(field) is not None
                    else NULL
                    for field in payload_fields
                }
            )
            normalized_rows.append(row)
    normalized_rows.sort(key=lambda row: row["id"])

    first_index = min(resources.index(item) for item in legacy)
    template = copy.deepcopy(legacy[0])
    template["name"] = "inventario_item"
    template["path"] = "data/inventario_item.csv"
    template["schema"]["fields"] = [
        *[
            copy.deepcopy(field)
            for field in legacy[0]["schema"]["fields"]
            if field["name"] in BASE_FIELDS
        ],
        *[field_descriptors[name] for name in payload_fields],
    ]
    new_resources = [item for item in resources if item not in legacy]
    new_resources = [item for item in new_resources if item["name"] != "cutover_audit"]
    new_resources.insert(first_index, template)
    descriptor["resources"] = new_resources
    descriptor["description"] = (
        "Catálogo de fichas OSINT e inventários compostos de Rondônia em CSV relacionais. "
        "Dados de terceiros mantêm as condições e licenças declaradas em suas fontes; "
        "a licença AGPL do repositório aplica-se ao código. O token \\N representa "
        "valor nulo; strings vazias permanecem distintas. Os documentos JSON legados "
        "foram removidos após conferência de cobertura; caminho e hash permanecem em registro_original.csv."
    )

    data_dir = package_dir / "data"
    output_path = data_dir / "inventario_item.csv"
    write_rows(output_path, output_fields, normalized_rows)
    descriptor_tmp = descriptor_path.with_suffix(".json.tmp")
    descriptor_tmp.write_text(
        json.dumps(descriptor, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(descriptor_tmp, descriptor_path)
    for item in legacy:
        (package_dir / item["path"]).unlink(missing_ok=True)
    (data_dir / "cutover_audit.csv").unlink(missing_ok=True)
    (data_dir / "migration_report.json").unlink(missing_ok=True)
    return {"resources_merged": len(legacy), "rows": len(normalized_rows)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package-dir", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    result = consolidate(args.package_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
