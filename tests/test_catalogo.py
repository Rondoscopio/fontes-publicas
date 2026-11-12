from __future__ import annotations

import csv
import json
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from export_sqlite import export_to_path  # noqa: E402
from geografia import abrangencia_id  # noqa: E402
from validate_package import NULL, validate  # noqa: E402


class CatalogPackageTests(unittest.TestCase):
    def test_package_integrity(self):
        result = validate(ROOT)
        self.assertEqual(
            result["resources"],
            len(json.loads((ROOT / "datapackage.json").read_text())["resources"]),
        )
        self.assertEqual(result["rows_fonte"], 4970)
        self.assertEqual(result["rows"], 30823)
        self.assertEqual(result["resources"], 14)
        self.assertEqual(result["rows_uf"], 27)
        self.assertEqual(result["rows_municipio"], 5571)
        self.assertEqual(result["rows_abrangencia"], 94)
        self.assertEqual(result["rows_fonte_abrangencia"], 3005)
        self.assertNotIn("rows_localidade", result)
        self.assertNotIn("rows_fonte_localidade", result)
        self.assertNotIn("rows_registro_original", result)
        self.assertEqual(result["rows_categoria"], 678)
        self.assertEqual(result["rows_fonte_categoria"], 8199)
        self.assertEqual(result["rows_fonte_url"], 4964)
        self.assertEqual(result["rows_origem"], 48)
        self.assertEqual(result["rows_fonte_origem"], 3031)
        self.assertNotIn("rows_item_todo", result)
        self.assertNotIn("rows_todo_url", result)

    @staticmethod
    def read_table(name: str) -> list[dict[str, str]]:
        with (ROOT / "data" / f"{name}.csv").open(
            encoding="utf-8", newline=""
        ) as stream:
            return list(csv.DictReader(stream))

    def test_geography_history_preserves_resolved_and_pending_links(self):
        with (ROOT / "historico" / "geografia.csv").open(
            encoding="utf-8", newline=""
        ) as stream:
            history = list(csv.DictReader(stream))
        self.assertEqual(len(history), 3670)
        self.assertEqual(
            len({(row["fonte_id"], row["papel"], row["id_legado"]) for row in history}),
            3670,
        )
        for row in history:
            self.assertEqual(
                row["resultado"] == "pendente", row["abrangencia_id"] == NULL
            )
        self.assertEqual(sum(row["resultado"] == "parcial" for row in history), 30)
        self.assertTrue(
            any(
                row["abrangencia_original"] == "Municipal / SP, fora de Rondônia"
                and row["resultado"] == "pendente"
                for row in history
            )
        )

        municipalities = {
            row["codigo_ibge"]: (row["nome"], row["uf_codigo_ibge"])
            for row in self.read_table("municipio")
        }
        self.assertEqual(municipalities["5300108"], ("Brasília", "53"))
        self.assertEqual(municipalities["2605459"], ("Fernando de Noronha", "26"))
        self.assertEqual(municipalities["5101837"], ("Boa Esperança do Norte", "51"))

    def test_todo_sources_and_links_are_in_catalog(self):
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
        resources = {
            item["name"]
            for item in json.loads((ROOT / "datapackage.json").read_text())["resources"]
        }
        self.assertNotIn("item_todo", resources)
        self.assertNotIn("todo_url", resources)

    def test_category_classifications_share_one_dimension_and_relation(self):
        descriptor = json.loads((ROOT / "datapackage.json").read_text())
        resources = {item["name"]: item for item in descriptor["resources"]}
        for name in (
            "categoria_original",
            "categoria_curadoria",
            "fonte_categoria_original",
            "fonte_categoria_curadoria",
        ):
            self.assertNotIn(name, resources)
            self.assertFalse((ROOT / "data" / f"{name}.csv").exists())

        category_resource = resources["categoria"]
        category_fields = {
            field["name"]: field for field in category_resource["schema"]["fields"]
        }
        self.assertEqual(
            category_fields["tipo_classificacao"]["categories"],
            ["principal", "original", "curadoria"],
        )
        categories = self.read_table("categoria")
        self.assertEqual(
            {
                kind: sum(row["tipo_classificacao"] == kind for row in categories)
                for kind in ("principal", "original", "curadoria")
            },
            {"principal": 587, "original": 56, "curadoria": 35},
        )
        associations = self.read_table("fonte_categoria")
        self.assertEqual(len(associations), 8199)
        self.assertEqual(
            len({(row["fonte_id"], row["categoria_id"]) for row in associations}),
            8199,
        )
        category_role = {row["id"]: row["tipo_classificacao"] for row in categories}
        self.assertEqual(
            {
                role: sum(
                    category_role[row["categoria_id"]] == role for row in associations
                )
                for role in ("principal", "original", "curadoria")
            },
            {"principal": 1039, "original": 1201, "curadoria": 5959},
        )

    def test_inventory_tables_are_removed_and_source_provenance_is_preserved(self):
        descriptor = json.loads((ROOT / "datapackage.json").read_text())
        self.assertFalse(
            any(r["name"].startswith("inventario") for r in descriptor["resources"])
        )
        self.assertFalse(any((ROOT / "data").glob("inventario*.csv")))
        self.assertFalse((ROOT / "data" / "registro_original.csv").exists())

        origins = {
            row["id"]
            for row in self.read_table("origem")
            if row["valor_original"].startswith("inventarios/")
        }
        migrated = {
            row["fonte_id"]
            for row in self.read_table("fonte_origem")
            if row["tipo_origem"] == "origem_cadastro" and row["origem_id"] in origins
        }
        self.assertEqual(len(migrated), 391)
        curated = {
            row["id"]
            for row in self.read_table("categoria")
            if row["tipo_classificacao"] == "curadoria"
        }
        classified = {
            row["fonte_id"]
            for row in self.read_table("fonte_categoria")
            if row["categoria_id"] in curated
        }
        self.assertTrue(migrated.issubset(classified))
        self.assertEqual(
            {
                row["status_triagem"]
                for row in self.read_table("fonte")
                if row["id"] in migrated
            },
            {"pendente"},
        )
        self.assertEqual(
            len(migrated - {row["fonte_id"] for row in self.read_table("fonte_url")}),
            28,
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
            with sqlite3.connect(first) as connection:
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM fonte").fetchone()[0], 4970
                )
                self.assertEqual(
                    connection.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table' "
                        "AND (name GLOB 'inventario*' OR name = 'registro_original')"
                    ).fetchall(),
                    [],
                )

                category_id = "cat-fbea146eec84eb"
                matches = connection.execute(
                    "SELECT f.id FROM fonte AS f "
                    "JOIN fonte_categoria AS fc ON fc.fonte_id = f.id "
                    "WHERE fc.categoria_id = :categoria_id",
                    {"categoria_id": category_id},
                ).fetchall()
                expected = [
                    (row["fonte_id"],)
                    for row in self.read_table("fonte_categoria")
                    if row["categoria_id"] == category_id
                ]
                self.assertCountEqual(matches, expected)
                self.assertEqual(len(matches), 200)
                self.assertEqual(len(matches), len(set(matches)))
                source = connection.execute(
                    "SELECT f.nome, f.status_triagem, COUNT(u.id) "
                    "FROM fonte f JOIN fonte_url u ON u.fonte_id = f.id "
                    "WHERE f.id = 'todo-3a0e2f586a126d' "
                    "GROUP BY f.id"
                ).fetchone()
                self.assertEqual(source, ("Awesome Self-Hosted", "pendente", 3))
                atlas = connection.execute(
                    "SELECT f.nome, f.status_triagem, COUNT(*) "
                    "FROM fonte_origem AS fo "
                    "JOIN origem AS o ON o.id = fo.origem_id "
                    "JOIN fonte AS f ON f.id = o.fonte_referenciada_id "
                    "JOIN fonte_url AS u ON u.fonte_id = f.id "
                    "WHERE o.valor_original = ? AND u.url = o.valor_original "
                    "AND u.papel = 'principal' GROUP BY f.id",
                    ("https://atlasdaimprensa.com.br/rondonia-jornais/",),
                ).fetchone()
                self.assertEqual(
                    atlas, ("Atlas da Imprensa — Rondônia", "pendente", 102)
                )
                self.assertEqual(
                    connection.execute(
                        "SELECT COUNT(*) FROM origem AS o "
                        "WHERE o.fonte_referenciada_id IS NOT NULL "
                        "AND EXISTS (SELECT 1 FROM fonte_url AS u "
                        "WHERE u.fonte_id = o.fonte_referenciada_id "
                        "AND u.url = o.valor_original)"
                    ).fetchone()[0],
                    6,
                )
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute(
                        "INSERT INTO origem (id, valor_original) "
                        "SELECT 'org-duplicada', valor_original FROM origem LIMIT 1"
                    )
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
                self.assert_geography_query(connection)

    def assert_geography_query(self, connection):
        first, second, national_source, city_source = (
            row[0]
            for row in connection.execute("SELECT id FROM fonte ORDER BY id LIMIT 4")
        )
        connection.executemany(
            "DELETE FROM fonte_abrangencia WHERE fonte_id = ?",
            ((id_,) for id_ in (first, second, national_source, city_source)),
        )
        states = ["11", "12"]
        cities = ["1100205", "1100122"]
        combined = abrangencia_id(False, True, states, cities)
        self.assertEqual(
            combined,
            abrangencia_id(False, True, ["12", "11", "11"], list(reversed(cities))),
        )
        national = abrangencia_id(True, False, [], [])
        municipal = abrangencia_id(False, False, [], cities[:1])
        connection.executemany(
            "INSERT OR IGNORE INTO abrangencia VALUES (?, ?, ?)",
            [
                (combined, False, True),
                (national, True, False),
                (municipal, False, False),
            ],
        )
        connection.executemany(
            "INSERT INTO abrangencia_uf VALUES (?, ?)",
            ((combined, code) for code in states),
        )
        connection.executemany(
            "INSERT OR IGNORE INTO abrangencia_municipio VALUES (?, ?)",
            [(combined, code) for code in cities] + [(municipal, cities[0])],
        )
        connection.executemany(
            "INSERT INTO fonte_abrangencia (fonte_id, abrangencia_id, papel) VALUES (?, ?, ?)",
            [
                (first, combined, "cobertura"),
                (second, combined, "cobertura"),
                (national_source, national, "cobertura"),
                (national_source, municipal, "localidade_declarada"),
                (city_source, municipal, "cobertura"),
            ],
        )
        docs = (ROOT / "docs" / "catalogo-relacional.md").read_text(encoding="utf-8")
        sql = (
            docs.split("## Filtrar fontes por UF no SQLite", 1)[1]
            .split("```sql\n", 1)[1]
            .split("```", 1)[0]
        )
        without_national = [
            row[0]
            for row in connection.execute(
                sql, {"codigo_uf": "11", "incluir_nacional": 0}
            )
        ]
        self.assertEqual(len(without_national), len(set(without_national)))
        self.assertTrue({first, second, city_source}.issubset(without_national))
        self.assertNotIn(national_source, without_national)
        with_national = {
            row[0]
            for row in connection.execute(
                sql, {"codigo_uf": "11", "incluir_nacional": 1}
            )
        }
        self.assertIn(national_source, with_national)

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
