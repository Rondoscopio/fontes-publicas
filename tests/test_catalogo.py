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

from export_sqlite import export_to_path  # noqa: E402
from validate_package import NULL, validate  # noqa: E402


class CatalogPackageTests(unittest.TestCase):
    def test_package_integrity(self):
        result = validate(ROOT)
        self.assertEqual(
            result["resources"],
            len(json.loads((ROOT / "datapackage.json").read_text())["resources"]),
        )
        self.assertEqual(result["rows_fonte"], 4578)
        self.assertEqual(result["rows_inventario"], 20)
        self.assertEqual(result["rows_inventario_item"], 7749)
        self.assertEqual(result["rows_registro_original"], 4591)
        self.assertEqual(result["rows_fonte_url"], 4600)
        self.assertEqual(result["rows_fonte_origem"], 2390)
        self.assertNotIn("rows_item_todo", result)
        self.assertNotIn("rows_todo_url", result)
        self.assertEqual(
            sum(row["fonte_id"] != NULL for row in self.read_table("inventario_item")),
            5551,
        )

    @staticmethod
    def read_table(name: str) -> list[dict[str, str]]:
        with (ROOT / "data" / f"{name}.csv").open(
            encoding="utf-8", newline=""
        ) as stream:
            return list(csv.DictReader(stream))

    def test_todo_sources_links_and_inventory_reference_are_in_catalog(self):
        todo_source_rows = [
            row for row in self.read_table("fonte") if row["id"].startswith("todo-")
        ]
        self.assertEqual(len(todo_source_rows), 7)
        self.assertTrue(
            all(row["status_triagem"] == "pendente" for row in todo_source_rows)
        )
        self.assertTrue(all(row["tipo_id"] == NULL for row in todo_source_rows))
        self.assertTrue(
            all(row["status_validacao_id"] == NULL for row in todo_source_rows)
        )
        todo_source_ids = {row["id"] for row in todo_source_rows}
        todo_source_urls = [
            row
            for row in self.read_table("fonte_url")
            if row["fonte_id"] in todo_source_ids
        ]
        self.assertEqual(len(todo_source_urls), 16)
        self.assertEqual(
            sum(row["papel"] == "principal" for row in todo_source_urls), 7
        )
        todo_sections = [
            row
            for row in self.read_table("fonte_origem")
            if row["tipo_origem"] == "secao_todo"
        ]
        self.assertEqual(len(todo_sections), 7)
        by_order = sorted(
            (
                row
                for row in todo_source_urls
                if row["fonte_id"] == "todo-3a0e2f586a126d"
            ),
            key=lambda row: int(row["ordem"]),
        )
        self.assertEqual(
            [row["nome"] for row in by_order], ["Site", "Dataset", "Gerador HTML"]
        )
        self.assertTrue(
            any(
                row["caminho_origem"] == "inventarios/pendencias-historicas.json"
                for row in self.read_table("inventario")
            )
        )
        resources = {
            item["name"]
            for item in json.loads((ROOT / "datapackage.json").read_text())["resources"]
        }
        self.assertNotIn("item_todo", resources)
        self.assertNotIn("todo_url", resources)

    def test_inventory_item_table_unifies_shapes_without_losing_values(self):
        descriptor = json.loads((ROOT / "datapackage.json").read_text())
        names = {resource["name"] for resource in descriptor["resources"]}
        self.assertIn("inventario_item", names)
        self.assertFalse(any(name.startswith("inventario_itens_") for name in names))
        self.assertFalse(any((ROOT / "data").glob("inventario_itens_*.csv")))
        resource = next(
            r for r in descriptor["resources"] if r["name"] == "inventario_item"
        )
        self.assertEqual(len(resource["schema"]["fields"]), 68)
        foreign_keys = resource["schema"]["foreignKeys"]
        self.assertEqual(
            {(tuple(fk["fields"]), fk["reference"]["resource"]) for fk in foreign_keys},
            {(("inventario_id",), "inventario"), (("fonte_id",), "fonte")},
        )

    def test_sqlite_export_preserves_tables_relations_and_is_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = ROOT
            first = Path(tmp) / "first.sqlite"
            second = Path(tmp) / "second.sqlite"
            first_counts = export_to_path(package, first)
            second_counts = export_to_path(package, second)
            self.assertEqual(first_counts, second_counts)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            import sqlite3

            with sqlite3.connect(first) as connection:
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM fonte").fetchone()[0], 4578
                )
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM inventario").fetchone()[0],
                    20,
                )
                source = connection.execute(
                    "SELECT f.nome, f.status_triagem, COUNT(u.id) "
                    "FROM fonte f JOIN fonte_url u ON u.fonte_id = f.id "
                    "WHERE f.id = 'todo-3a0e2f586a126d' "
                    "GROUP BY f.id"
                ).fetchone()
                self.assertEqual(source, ("Awesome Self-Hosted", "pendente", 3))
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
            package = Path(tmp) / "package"
            package.mkdir()
            shutil.copy2(ROOT / "datapackage.json", package / "datapackage.json")
            shutil.copytree(ROOT / "data", package / "data")
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


if __name__ == "__main__":
    unittest.main()
