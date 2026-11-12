#!/usr/bin/env python3
"""Verify CSV coverage, then delete each legacy JSON and TODO.md one file at a time."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from catalogo import DATA_DIR, discover_json, sha256_bytes
from migrate_legacy import parse_todo
from validate_package import decode, validate


AUDIT_FIELDS = [
    "source_path",
    "sha256",
    "source_type",
    "source_record_count",
    "inventory_item_count",
    "array_element_count",
    "metadata_count",
    "url_count",
    "category_relation_count",
    "provenance_count",
    "locality_count",
    "triage_pending_count",
    "verification",
    "deleted",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def verify_todo(
    root: Path, package_dir: Path
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    manifest_path = package_dir / DATA_DIR / "id_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))["ids"]
    expected_items, expected_urls = parse_todo(root, manifest)
    actual_items = read_rows(package_dir / DATA_DIR / "item_todo.csv")
    actual_urls = read_rows(package_dir / DATA_DIR / "todo_url.csv")
    if {row["id"] for row in actual_items} != {row["id"] for row in expected_items}:
        raise ValueError(
            "Itens de TODO.md não estão todos representados em item_todo.csv"
        )
    for row in actual_items:
        expected = next(item for item in expected_items if item["id"] == row["id"])
        for field in ("tipo_item", "secao", "titulo", "status_triagem"):
            if row[field] != expected[field]:
                raise ValueError(
                    f"Campo TODO divergente ({field}) para {expected['titulo']}"
                )
        for field in ("descricao", "nota_triagem"):
            if decode(row[field], "string") != expected[field]:
                raise ValueError(
                    f"Texto TODO divergente ({field}) para {expected['titulo']}"
                )
        if decode(row["concluido"], "boolean") != expected["concluido"]:
            raise ValueError(
                f"Estado de conclusão TODO divergente para {expected['titulo']}"
            )
        if row["status_triagem"] != "pendente":
            raise ValueError(f"Item TODO sem triagem pendente: {expected['titulo']}")
    expected_url_rows = {
        (
            row["id"],
            row["todo_item_id"],
            row["rotulo"],
            row["endereco"],
            row["tipo_endereco"],
        )
        for row in expected_urls
    }
    actual_url_rows = {
        (
            row["id"],
            row["todo_item_id"],
            row["rotulo"],
            decode(row["endereco"], "string"),
            row["tipo_endereco"],
        )
        for row in actual_urls
    }
    if expected_url_rows != actual_url_rows:
        raise ValueError("Links/caminhos do TODO.md não correspondem a todo_url.csv")
    return actual_items, actual_urls


def write_audit(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=AUDIT_FIELDS, lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)


def cutover(root: Path, package_dir: Path) -> dict[str, int]:
    root = root.resolve()
    package_dir = package_dir.resolve()
    audit_path = (
        package_dir / ".local" / "share" / "osint-rondonia" / "cutover_audit.csv"
    )
    if audit_path.exists():
        raise ValueError(f"Registro de corte já existe: {audit_path}")

    # Global value-by-value verification first. No source file is removed before this passes.
    package_counts = validate(package_dir, verify_originals=True, root=root)
    todo_items, todo_urls = verify_todo(root, package_dir)
    files = discover_json(root)
    if not files:
        raise ValueError("Nenhum JSON legado está disponível para o corte")

    original_rows = {
        row["caminho_origem"]: row
        for row in read_rows(package_dir / DATA_DIR / "registro_original.csv")
    }
    source_rows = read_rows(package_dir / DATA_DIR / "fonte.csv")
    source_by_id = {row["id"]: row for row in source_rows}
    inventory_rows = read_rows(package_dir / DATA_DIR / "inventario.csv")
    inventory_by_id = {row["id"]: row for row in inventory_rows}
    source_urls = Counter(
        row["fonte_id"] for row in read_rows(package_dir / DATA_DIR / "fonte_url.csv")
    )
    source_categories = Counter(
        row["fonte_id"]
        for name in (
            "fonte_categoria",
            "fonte_categoria_original",
            "fonte_categoria_curadoria",
        )
        for row in read_rows(package_dir / DATA_DIR / f"{name}.csv")
    )
    source_origins = Counter(
        row["fonte_id"]
        for row in read_rows(package_dir / DATA_DIR / "fonte_origem.csv")
    )
    source_localities = Counter(
        row["fonte_id"]
        for row in read_rows(package_dir / DATA_DIR / "fonte_localidade.csv")
    )
    inventory_items: Counter[str] = Counter()
    for row in read_rows(package_dir / DATA_DIR / "inventario_item.csv"):
        inventory_items[row["inventario_id"]] += 1
    inventory_elements = Counter(
        row["inventario_id"]
        for row in read_rows(package_dir / DATA_DIR / "inventario_elemento.csv")
    )
    inventory_metadata = Counter(
        row["inventario_id"]
        for row in read_rows(package_dir / DATA_DIR / "inventario_metadado.csv")
    )

    audit_rows: list[dict[str, Any]] = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        registry = original_rows.get(relative)
        if registry is None:
            raise ValueError(f"Arquivo sem linha de proveniência: {relative}")
        raw = path.read_bytes()
        digest = sha256_bytes(raw)
        if digest != registry["sha256"]:
            raise ValueError(f"Hash alterado antes do corte: {relative}")
        source_id = registry["fonte_id"]
        inventory_id = registry["inventario_id"]
        is_source = source_id not in {"", r"\N"}
        is_inventory = inventory_id not in {"", r"\N"}
        if is_source == is_inventory:
            raise ValueError(
                f"Origem sem tipo único/identidade para cobertura: {relative}"
            )
        if is_source and source_id not in source_by_id:
            raise ValueError(f"Ficha não encontrada em fonte.csv: {relative}")
        if is_inventory and inventory_id not in inventory_by_id:
            raise ValueError(f"Inventário não encontrado em inventario.csv: {relative}")
        audit_rows.append(
            {
                "source_path": relative,
                "sha256": digest,
                "source_type": "fonte" if is_source else "inventario",
                "source_record_count": 1 if is_source else 0,
                "inventory_item_count": inventory_items[inventory_id]
                if is_inventory
                else 0,
                "array_element_count": inventory_elements[inventory_id]
                if is_inventory
                else 0,
                "metadata_count": inventory_metadata[inventory_id]
                if is_inventory
                else 0,
                "url_count": source_urls[source_id] if is_source else 0,
                "category_relation_count": source_categories[source_id]
                if is_source
                else 0,
                "provenance_count": source_origins[source_id] if is_source else 0,
                "locality_count": source_localities[source_id] if is_source else 0,
                "triage_pending_count": 0,
                "verification": "hash e comparação estrutural/relacional aprovados",
                "deleted": "true",
            }
        )

    todo_path = root / "TODO.md"
    if todo_path.is_file():
        audit_rows.append(
            {
                "source_path": "TODO.md",
                "sha256": sha256_bytes(todo_path.read_bytes()),
                "source_type": "backlog",
                "source_record_count": len(todo_items),
                "inventory_item_count": 0,
                "array_element_count": 0,
                "metadata_count": 0,
                "url_count": len(todo_urls),
                "category_relation_count": 0,
                "provenance_count": 0,
                "locality_count": 0,
                "triage_pending_count": sum(
                    row["status_triagem"] == "pendente" for row in todo_items
                ),
                "verification": "itens, textos, status e endereços comparados com item_todo.csv/todo_url.csv",
                "deleted": "true",
            }
        )

    # Keep the detailed audit outside the published and versioned catalog.
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    write_audit(audit_path, audit_rows)
    report_path = (
        package_dir / ".local" / "share" / "osint-rondonia" / "migration_report.json"
    )
    report_backup = report_path.read_bytes() if report_path.exists() else None
    if report_backup is not None:
        report = json.loads(report_backup)
        report["cutover"] = {
            "legacy_json_deleted": 0,
            "todo_markdown_deleted": False,
            "audit_csv": ".local/share/osint-rondonia/cutover_audit.csv",
            "csv_package_rows_before_audit": package_counts["rows"],
            "status": "em andamento; ver o relatório de corte local",
        }
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    # Delete each file individually, re-hashing immediately before unlinking it.
    for index, path in enumerate(files):
        expected_hash = audit_rows[index]["sha256"]
        if sha256_bytes(path.read_bytes()) != expected_hash:
            raise ValueError(
                f"Arquivo mudou durante a rodada de corte: {path.relative_to(root)}"
            )
        os.unlink(path)
    if todo_path.is_file():
        todo_expected = next(
            row["sha256"] for row in audit_rows if row["source_path"] == "TODO.md"
        )
        if sha256_bytes(todo_path.read_bytes()) != todo_expected:
            raise ValueError("TODO.md mudou durante a rodada de corte")
        os.unlink(todo_path)

    report = json.loads(report_backup) if report_backup is not None else {}
    report["cutover"] = {
        "legacy_json_deleted": len(files),
        "todo_markdown_deleted": any(
            row["source_path"] == "TODO.md" for row in audit_rows
        ),
        "audit_csv": ".local/share/osint-rondonia/cutover_audit.csv",
        "csv_package_rows_before_audit": package_counts["rows"],
        "status": "concluído",
    }
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    final_counts = validate(package_dir)
    return {
        "json_deleted": len(files),
        "todo_deleted": int(any(row["source_path"] == "TODO.md" for row in audit_rows)),
        "files_audited": len(audit_rows),
        "resources_after_cutover": final_counts["resources"],
        "rows_after_cutover": final_counts["rows"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--package-dir", type=Path, default=None)
    args = parser.parse_args()
    try:
        print(
            json.dumps(
                cutover(args.root, args.package_dir or args.root),
                ensure_ascii=False,
                indent=2,
            )
        )
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
