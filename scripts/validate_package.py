#!/usr/bin/env python3
"""Valida CSV, chaves, Data Package local e (opcionalmente) os JSON originais."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from catalogo import NULL, PROFILE_V2, discover_json, read_json, sha256_bytes


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


def json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    return "object"


def get_pointer(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        fail(f"JSON Pointer inválido: {pointer}")
    value = document
    for part in pointer[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            value = value[int(part)]
        else:
            value = value[part]
    return value


def validate(
    package_dir: Path, verify_originals: bool = False, root: Path | None = None
) -> dict[str, int]:
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

    counts = {name: len(rows) for name, rows in tables.items()}
    if verify_originals:
        if root is None:
            fail("--verify-originals requer --root")
        verify_originals_data(root.resolve(), tables, package_dir.resolve())
    return {
        "resources": len(resources),
        "rows": total_rows,
        **{f"rows_{k}": v for k, v in counts.items()},
    }


def verify_originals_data(
    root: Path, tables: dict[str, list[dict[str, str]]], package_dir: Path
) -> None:
    descriptor = json.loads(
        (package_dir / "datapackage.json").read_text(encoding="utf-8")
    )
    resource_schemas = {
        item["name"]: item["schema"] for item in descriptor["resources"]
    }
    originals = {row["caminho_origem"]: row for row in tables["registro_original"]}
    discovered = {path.relative_to(root).as_posix() for path in discover_json(root)}
    if discovered != set(originals):
        fail(
            f"Inventário de JSON divergente: {len(discovered)} arquivos presentes, {len(originals)} indexados"
        )
    parsed: dict[str, Any] = {}
    for relative, index_row in originals.items():
        path = root / relative
        if not path.is_file():
            fail(f"JSON original ausente: {relative}")
        raw = path.read_bytes()
        if sha256_bytes(raw) != index_row["sha256"]:
            fail(f"Hash SHA-256 divergente para {relative}")
        parsed[relative] = read_json(path)

    # Verify that every source fact has a corresponding normalized row and exact value.
    source_rows = {row["id"]: row for row in tables["fonte"]}
    original_to_source = {
        row["caminho_origem"]: row["fonte_id"]
        for row in originals.values()
        if row["tipo_documento"] == "fonte"
    }
    if set(original_to_source.values()) != set(source_rows):
        fail("Nem todas as fichas têm linha fonte e referência de origem")
    category_sets: dict[str, set[tuple[str, str]]] = {}
    for resource_name in (
        "fonte_categoria",
        "fonte_categoria_original",
        "fonte_categoria_curadoria",
    ):
        category_sets[resource_name] = {
            (row["fonte_id"], row["categoria_id"]) for row in tables[resource_name]
        }
    category_lookup = {
        "categoria": {row["id"]: row["nome"] for row in tables["categoria"]},
        "categoria_original": {
            row["id"]: row["valor_original"] for row in tables["categoria_original"]
        },
        "categoria_curadoria": {
            row["id"]: row["valor_original"] for row in tables["categoria_curadoria"]
        },
    }
    type_lookup = {row["id"]: row["nome"] for row in tables["tipo"]}
    validation_lookup = {
        row["id"]: row["valor_original"] for row in tables["status_validacao"]
    }
    scope_lookup = {row["id"]: row["valor_original"] for row in tables["abrangencia"]}
    locations = {row["id"]: row for row in tables["localidade"]}
    source_locations = {
        row["fonte_id"]: locations[row["localidade_id"]]
        for row in tables["fonte_localidade"]
    }
    provenance: dict[str, dict[str, str]] = defaultdict(dict)
    for row in tables["fonte_origem"]:
        provenance[row["fonte_id"]][row["tipo_origem"]] = row["valor_original"]
    urls: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tables["fonte_url"]:
        urls[row["fonte_id"]].append(row)
    scope_rows = {
        row["fonte_id"]: row["abrangencia_id"] for row in tables["fonte_abrangencia"]
    }
    scalar_fields = [
        "nome",
        "descricao",
        "nota",
        "observacao",
        "observacoes",
        "orgao_responsavel",
        "entidade_responsavel",
        "esfera",
        "tecnologia",
        "acesso_declarado",
        "data_referencia",
        "referencia_institucional",
        "repositorio_oficial",
        "licenca_spdx",
        "situacao_url",
    ]
    source_attributes = set(scalar_fields) | {
        "tipo",
        "status_validacao",
        "categoria",
        "categoria_original",
        "categoria_curadoria",
        "abrangencia",
        "url",
        "origem",
        "origem_cadastro",
        "municipio",
        "uf",
        "pais",
        "id",
        "links_relacionados",
        "status_triagem",
    }
    source_to_path = {source_id: path for path, source_id in original_to_source.items()}
    for relative, source_id in original_to_source.items():
        original = parsed[relative]
        unsupported_fields = set(original) - source_attributes
        if unsupported_fields:
            fail(
                f"Campos de ficha sem representação no CSV em {relative}: {sorted(unsupported_fields)}"
            )
        actual_triage = source_rows[source_id]["status_triagem"]
        if original.get("status_triagem") != (
            None if actual_triage == NULL else actual_triage
        ):
            fail(f"Status de triagem inferido ou alterado em {relative}")
    for source_id, row in source_rows.items():
        path = source_to_path[source_id]
        original = parsed[path]
        for field in scalar_fields:
            expected = original.get(field)
            actual = decode(row[field], "string")
            if expected != actual:
                fail(
                    f"Perda/divergência em {path} campo {field}: {expected!r} != {actual!r}"
                )
        if original.get("id") != decode(row["id_externo"], "string"):
            fail(f"ID externo divergente em {path}")
        if "tipo" in original and type_lookup[row["tipo_id"]] != original["tipo"]:
            fail(f"Tipo divergente em {path}")
        if (
            "status_validacao" in original
            and validation_lookup[row["status_validacao_id"]]
            != original["status_validacao"]
        ):
            fail(f"Status de validação divergente em {path}")
        for source_field, table_name in (
            ("categoria", "fonte_categoria"),
            ("categoria_original", "fonte_categoria_original"),
            ("categoria_curadoria", "fonte_categoria_curadoria"),
        ):
            found = {
                category_lookup[source_field][category_id]
                for fid, category_id in category_sets[table_name]
                if fid == source_id
            }
            expected = (
                {original[source_field]}
                if isinstance(original.get(source_field), str)
                else set()
            )
            if found != expected:
                fail(f"Classificação divergente em {path} campo {source_field}")
        if "abrangencia" in original:
            if (
                decode(scope_lookup[scope_rows[source_id]], "string")
                != original["abrangencia"]
            ):
                fail(f"Abrangência divergente em {path}")
        actual_origins = provenance.get(source_id, {})
        for field in ("origem", "origem_cadastro"):
            expected = original.get(field)
            if (
                expected is not None
                and decode(actual_origins[field], "string") != expected
            ):
                fail(f"Proveniência divergente em {path} campo {field}")
        if any(key in original for key in ("municipio", "uf", "pais")):
            local = source_locations[source_id]
            for field in ("municipio", "uf", "pais"):
                actual = decode(local[field], "string")
                if original.get(field) != actual:
                    fail(f"Localidade divergente em {path} campo {field}")
        main_urls = [
            entry for entry in urls[source_id] if entry["papel"] == "principal"
        ]
        if len(main_urls) != 1 or decode(main_urls[0]["url"], "string") != original.get(
            "url"
        ):
            fail(f"URL principal divergente em {path}")
        related_original = original.get("links_relacionados")
        related_rows = sorted(
            (entry for entry in urls[source_id] if entry["papel"] == "relacionada"),
            key=lambda entry: int(entry["ordem"]),
        )
        if isinstance(related_original, list):
            decoded = [
                {
                    "nome": decode(row["nome"], "string"),
                    "url": decode(row["url"], "string"),
                }
                for row in related_rows
            ]
            if decoded != related_original:
                fail(f"Links relacionados divergentes em {path}")
        elif related_rows:
            fail(f"Links relacionados adicionais em {path}")

    # Every inventory record points to an actual JSON object and preserves every declared field.
    inventories_by_id = {
        row["id"]: row["caminho_origem"] for row in tables["inventario"]
    }
    inventory_rows_by_path = {
        row["caminho_origem"]: row for row in tables["inventario"]
    }
    for inventory_id, path in inventories_by_id.items():
        doc = parsed[path]
        row = inventory_rows_by_path[path]
        expected_title = (
            doc.get("titulo")
            if isinstance(doc, dict) and isinstance(doc.get("titulo"), str)
            else Path(path).stem
        )
        expected_updated = doc.get("atualizado_em") if isinstance(doc, dict) else None
        if (
            decode(row["titulo"], "string") != expected_title
            or decode(row["atualizado_em"], "string") != expected_updated
        ):
            fail(f"Título/data do inventário divergente: {path}")
    for row in tables["inventario_elemento"]:
        inventory_path = inventories_by_id[row["inventario_id"]]
        expected = get_pointer(parsed[inventory_path], row["json_pointer"])
        actual = json.loads(row["valor_json"])
        if expected != actual or json_type(expected) != row["tipo_valor"]:
            fail(
                f"Elemento de lista divergente: {inventory_path}#{row['json_pointer']}"
            )
    inventory_item_count = 0
    item_schema = resource_schemas.get("inventario_item")
    if item_schema is None:
        fail("Recurso inventario_item ausente do Data Package")
    reserved = {
        "id",
        "inventario_id",
        "caminho_colecao",
        "json_pointer",
        "arquivo_referenciado",
        "fonte_id",
    }
    payload_fields = [
        field for field in item_schema["fields"] if field["name"] not in reserved
    ]
    for row in tables["inventario_item"]:
        inventory_path = inventories_by_id[row["inventario_id"]]
        item = get_pointer(parsed[inventory_path], row["json_pointer"])
        if not isinstance(item, dict):
            fail(
                f"Ponteiro de item não aponta para objeto: {inventory_path}#{row['json_pointer']}"
            )
        for field_descriptor in payload_fields:
            field = field_descriptor["name"]
            source_field = field_descriptor.get("sourceField", field)
            expected = item.get(source_field)
            raw_value = row[field]
            kind = field_descriptor["type"]
            if raw_value == NULL:
                actual = None
            elif field_descriptor.get("sourceEncoding") == "json" or isinstance(
                expected, (dict, list)
            ):
                actual = json.loads(raw_value)
            else:
                actual = decode(raw_value, kind)
            if expected != actual:
                fail(
                    f"Item de inventário divergente: {inventory_path}#{row['json_pointer']} campo {field}"
                )
        referenced = item.get("arquivo")
        if referenced != (
            None if row["arquivo_referenciado"] == NULL else row["arquivo_referenciado"]
        ):
            fail(
                f"Referência de arquivo divergente em {inventory_path}#{row['json_pointer']}"
            )
        inventory_item_count += 1
    if inventory_item_count == 0:
        fail("Nenhum item de inventário foi migrado")

    # Root fields not represented by collection tables are recoverable via typed metadata/elements.
    metadata_by_inventory: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tables["inventario_metadado"]:
        metadata_by_inventory[row["inventario_id"]].append(row)
    element_values: dict[str, set[str]] = defaultdict(set)
    for row in tables["inventario_elemento"]:
        element_values[row["inventario_id"]].add(row["json_pointer"])
    for inventory_id, path in inventories_by_id.items():
        doc = parsed[path]
        if not isinstance(doc, dict):
            continue
        for row in metadata_by_inventory[inventory_id]:
            expected = get_pointer(doc, row["json_pointer"])
            actual = json.loads(row["valor_json"])
            if expected != actual:
                fail(
                    f"Metadado de inventário divergente em {path}#{row['json_pointer']}"
                )
        # Every non-object collection element is represented by a JSON Pointer row.
        represented_elements = {
            row["json_pointer"]
            for row in tables["inventario_elemento"]
            if row["inventario_id"] == inventory_id
        }
        represented_items = {
            row["json_pointer"]
            for row in tables["inventario_item"]
            if row["inventario_id"] == inventory_id
        }

        def check_arrays(value: Any, parts: list[Any] | None = None):
            parts = parts or []
            if isinstance(value, dict):
                for key, child in value.items():
                    check_arrays(child, parts + [key])
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    pointer = "/" + "/".join(
                        str(p).replace("~", "~0").replace("/", "~1")
                        for p in parts + [index]
                    )
                    if isinstance(child, dict):
                        if pointer not in represented_items:
                            fail(f"Item de coleção ausente em {path}#{pointer}")
                    elif pointer not in represented_elements:
                        fail(f"Elemento de lista ausente em {path}#{pointer}")
                    if isinstance(child, (dict, list)):
                        check_arrays(child, parts + [index])

        check_arrays(doc)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package-dir", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument(
        "--verify-originals",
        action="store_true",
        help="Compara hash e valores normalizados com os JSON existentes",
    )
    args = parser.parse_args()
    try:
        result = validate(args.package_dir.resolve(), args.verify_originals, args.root)
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
