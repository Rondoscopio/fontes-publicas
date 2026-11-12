from __future__ import annotations

import csv
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from catalogo import NULL, write_csv  # noqa: E402
from migrate_legacy import migration  # noqa: E402
from cutover_csv_only import cutover  # noqa: E402
from export_sqlite import export_to_path  # noqa: E402
from validate_package import decode, validate  # noqa: E402


def create_legacy_fixture(root: Path) -> None:
    (root / "records").mkdir(parents=True)
    (root / "inventarios").mkdir()
    (root / "records" / "source.json").write_text(
        json.dumps(
            {
                "nome": "Fonte de teste",
                "url": "https://example.org/?a=1&b=2",
                "descricao": 'vírgula, aspas " e\nlinha',
                "tipo": "referencia_tecnica",
                "categoria": "Dados abertos",
                "categoria_original": "Original",
                "categoria_curadoria": "Pesquisa",
                "abrangencia": "Brasil",
                "origem": "catálogo de teste",
                "status_validacao": "nao_verificado",
                "links_relacionados": [
                    {"nome": "Doc", "url": "https://example.org/docs"}
                ],
                "uf": "",
                "status_triagem": "pendente",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (root / "inventarios" / "completo.json").write_text(
        json.dumps(
            {
                "titulo": "Inventário de teste",
                "fontes": [
                    {
                        "nome": "item",
                        "arquivo": "records/source.json",
                        "url": "https://example.org",
                    }
                ],
                "criterios": ["um", "dois"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (root / "TODO.md").write_text(
        "# TODO\n\nContexto do catálogo.\n\n## Catálogo web pesquisável\n\nCriar interface pública.\n\n"
        "### Projetos de referência para estudar\n\nDois links de exemplo.\n\n#### Referências\n\n"
        "- **Projeto de teste**\n  - Site: https://example.org\n  - Estudar: busca.\n\n### Atividades\n\n- [ ] Conferir referência.\n\n"
        "Os links acima são referências para avaliação, não dependências aprovadas nem fontes de investigação já auditadas.\n",
        encoding="utf-8",
    )


class CatalogPackageTests(unittest.TestCase):
    def test_package_integrity(self):
        result = validate(ROOT)
        self.assertEqual(
            result["resources"],
            len(json.loads((ROOT / "datapackage.json").read_text())["resources"]),
        )
        self.assertEqual(result["rows_fonte"], 4571)
        self.assertEqual(result["rows_inventario"], 20)
        self.assertEqual(result["rows_registro_original"], 4591)
        self.assertEqual(result["rows_item_todo"], 21)
        self.assertEqual(result["rows_todo_url"], 17)

    def test_todo_entries_and_links_are_exported_pending(self):
        with (ROOT / "data" / "item_todo.csv").open(
            encoding="utf-8", newline=""
        ) as stream:
            actual_items = list(csv.DictReader(stream))
        with (ROOT / "data" / "todo_url.csv").open(
            encoding="utf-8", newline=""
        ) as stream:
            actual_urls = list(csv.DictReader(stream))
        self.assertEqual(len(actual_items), 21)
        self.assertEqual(len(actual_urls), 17)
        self.assertTrue(
            all(row["status_triagem"] == "pendente" for row in actual_items)
        )
        self.assertEqual(
            sum(row["tipo_item"] == "referencia" for row in actual_items), 7
        )
        self.assertEqual(
            sum(row["tipo_item"] == "atividade" for row in actual_items), 12
        )
        self.assertEqual(
            sum(row["tipo_endereco"] == "arquivo" for row in actual_urls), 1
        )

    def test_import_is_reproducible_and_ids_are_stable(self):
        with tempfile.TemporaryDirectory() as tmp:
            legacy = Path(tmp) / "legacy"
            legacy.mkdir()
            create_legacy_fixture(legacy)
            first = Path(tmp) / "first"
            second = Path(tmp) / "second"
            migration(legacy, first)
            first_files = {
                p.relative_to(first).as_posix(): p.read_bytes()
                for p in first.rglob("*")
                if p.is_file()
            }
            migration(
                legacy, first
            )  # Existing manifest must preserve IDs and stable output.
            first_replay = {
                p.relative_to(first).as_posix(): p.read_bytes()
                for p in first.rglob("*")
                if p.is_file()
            }
            migration(legacy, second)
            second_files = {
                p.relative_to(second).as_posix(): p.read_bytes()
                for p in second.rglob("*")
                if p.is_file()
            }
            self.assertEqual(first_files, first_replay)
            self.assertEqual(first_files.keys(), second_files.keys())
            for name in first_files:
                self.assertEqual(first_files[name], second_files[name], name)
            validate(first, verify_originals=True, root=legacy)

    def test_migration_refuses_to_regenerate_without_legacy_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "empty"
            root.mkdir()
            with self.assertRaisesRegex(ValueError, "Nenhum JSON legado encontrado"):
                migration(root, Path(tmp) / "package")

    def test_cutover_audits_then_removes_legacy_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "legacy"
            package = Path(tmp) / "package"
            root.mkdir()
            create_legacy_fixture(root)
            migration(root, package)
            result = cutover(root, package)
            self.assertEqual(result["json_deleted"], 2)
            self.assertEqual(result["todo_deleted"], 1)
            self.assertFalse(list(root.rglob("*.json")))
            self.assertFalse((root / "TODO.md").exists())
            self.assertTrue((package / "datapackage.json").exists())
            with (package / "data" / "cutover_audit.csv").open(
                encoding="utf-8", newline=""
            ) as stream:
                audit = list(csv.DictReader(stream))
            self.assertEqual(len(audit), 3)
            self.assertTrue(all(row["deleted"] == "true" for row in audit))
            validate(package)

    def test_sqlite_export_preserves_tables_relations_and_is_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "legacy"
            package = Path(tmp) / "package"
            root.mkdir()
            create_legacy_fixture(root)
            migration(root, package)
            first = Path(tmp) / "first.sqlite"
            second = Path(tmp) / "second.sqlite"
            first_counts = export_to_path(package, first)
            second_counts = export_to_path(package, second)
            self.assertEqual(first_counts, second_counts)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            import sqlite3

            with sqlite3.connect(first) as connection:
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM fonte").fetchone()[0], 1
                )
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM inventario").fetchone()[0],
                    1,
                )
                source = connection.execute(
                    "SELECT l.uf, f.descricao, f.status_triagem "
                    "FROM fonte f JOIN fonte_localidade fl ON fl.fonte_id = f.id "
                    "JOIN localidade l ON l.id = fl.localidade_id"
                ).fetchone()
                self.assertEqual(source, ("", 'vírgula, aspas " e\nlinha', "pendente"))
                self.assertEqual(
                    connection.execute("PRAGMA foreign_key_check").fetchall(), []
                )
                self.assertEqual(
                    connection.execute("PRAGMA integrity_check").fetchone()[0], "ok"
                )
                self.assertGreater(
                    len(
                        connection.execute(
                            "PRAGMA foreign_key_list(fonte_url)"
                        ).fetchall()
                    ),
                    0,
                )
                self.assertGreater(
                    connection.execute("SELECT COUNT(*) FROM fonte_url").fetchone()[0],
                    0,
                )

    def test_failed_sqlite_export_keeps_previous_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "legacy"
            package = Path(tmp) / "package"
            root.mkdir()
            create_legacy_fixture(root)
            migration(root, package)
            output = Path(tmp) / "published.sqlite"
            output.write_bytes(b"previous-good-artifact")
            source_csv = package / "data" / "fonte.csv"
            with source_csv.open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            rows[0]["id"] = NULL
            with source_csv.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(
                    stream, fieldnames=rows[0].keys(), lineterminator="\r\n"
                )
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaises(ValueError):
                export_to_path(package, output)
            self.assertEqual(output.read_bytes(), b"previous-good-artifact")
            self.assertFalse(output.with_suffix(".sqlite.tmp").exists())

    def test_csv_row_reordering_does_not_break_relations(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "package"
            package.mkdir()
            shutil.copy2(ROOT / "datapackage.json", package / "datapackage.json")
            shutil.copytree(ROOT / "data", package / "data")
            csv_path = package / "data" / "fonte.csv"
            with csv_path.open(encoding="utf-8", newline="") as stream:
                reader = csv.DictReader(stream)
                columns = reader.fieldnames
                rows = list(reader)
            with csv_path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(
                    stream, fieldnames=columns, lineterminator="\r\n"
                )
                writer.writeheader()
                writer.writerows(reversed(rows))
            validate(package)

    def test_invalid_foreign_key_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "package"
            package.mkdir()
            shutil.copy2(ROOT / "datapackage.json", package / "datapackage.json")
            shutil.copytree(ROOT / "data", package / "data")
            csv_path = package / "data" / "fonte_categoria.csv"
            with csv_path.open(encoding="utf-8", newline="") as stream:
                reader = csv.DictReader(stream)
                columns = reader.fieldnames
                rows = list(reader)
            rows[0]["categoria_id"] = "cat-nao-existe"
            with csv_path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(
                    stream, fieldnames=columns, lineterminator="\r\n"
                )
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "FK órfã"):
                validate(package)

    def test_rfc4180_and_missing_value_round_trip(self):
        values = [
            'vírgula, aspas " duplas\ne Unicode: Rondônia',
            "",
            None,
            r"\\N literal",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "roundtrip.csv"
            write_csv(path, ["valor"], [{"valor": value} for value in values])
            raw_csv = path.read_bytes()
            with path.open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
        self.assertEqual([decode(row["valor"], "string") for row in rows], values)
        self.assertIn(b'"v\xc3\xadrgula, aspas "" duplas\n', raw_csv)

    def test_reserved_null_token_collision_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "reservado para nulo"):
                write_csv(Path(tmp) / "collision.csv", ["valor"], [{"valor": NULL}])

    def test_invalid_legacy_json_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "legacy"
            package = Path(tmp) / "package"
            root.mkdir()
            (root / "quebrado.json").write_text('{"nome":', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "JSON inválidos"):
                migration(root, package)

    def test_unmapped_source_field_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "legacy"
            package = Path(tmp) / "package"
            root.mkdir()
            (root / "fonte.json").write_text(
                json.dumps(
                    {
                        "nome": "Fonte",
                        "url": "https://example.org",
                        "campo_novo": "valor",
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ValueError, "Campos de ficha sem destino relacional"
            ):
                migration(root, package)


if __name__ == "__main__":
    unittest.main()
