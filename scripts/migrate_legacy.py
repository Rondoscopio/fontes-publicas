#!/usr/bin/env python3
"""Importação inicial dos JSON legados para CSV relacionais e Data Package v2."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from catalogo import (
    DATA_DIR,
    NULL,
    PROFILE_V2,
    canonical_json,
    discover_json,
    field_type,
    fk,
    guess_record,
    inventory_walk,
    json_pointer,
    load_manifest,
    nested_value,
    read_json,
    resource,
    sha256_bytes,
    stable_id,
    type_map,
    write_csv,
)


SOURCE_SCALAR_FIELDS = [
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
SOURCE_STRUCTURED_FIELDS = {
    "id",
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
    "links_relacionados",
    "status_triagem",
}
SOURCE_FIELDS_SUPPORTED = set(SOURCE_SCALAR_FIELDS) | SOURCE_STRUCTURED_FIELDS
CAT_FIELDS = (
    ("categoria", "categoria"),
    ("categoria_original", "categoria_original"),
    ("categoria_curadoria", "categoria_curadoria"),
)


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def text_value(value: Any) -> Any:
    # Structured field values are kept as canonical JSON text in the relevant typed CSV column.
    if isinstance(value, (dict, list)):
        return canonical_json(value)
    return value


def source_reference(value: Any, source_paths: dict[str, str]) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    candidate = value.replace("\\", "/")
    while candidate.startswith("./"):
        candidate = candidate[2:]
    return source_paths.get(candidate)


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


def parse_todo(
    root: Path, manifest: dict[str, str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Export the TODO backlog without conflating implementation tasks with OSINT sources."""
    path = root / "TODO.md"
    if not path.is_file():
        return [], []
    lines = path.read_text(encoding="utf-8").splitlines()
    items: list[dict[str, Any]] = []
    urls: list[dict[str, Any]] = []
    current_section = ""
    reference_group = ""
    in_catalogue_intro = False
    in_activities = False
    note = next(
        (
            line.strip()
            for line in lines
            if line.startswith("Os links acima são referências para avaliação")
        ),
        "",
    )

    def add_item(
        key: str,
        item_type: str,
        section: str,
        title: str,
        description: str = "",
        completed: Any = None,
        triage_note: str | None = None,
    ) -> str:
        item_id = stable_id(manifest, f"todo_item:{key}", "todo")
        items.append(
            {
                "id": item_id,
                "tipo_item": item_type,
                "secao": section,
                "titulo": title,
                "descricao": description,
                "status_triagem": "pendente",
                "concluido": completed,
                "nota_triagem": triage_note,
            }
        )
        return item_id

    def add_urls(item_id: str, identity: str, text: str) -> str:
        # Markdown links first; then plain URLs used by TODO.md. Preserve URL spelling exactly.
        matches: list[tuple[str, str]] = []
        markdown_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        for match in markdown_pattern.finditer(text):
            matches.append((match.group(1), match.group(2)))
        remaining = markdown_pattern.sub("", text)
        for match in re.finditer(r"https?://[^\s)<>]+", remaining):
            url_value = match.group(0).rstrip(".,;")
            if url_value:
                matches.append(
                    (remaining[: match.start()].strip().rstrip(":") or "URL", url_value)
                )
        for index, (label, url_value) in enumerate(matches):
            url_id = stable_id(
                manifest, f"todo_url:{identity}:{text}:{index}:{url_value}", "turl"
            )
            urls.append(
                {
                    "id": url_id,
                    "todo_item_id": item_id,
                    "rotulo": label,
                    "endereco": url_value,
                    "tipo_endereco": "url"
                    if url_value.startswith(("http://", "https://"))
                    else "arquivo",
                }
            )
        # Return text without URL syntax for a compact descriptive field.
        stripped = markdown_pattern.sub(lambda match: match.group(1), text)
        stripped = re.sub(r"https?://[^\s)<>]+", "", stripped)
        return stripped.strip().rstrip(":")

    preamble: list[str] = []
    for raw in lines:
        if raw.startswith("## "):
            break
        if raw and not raw.startswith("#"):
            preamble.append(raw.strip())
    if preamble:
        preamble_text = "\n".join(preamble)
        context_id = add_item(
            "contexto:todo", "contexto", "TODO", "Contexto do TODO.md"
        )
        items[-1]["descricao"] = add_urls(context_id, "contexto:todo", preamble_text)

    objective_id: str | None = None
    project: dict[str, Any] | None = None

    def finish_project() -> None:
        nonlocal project
        if project is None:
            return
        description_lines: list[str] = []
        for raw_line in project["details"]:
            cleaned = add_urls(project["id"], project["identity"], raw_line)
            if cleaned:
                description_lines.append(cleaned)
        project["item"]["descricao"] = "\n".join(description_lines)
        project = None

    for raw in lines:
        if raw.startswith("## "):
            finish_project()
            current_section = raw[3:].strip()
            in_activities = False
            reference_group = ""
            in_catalogue_intro = current_section == "Catálogo web pesquisável"
            if in_catalogue_intro:
                objective_id = add_item(
                    "objetivo:catalogo-web-pesquisavel",
                    "objetivo",
                    current_section,
                    "Catálogo web pesquisável",
                    "",
                )
        elif raw.startswith("### "):
            finish_project()
            current_section = raw[4:].strip()
            in_activities = current_section == "Atividades"
            if in_activities:
                in_catalogue_intro = False
                reference_group = ""
            elif current_section == "Projetos de referência para estudar":
                in_catalogue_intro = True
                reference_group = ""
            else:
                in_catalogue_intro = False
                reference_group = ""
        elif raw.startswith("#### "):
            finish_project()
            in_catalogue_intro = False
            reference_group = raw[5:].strip()
            in_activities = False

        if in_catalogue_intro and raw and not raw.startswith("#"):
            cleaned = add_urls(
                objective_id or "", "objetivo:catalogo-web-pesquisavel", raw.strip()
            )
            if cleaned:
                for item in items:
                    if item["id"] == objective_id:
                        item["descricao"] = (item["descricao"] + "\n" + cleaned).strip()
                        break
        if in_activities:
            match = re.match(r"^- \[([ xX])\] (.+)$", raw)
            if match:
                task_text = match.group(2)
                add_item(
                    f"atividade:{task_text}",
                    "atividade",
                    current_section,
                    task_text,
                    completed=(match.group(1).lower() == "x"),
                )
        elif reference_group and raw.startswith("- **"):
            finish_project()
            match = re.match(r"^- \*\*(.+?)\*\*\s*$", raw)
            if match:
                title = match.group(1)
                identity = f"referencia:{reference_group}:{title}"
                item_id = add_item(
                    identity, "referencia", reference_group, title, triage_note=note
                )
                project = {
                    "id": item_id,
                    "identity": identity,
                    "item": items[-1],
                    "details": [],
                }
        elif project is not None and re.match(r"^\s{2,}- ", raw):
            project["details"].append(re.sub(r"^\s+- ", "", raw))

    finish_project()
    return items, urls


def migration(root: Path, package_dir: Path) -> dict[str, Any]:
    root = root.resolve()
    package_dir = package_dir.resolve()
    data_dir = package_dir / DATA_DIR
    data_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = data_dir / "id_manifest.json"
    manifest = load_manifest(manifest_path)
    paths = discover_json(root)
    if not paths:
        raise ValueError(
            "Nenhum JSON legado encontrado. Após o corte para CSV, use somente scripts/validate_package.py; "
            "não regenere o pacote a partir de entradas removidas."
        )
    docs: list[dict[str, Any]] = []
    parse_errors: list[dict[str, str]] = []
    source_paths: dict[str, str] = {}

    for path in paths:
        relative = relpath(path, root)
        raw = path.read_bytes()
        digest = sha256_bytes(raw)
        try:
            content = read_json(path)
        except Exception as exc:  # Explicit failure/report rather than silent omission.
            parse_errors.append(
                {"path": relative, "error": f"{type(exc).__name__}: {exc}"}
            )
            continue
        kind = (
            "fonte"
            if guess_record(content) and not relative.startswith("inventarios/")
            else "inventario"
        )
        document: dict[str, Any] = {
            "path": path,
            "relative_path": relative,
            "raw": raw,
            "sha256": digest,
            "content": content,
            "kind": kind,
        }
        docs.append(document)
        if kind == "fonte":
            source_paths[relative] = stable_id(manifest, f"fonte:{relative}", "src")

    if parse_errors:
        report = {"json_files": len(paths), "parse_errors": parse_errors}
        report_path = (
            package_dir
            / ".local"
            / "share"
            / "osint-rondonia"
            / "migration_report.json"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        raise ValueError(
            f"Encontrados {len(parse_errors)} JSON inválidos; relatório em .local/share/osint-rondonia/migration_report.json"
        )

    source_docs = [doc for doc in docs if doc["kind"] == "fonte"]
    inventory_docs = [doc for doc in docs if doc["kind"] == "inventario"]
    inventory_ids: dict[str, str] = {}
    for doc in inventory_docs:
        inventory_ids[doc["relative_path"]] = stable_id(
            manifest, f"inventario:{doc['relative_path']}", "inv"
        )
    todo_items, todo_urls = parse_todo(root, manifest)

    # Exact-string vocabularies: labels are not merged or editorially rewritten.
    vocab: dict[str, list[str]] = {name: [] for _, name in CAT_FIELDS}
    type_values: set[str] = set()
    validation_values: set[str] = set()
    scope_values: set[str] = set()
    local_keys: set[tuple[Any, Any, Any, str]] = set()
    for doc in source_docs:
        record = doc["content"]
        unsupported_fields = set(record) - SOURCE_FIELDS_SUPPORTED
        if unsupported_fields:
            raise ValueError(
                f"Campos de ficha sem destino relacional em {doc['relative_path']}: {sorted(unsupported_fields)}"
            )
        if isinstance(record.get("tipo"), str):
            type_values.add(record["tipo"])
        if isinstance(record.get("status_validacao"), str):
            validation_values.add(record["status_validacao"])
        if isinstance(record.get("abrangencia"), str):
            scope_values.add(record["abrangencia"])
        for source_field, vocab_name in CAT_FIELDS:
            value = record.get(source_field)
            if isinstance(value, str):
                vocab[vocab_name].append(value)
        location_keys = ("municipio", "uf", "pais")
        if any(key in record for key in location_keys):
            municipality = record.get("municipio")
            uf = record.get("uf")
            country = record.get("pais")
            level = (
                "municipio"
                if "municipio" in record
                else ("uf" if "uf" in record else "pais")
            )
            local_keys.add((municipality, uf, country, level))

    # Dimension IDs are also held in the persistent manifest.
    type_ids = {
        value: stable_id(manifest, f"tipo:{value}", "typ")
        for value in sorted(type_values)
    }
    validation_ids = {
        value: stable_id(manifest, f"status_validacao:{value}", "val")
        for value in sorted(validation_values)
    }
    category_ids: dict[str, dict[str, str]] = {}
    for vocab_name, values in vocab.items():
        category_ids[vocab_name] = {
            value: stable_id(manifest, f"{vocab_name}:{value}", "cat")
            for value in sorted(set(values))
        }
    scope_ids = {
        value: stable_id(manifest, f"abrangencia:{value}", "scp")
        for value in sorted(scope_values)
    }
    local_ids = {
        key: stable_id(manifest, "localidade:" + canonical_json(key), "loc")
        for key in sorted(local_keys, key=canonical_json)
    }

    # Main source records retain uncommon scalar attributes in dedicated columns.
    source_columns = [
        "id",
        "id_externo",
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
        "tipo_id",
        "status_triagem",
        "status_validacao_id",
    ]
    source_rows: list[dict[str, Any]] = []
    source_cat_rows: dict[str, list[dict[str, Any]]] = {name: [] for name in vocab}
    source_scope_rows: list[dict[str, Any]] = []
    source_location_rows: list[dict[str, Any]] = []
    source_provenance_rows: list[dict[str, Any]] = []
    source_url_rows: list[dict[str, Any]] = []
    for doc in source_docs:
        record = doc["content"]
        source_id = source_paths[doc["relative_path"]]
        row: dict[str, Any] = {"id": source_id}
        for field in SOURCE_SCALAR_FIELDS:
            row[field] = text_value(record.get(field))
        row.update(
            {
                "id_externo": record.get("id"),
                "tipo_id": type_ids.get(record.get("tipo")),
                "status_triagem": record.get("status_triagem"),
                "status_validacao_id": validation_ids.get(
                    record.get("status_validacao")
                ),
            }
        )
        source_rows.append(row)

        # Every URL is associated to the record that declared it; shared URLs stay repeated.
        main_url = record.get("url")
        identity = f"fonte:{doc['relative_path']}#/url"
        url_id = stable_id(manifest, identity, "url")
        source_url_rows.append(
            {
                "id": url_id,
                "fonte_id": source_id,
                "papel": "principal",
                "ordem": 0,
                "nome": None,
                "url": main_url,
            }
        )
        related = record.get("links_relacionados")
        if isinstance(related, list):
            for index, link in enumerate(related):
                if isinstance(link, dict):
                    url_value = link.get("url")
                    link_name = link.get("nome")
                else:
                    url_value = link
                    link_name = None
                related_identity = (
                    f"fonte:{doc['relative_path']}#/links_relacionados/{index}"
                )
                source_url_rows.append(
                    {
                        "id": stable_id(manifest, related_identity, "url"),
                        "fonte_id": source_id,
                        "papel": "relacionada",
                        "ordem": index,
                        "nome": link_name,
                        "url": url_value,
                    }
                )

        for source_field, vocab_name in CAT_FIELDS:
            value = record.get(source_field)
            if isinstance(value, str):
                source_cat_rows[vocab_name].append(
                    {
                        "fonte_id": source_id,
                        "categoria_id": category_ids[vocab_name][value],
                    }
                )
        scope = record.get("abrangencia")
        if isinstance(scope, str):
            source_scope_rows.append(
                {"fonte_id": source_id, "abrangencia_id": scope_ids[scope]}
            )
        if any(key in record for key in ("municipio", "uf", "pais")):
            location_key = (
                record.get("municipio"),
                record.get("uf"),
                record.get("pais"),
                "municipio"
                if "municipio" in record
                else ("uf" if "uf" in record else "pais"),
            )
            source_location_rows.append(
                {"fonte_id": source_id, "localidade_id": local_ids[location_key]}
            )
        for origin_field in ("origem", "origem_cadastro"):
            value = record.get(origin_field)
            if isinstance(value, str):
                source_provenance_rows.append(
                    {
                        "fonte_id": source_id,
                        "tipo_origem": origin_field,
                        "valor_original": value,
                    }
                )

    # Collect structured object arrays in inventory JSON and group by the actual field family.
    families: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    collection_pointers: dict[str, set[str]] = defaultdict(set)
    inventory_elements: list[dict[str, Any]] = []
    inventory_metadata: list[dict[str, Any]] = []
    inventory_rows: list[dict[str, Any]] = []
    inventory_record_counts: Counter[str] = Counter()
    array_element_count = 0

    for doc in inventory_docs:
        inventory_id = inventory_ids[doc["relative_path"]]
        root_obj = doc["content"] if isinstance(doc["content"], dict) else {}
        inventory_rows.append(
            {
                "id": inventory_id,
                "caminho_origem": doc["relative_path"],
                "titulo": root_obj.get("titulo")
                if isinstance(root_obj.get("titulo"), str)
                else Path(doc["relative_path"]).stem,
                "atualizado_em": root_obj.get("atualizado_em"),
                "sha256": doc["sha256"],
            }
        )
        object_arrays: list[tuple[list[Any], list[dict[str, Any]]]] = []

        def find_object_arrays(value: Any, parts: list[Any] | None = None):
            parts = parts or []
            if isinstance(value, dict):
                for key, child in value.items():
                    find_object_arrays(child, parts + [key])
            elif isinstance(value, list):
                if value and all(isinstance(item, dict) for item in value):
                    object_arrays.append((parts, value))
                for index, child in enumerate(value):
                    if isinstance(child, (dict, list)):
                        find_object_arrays(child, parts + [index])

        find_object_arrays(doc["content"])
        for parts, records in object_arrays:
            collection_pointer = json_pointer(parts)
            collection_pointers[doc["relative_path"]].add(collection_pointer)
            keys = tuple(sorted({key for item in records for key in item}))
            family = keys
            collection_path = "/" + "/".join(
                str(part) for part in parts if not isinstance(part, int)
            )
            for index, item in enumerate(records):
                pointer = json_pointer(parts + [index])
                file_reference = item.get("arquivo")
                linked_source_id = source_reference(file_reference, source_paths)
                row = {
                    "id": stable_id(
                        manifest, f"item:{doc['relative_path']}#{pointer}", "item"
                    ),
                    "inventario_id": inventory_id,
                    "caminho_colecao": collection_path,
                    "json_pointer": pointer,
                    "arquivo_referenciado": file_reference,
                    "fonte_id": linked_source_id,
                }
                row.update({key: item.get(key) for key in keys})
                families[family].append(row)
                inventory_record_counts[doc["relative_path"]] += 1

        # Root scalar metadata outside collection arrays is represented explicitly; compound values
        # remain JSON-typed in this auxiliary inventory metadata relation and in the original file.
        object_item_pointers = {
            json_pointer(array_parts + [index])
            for array_parts, records in object_arrays
            for index, _ in enumerate(records)
        }

        def add_inventory_metadata(value: Any, parts: list[Any] | None = None):
            parts = parts or []
            pointer = json_pointer(parts)
            if pointer in object_item_pointers:
                return
            if isinstance(value, dict):
                for key, child in value.items():
                    child_parts = parts + [key]
                    child_pointer = json_pointer(child_parts)
                    if not parts and key in {"titulo", "atualizado_em"}:
                        continue
                    if isinstance(child, list):
                        continue  # lists are represented by collection/element resources
                    if isinstance(child, dict):
                        add_inventory_metadata(child, child_parts)
                    else:
                        inventory_metadata.append(
                            {
                                "id": stable_id(
                                    manifest,
                                    f"inventario_meta:{doc['relative_path']}#{child_pointer}",
                                    "meta",
                                ),
                                "inventario_id": inventory_id,
                                "json_pointer": child_pointer,
                                "campo": str(key),
                                "tipo_valor": json_type(child),
                                "valor_json": canonical_json(child),
                            }
                        )

        add_inventory_metadata(doc["content"])

        # Preserve every primitive/mixed list element by its JSON Pointer, excluding object arrays
        # represented by their family-specific relational CSV.
        for parts, values in inventory_walk(doc["content"]):
            pointer = json_pointer(parts)
            if pointer in collection_pointers[doc["relative_path"]]:
                continue
            for index, value in enumerate(values):
                element_pointer = json_pointer(parts + [index])
                if isinstance(value, dict) and any(
                    element_pointer == json_pointer(array_parts + [n])
                    for array_parts, records in object_arrays
                    for n, _ in enumerate(records)
                ):
                    continue
                inventory_elements.append(
                    {
                        "id": stable_id(
                            manifest,
                            f"inventario_elemento:{doc['relative_path']}#{element_pointer}",
                            "elem",
                        ),
                        "inventario_id": inventory_id,
                        "json_pointer_pai": pointer,
                        "ordem": index,
                        "json_pointer": element_pointer,
                        "tipo_valor": json_type(value),
                        "valor_json": canonical_json(value),
                    }
                )
                array_element_count += 1

    resources: list[dict[str, Any]] = []
    resource_counts: dict[str, int] = {}

    def emit(
        name: str,
        columns: list[str],
        rows: list[dict[str, Any]],
        pk: list[str],
        types=None,
        desc=None,
        foreign_keys=None,
        required=None,
        source_fields=None,
        categories=None,
        json_fields=None,
    ):
        path = f"{DATA_DIR}/{name}.csv"
        rows.sort(
            key=lambda row: tuple(
                str(row.get(key) if row.get(key) is not None else NULL) for key in pk
            )
        )
        row_types = type_map(rows, columns, types)
        resource_descriptor = resource(
            name,
            path,
            columns,
            row_types,
            desc or {col: col.replace("_", " ") for col in columns},
            pk,
            foreign_keys,
            set(required or []),
        )
        if source_fields:
            for field in resource_descriptor["schema"]["fields"]:
                if field["name"] in source_fields:
                    field["sourceField"] = source_fields[field["name"]]
        if categories:
            for field in resource_descriptor["schema"]["fields"]:
                if field["name"] in categories:
                    field["categories"] = categories[field["name"]]
        if json_fields:
            for field in resource_descriptor["schema"]["fields"]:
                if field["name"] in json_fields:
                    field["sourceEncoding"] = "json"
        resources.append(resource_descriptor)
        resource_counts[name] = write_csv(package_dir / path, columns, rows)

    string_cols = {col: "string" for col in source_columns}
    emit(
        "fonte",
        source_columns,
        source_rows,
        ["id"],
        string_cols,
        {
            "id": "ID persistente da ficha",
            "id_externo": "Identificador externo legado, quando existente",
            "nome": "Nome literal da ficha",
            "descricao": "Descrição literal da ficha",
            "status_triagem": "Triagem editorial; null significa não informado",
            "status_validacao_id": "Status legado de validação, sem interpretação adicional",
        },
        [
            fk("tipo_id", "tipo", "id"),
            fk("status_validacao_id", "status_validacao", "id"),
        ],
        ["id", "nome"],
    )

    emit(
        "tipo",
        ["id", "nome"],
        [{"id": type_ids[v], "nome": v} for v in sorted(type_values)],
        ["id"],
        {"id": "string", "nome": "string"},
        {"id": "ID persistente", "nome": "Rótulo original de tipo"},
        required=["id", "nome"],
    )
    emit(
        "status_validacao",
        ["id", "valor_original"],
        [
            {"id": validation_ids[v], "valor_original": v}
            for v in sorted(validation_values)
        ],
        ["id"],
        {"id": "string", "valor_original": "string"},
        {"id": "ID persistente", "valor_original": "Texto original do status"},
        required=["id", "valor_original"],
    )

    for vocab_name, _ in ((name, label) for label, name in CAT_FIELDS):
        label_col = "nome" if vocab_name == "categoria" else "valor_original"
        table_name = vocab_name
        values = sorted(category_ids[vocab_name])
        emit(
            table_name,
            ["id", label_col],
            [
                {"id": category_ids[vocab_name][value], label_col: value}
                for value in values
            ],
            ["id"],
            {"id": "string", label_col: "string"},
            {
                "id": "ID persistente",
                label_col: "Termo literal; sem equivalência presumida",
            },
            required=["id", label_col],
        )
        relation_name = {
            "categoria": "fonte_categoria",
            "categoria_original": "fonte_categoria_original",
            "categoria_curadoria": "fonte_categoria_curadoria",
        }[vocab_name]
        relation_rows = source_cat_rows[vocab_name]
        emit(
            relation_name,
            ["fonte_id", "categoria_id"],
            relation_rows,
            ["fonte_id", "categoria_id"],
            {"fonte_id": "string", "categoria_id": "string"},
            {
                "fonte_id": "Ficha relacionada",
                "categoria_id": "Termo da taxonomia original correspondente",
            },
            [fk("fonte_id", "fonte", "id"), fk("categoria_id", table_name, "id")],
            ["fonte_id", "categoria_id"],
        )

    emit(
        "abrangencia",
        ["id", "valor_original"],
        [{"id": scope_ids[v], "valor_original": v} for v in sorted(scope_values)],
        ["id"],
        {"id": "string", "valor_original": "string"},
        {
            "id": "ID persistente",
            "valor_original": "Abrangência original, sem parsing heurístico",
        },
        required=["id", "valor_original"],
    )
    emit(
        "fonte_abrangencia",
        ["fonte_id", "abrangencia_id"],
        source_scope_rows,
        ["fonte_id", "abrangencia_id"],
        {"fonte_id": "string", "abrangencia_id": "string"},
        foreign_keys=[
            fk("fonte_id", "fonte", "id"),
            fk("abrangencia_id", "abrangencia", "id"),
        ],
        required=["fonte_id", "abrangencia_id"],
    )

    local_rows = []
    for key, location_id in local_ids.items():
        municipality, uf, country, level = key
        local_rows.append(
            {
                "id": location_id,
                "nivel": level,
                "municipio": municipality,
                "uf": uf,
                "pais": country,
            }
        )
    emit(
        "localidade",
        ["id", "nivel", "municipio", "uf", "pais"],
        local_rows,
        ["id"],
        {
            "id": "string",
            "nivel": "string",
            "municipio": "string",
            "uf": "string",
            "pais": "string",
        },
        {
            "id": "ID persistente do conjunto literal de valores",
            "nivel": "Campo geográfico explícito mais específico presente",
            "municipio": "Valor legado, sem correção ortográfica",
            "uf": "Valor legado, inclusive string vazia",
            "pais": "Valor legado, sem inferência",
        },
        required=["id", "nivel"],
    )
    emit(
        "fonte_localidade",
        ["fonte_id", "localidade_id"],
        source_location_rows,
        ["fonte_id", "localidade_id"],
        {"fonte_id": "string", "localidade_id": "string"},
        foreign_keys=[
            fk("fonte_id", "fonte", "id"),
            fk("localidade_id", "localidade", "id"),
        ],
        required=["fonte_id", "localidade_id"],
    )

    origin_rows = sorted(
        source_provenance_rows,
        key=lambda row: (row["fonte_id"], row["tipo_origem"], row["valor_original"]),
    )
    emit(
        "fonte_origem",
        ["fonte_id", "tipo_origem", "valor_original"],
        origin_rows,
        ["fonte_id", "tipo_origem"],
        {"fonte_id": "string", "tipo_origem": "string", "valor_original": "string"},
        {
            "fonte_id": "Ficha de origem",
            "tipo_origem": "Campo de origem (origem ou origem_cadastro)",
            "valor_original": "Conteúdo exato do campo",
        },
        [fk("fonte_id", "fonte", "id")],
        ["fonte_id", "tipo_origem"],
        categories={"tipo_origem": ["origem", "origem_cadastro"]},
    )
    emit(
        "fonte_url",
        ["id", "fonte_id", "papel", "ordem", "nome", "url"],
        source_url_rows,
        ["id"],
        {
            "id": "string",
            "fonte_id": "string",
            "papel": "string",
            "ordem": "integer",
            "nome": "string",
            "url": "string",
        },
        {
            "id": "ID persistente da declaração de URL",
            "fonte_id": "Ficha que declarou o endereço",
            "papel": "URL principal ou relacionada",
            "ordem": "Posição no documento original",
            "nome": "Rótulo original do link relacionado",
            "url": "URL literal, sem normalização",
        },
        [fk("fonte_id", "fonte", "id")],
        ["id", "fonte_id", "papel", "url"],
        categories={"papel": ["principal", "relacionada"]},
    )

    emit(
        "inventario",
        ["id", "caminho_origem", "titulo", "atualizado_em", "sha256"],
        inventory_rows,
        ["id"],
        {
            "id": "string",
            "caminho_origem": "string",
            "titulo": "string",
            "atualizado_em": "string",
            "sha256": "string",
        },
        {
            "id": "ID persistente do documento de inventário",
            "caminho_origem": "Caminho relativo do JSON original",
            "titulo": "Título declarado ou nome do arquivo",
            "atualizado_em": "Valor declarado no documento",
            "sha256": "Hash dos bytes originais",
        },
        required=["id", "caminho_origem", "titulo", "sha256"],
    )
    emit(
        "inventario_metadado",
        ["id", "inventario_id", "json_pointer", "campo", "tipo_valor", "valor_json"],
        inventory_metadata,
        ["id"],
        {
            "id": "string",
            "inventario_id": "string",
            "json_pointer": "string",
            "campo": "string",
            "tipo_valor": "string",
            "valor_json": "string",
        },
        {
            "id": "ID persistente do metadado",
            "inventario_id": "Documento de inventário",
            "json_pointer": "Ponteiro para o valor no JSON",
            "campo": "Nome original do atributo",
            "tipo_valor": "Tipo JSON original",
            "valor_json": "Valor serializado como JSON canônico",
        },
        [fk("inventario_id", "inventario", "id")],
        ["id", "inventario_id", "json_pointer", "campo", "valor_json"],
    )
    emit(
        "inventario_elemento",
        [
            "id",
            "inventario_id",
            "json_pointer_pai",
            "ordem",
            "json_pointer",
            "tipo_valor",
            "valor_json",
        ],
        inventory_elements,
        ["id"],
        {
            "id": "string",
            "inventario_id": "string",
            "json_pointer_pai": "string",
            "ordem": "integer",
            "json_pointer": "string",
            "tipo_valor": "string",
            "valor_json": "string",
        },
        {
            "id": "ID persistente do elemento",
            "inventario_id": "Documento de inventário",
            "json_pointer_pai": "Caminho da lista no JSON",
            "ordem": "Índice na lista original",
            "json_pointer": "Ponteiro para o elemento",
            "tipo_valor": "Tipo JSON original",
            "valor_json": "Valor em JSON canônico",
        },
        [fk("inventario_id", "inventario", "id")],
        ["id", "inventario_id", "json_pointer", "tipo_valor", "valor_json"],
    )

    emit(
        "item_todo",
        [
            "id",
            "tipo_item",
            "secao",
            "titulo",
            "descricao",
            "status_triagem",
            "concluido",
            "nota_triagem",
        ],
        todo_items,
        ["id"],
        {
            "id": "string",
            "tipo_item": "string",
            "secao": "string",
            "titulo": "string",
            "descricao": "string",
            "status_triagem": "string",
            "concluido": "boolean",
            "nota_triagem": "string",
        },
        {
            "id": "ID persistente do item de backlog",
            "tipo_item": "Objetivo, referência de implementação ou atividade",
            "secao": "Seção de origem no TODO.md",
            "titulo": "Título ou texto original do item",
            "descricao": "Descrição literal das abordagens e avaliações",
            "status_triagem": "Triagem editorial do item",
            "concluido": "Estado da caixa de seleção de atividade; nulo para objetivo e referência",
            "nota_triagem": "Nota que limita o uso das referências",
        },
        required=["id", "tipo_item", "secao", "titulo", "status_triagem"],
        categories={
            "tipo_item": ["contexto", "objetivo", "referencia", "atividade"],
            "status_triagem": ["pendente"],
        },
    )
    emit(
        "todo_url",
        ["id", "todo_item_id", "rotulo", "endereco", "tipo_endereco"],
        todo_urls,
        ["id"],
        {
            "id": "string",
            "todo_item_id": "string",
            "rotulo": "string",
            "endereco": "string",
            "tipo_endereco": "string",
        },
        {
            "id": "ID persistente do link no backlog",
            "todo_item_id": "Item TODO que cita o endereço",
            "rotulo": "Texto do rótulo original",
            "endereco": "URL absoluta ou caminho relativo citado no TODO.md",
            "tipo_endereco": "Identifica URL externa ou arquivo relativo do repositório",
        },
        [fk("todo_item_id", "item_todo", "id")],
        ["id", "todo_item_id", "rotulo", "endereco", "tipo_endereco"],
        categories={"tipo_endereco": ["url", "arquivo"]},
    )

    inventory_item_rows = [row for rows in families.values() for row in rows]
    payload_fields = sorted({field for family in families for field in family})
    base_columns = [
        "id",
        "inventario_id",
        "caminho_colecao",
        "json_pointer",
        "arquivo_referenciado",
        "fonte_id",
    ]
    output_names = {
        field: (f"legado_{field}" if field in base_columns else field)
        for field in payload_fields
    }
    columns = base_columns + [output_names[field] for field in payload_fields]
    payload_types: dict[str, str] = {}
    json_encoded_fields: set[str] = set()
    for field in payload_fields:
        all_values = [row.get(field) for row in inventory_item_rows]
        if nested_value(all_values):
            payload_types[output_names[field]] = "string"
            json_encoded_fields.add(output_names[field])
        else:
            payload_types[output_names[field]] = field_type(all_values)
    item_csv_rows = []
    for row in inventory_item_rows:
        csv_row = {key: row.get(key) for key in base_columns}
        csv_row.update(
            {
                output_names[field]: canonical_json(row.get(field))
                if output_names[field] in json_encoded_fields
                and row.get(field) is not None
                else row.get(field)
                for field in payload_fields
            }
        )
        item_csv_rows.append(csv_row)
    emit(
        "inventario_item",
        columns,
        item_csv_rows,
        ["id"],
        {
            "id": "string",
            "inventario_id": "string",
            "caminho_colecao": "string",
            "json_pointer": "string",
            "arquivo_referenciado": "string",
            "fonte_id": "string",
            **payload_types,
        },
        {
            "id": "ID persistente do item de inventário",
            "inventario_id": "Documento de inventário que contém o item",
            "caminho_colecao": "Caminho da coleção declarada no documento",
            "json_pointer": "Ponteiro do item no documento original",
            "arquivo_referenciado": "Referência literal a arquivo, quando declarada",
            "fonte_id": "Ficha vinculada somente quando há referência exata verificável",
            **{
                output_names[
                    field
                ]: f"Valor original do campo {field}; objetos/listas são JSON canônico"
                for field in payload_fields
            },
        },
        [fk("inventario_id", "inventario", "id"), fk("fonte_id", "fonte", "id")],
        ["id", "inventario_id", "json_pointer"],
        {output_names[field]: field for field in payload_fields},
        json_fields=json_encoded_fields,
    )
    family_stats = {
        "schema_families": len(families),
        "resources": 1,
        "records": len(inventory_item_rows),
        "fields": payload_fields,
    }

    # Original-document provenance index covers every scanned JSON exactly once.
    provenance_rows = []
    for doc in docs:
        provenance_rows.append(
            {
                "id": stable_id(manifest, f"documento:{doc['relative_path']}", "doc"),
                "caminho_origem": doc["relative_path"],
                "sha256": doc["sha256"],
                "tipo_documento": doc["kind"],
                "fonte_id": source_paths.get(doc["relative_path"]),
                "inventario_id": inventory_ids.get(doc["relative_path"]),
                "tipo_json_raiz": json_type(doc["content"]),
                "quantidade_atributos_raiz": len(doc["content"])
                if isinstance(doc["content"], dict)
                else None,
            }
        )
    emit(
        "registro_original",
        [
            "id",
            "caminho_origem",
            "sha256",
            "tipo_documento",
            "fonte_id",
            "inventario_id",
            "tipo_json_raiz",
            "quantidade_atributos_raiz",
        ],
        provenance_rows,
        ["id"],
        {
            "id": "string",
            "caminho_origem": "string",
            "sha256": "string",
            "tipo_documento": "string",
            "fonte_id": "string",
            "inventario_id": "string",
            "tipo_json_raiz": "string",
            "quantidade_atributos_raiz": "integer",
        },
        {
            "id": "ID persistente do documento original",
            "caminho_origem": "Caminho relativo para recuperação dos bytes originais",
            "sha256": "SHA-256 dos bytes originais",
            "tipo_documento": "Ficha individual ou inventário composto",
            "fonte_id": "Ficha importada, quando aplicável",
            "inventario_id": "Inventário importado, quando aplicável",
            "tipo_json_raiz": "Tipo JSON da raiz",
            "quantidade_atributos_raiz": "Número de campos na raiz objeto",
        },
        [fk("fonte_id", "fonte", "id"), fk("inventario_id", "inventario", "id")],
        ["id", "caminho_origem", "sha256", "tipo_documento"],
    )

    # Deterministic inventory and provenance report.
    source_field_types: dict[str, Counter[str]] = defaultdict(Counter)
    attribute_occurrences: Counter[str] = Counter()
    for doc in docs:
        content = doc["content"]
        if isinstance(content, dict):
            for key, value in content.items():
                if doc["kind"] == "fonte":
                    attribute_occurrences[key] += 1
                    source_field_types[key][json_type(value)] += 1
    exact_hashes: Counter[str] = Counter()
    source_urls: Counter[str] = Counter()
    source_names: Counter[str] = Counter()
    source_structures: Counter[str] = Counter()
    total_array_items = sum(
        len(values)
        for doc in inventory_docs
        for _, values in inventory_walk(doc["content"])
    )
    for doc in source_docs:
        exact_hashes[sha256_bytes(canonical_json(doc["content"]).encode("utf-8"))] += 1
        if isinstance(doc["content"].get("url"), str):
            source_urls[doc["content"]["url"]] += 1
        if isinstance(doc["content"].get("nome"), str):
            source_names[doc["content"]["nome"]] += 1
        source_structures[canonical_json(sorted(doc["content"].keys()))] += 1
    duplicate_exact_groups = sum(1 for count in exact_hashes.values() if count > 1)
    duplicate_url_groups = sum(1 for count in source_urls.values() if count > 1)
    attribute_report = {
        key: {
            "occurrences": count,
            "types": dict(sorted(source_field_types[key].items())),
        }
        for key, count in sorted(attribute_occurrences.items())
    }
    report = {
        "json_files_discovered": len(paths),
        "json_files_processed": len(docs),
        "parse_errors": parse_errors,
        "individual_source_records": len(source_docs),
        "inventory_documents": len(inventory_docs),
        "source_attribute_names": len(attribute_report),
        "source_attribute_occurrences": attribute_report,
        "source_record_structures": len(source_structures),
        "inventory_collection_schema_families": len(families),
        "inventory_item_resources": 1,
        "inventory_object_records": sum(len(rows) for rows in families.values()),
        "inventory_array_elements": array_element_count,
        "inventory_array_items_total": total_array_items,
        "todo_items": len(todo_items),
        "todo_urls": len(todo_urls),
        "generated_csv_row_counts": dict(sorted(resource_counts.items())),
        "distinct_categories": {
            name: len(values) for name, values in sorted(category_ids.items())
        },
        "distinct_types": len(type_values),
        "distinct_validation_status_texts": len(validation_values),
        "distinct_scope_strings": len(scope_values),
        "url_relationships": len(source_url_rows),
        "distinct_source_urls": len(source_urls),
        "potential_exact_duplicate_groups": duplicate_exact_groups,
        "identical_source_name_groups": sum(
            1 for count in source_names.values() if count > 1
        ),
        "duplicate_source_url_groups": duplicate_url_groups,
        "duplicate_source_url_excess_records": sum(
            count - 1 for count in source_urls.values() if count > 1
        ),
        "inventory_collection_resources": family_stats,
        "source_root_field_occurrences": dict(sorted(attribute_occurrences.items())),
        "migration_notes": [
            "Nenhuma ficha foi deduplicada. URLs compartilhadas são mantidas como relações distintas.",
            "Os 20 inventários permanecem documentos compostos; itens aninhados são recursos de inventário, não novas fontes.",
            "Os itens de inventário são consolidados em inventario_item.csv sem deduplicação.",
            "Os JSON legados são removidos após o corte; caminhos e hashes permanecem em registro_original.csv.",
            "status_triagem permanece nulo quando não foi declarado na origem.",
        ],
    }

    descriptor = {
        "$schema": PROFILE_V2,
        "name": "osint-rondonia-catalogo-relacional",
        "title": "Catálogo OSINT Rondônia — tabelas relacionais",
        "description": (
            "Catálogo de fichas OSINT e inventários compostos de Rondônia em CSV relacionais. "
            "Dados de terceiros mantêm as condições e licenças declaradas em suas fontes; a licença AGPL do repositório aplica-se ao código. "
            "O token \\N representa valor nulo. Strings vazias permanecem distintas. Caminhos e hashes legados estão em registro_original.csv."
        ),
        "homepage": "https://github.com/Rondoscopio/osint-rondonia",
        "version": "1.0.0",
        "profile": "data-package",
        "resources": resources,
    }
    descriptor_path = package_dir / "datapackage.json"
    descriptor_path.write_text(
        json.dumps(descriptor, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    manifest_path.write_text(
        json.dumps(
            {
                "version": 1,
                "id_strategy": "persistent-sha256-of-source-identity",
                "ids": dict(sorted(manifest.items())),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    report_path = (
        package_dir / ".local" / "share" / "osint-rondonia" / "migration_report.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Raiz dos JSON legados",
    )
    parser.add_argument(
        "--package-dir",
        type=Path,
        default=None,
        help="Destino do Data Package (padrão: raiz)",
    )
    args = parser.parse_args()
    package_dir = args.package_dir or args.root
    try:
        report = migration(args.root, package_dir)
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "json_processados": report["json_files_processed"],
                "fichas": report["individual_source_records"],
                "inventarios": report["inventory_documents"],
                "itens_de_inventario": report["inventory_object_records"],
                "csv": len(report["generated_csv_row_counts"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
