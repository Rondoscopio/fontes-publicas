"""Importa o recorte municipal da Divisão Territorial Brasileira 2025."""

from __future__ import annotations

import csv
import hashlib
import io
import re
import zipfile
from pathlib import Path
from urllib.request import urlopen
from xml.etree import ElementTree

URL = (
    "https://geoftp.ibge.gov.br/organizacao_do_territorio/"
    "estrutura_territorial/divisao_territorial/2025/DTB_2025.zip"
)
SHA256 = "d077a0e48c36cf18bcc96268b4a436200c014c6b8522c1a62d894acaf39dad27"
REPORT = "RELATORIO_DTB_BRASIL_2025_MUNICIPIOS.ods"
TOTAL_MUNICIPIOS = 5571
SIGLAS = dict(
    item.split(":")
    for item in (
        "11:RO 12:AC 13:AM 14:RR 15:PA 16:AP 17:TO 21:MA 22:PI 23:CE "
        "24:RN 25:PB 26:PE 27:AL 28:SE 29:BA 31:MG 32:ES 33:RJ 35:SP "
        "41:PR 42:SC 43:RS 50:MS 51:MT 52:GO 53:DF"
    ).split()
)
DATA = Path(__file__).resolve().parents[1] / "data"


def read_dtb(payload: bytes) -> tuple[dict[str, str], dict[str, tuple[str, str]]]:
    if hashlib.sha256(payload).hexdigest() != SHA256:
        raise ValueError("SHA-256 da DTB 2025 divergente")
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        report = archive.read(REPORT)
    with zipfile.ZipFile(io.BytesIO(report)) as archive:
        root = ElementTree.fromstring(archive.read("content.xml"))
    ufs: dict[str, str] = {}
    municipalities: dict[str, tuple[str, str]] = {}
    for row in root.findall(".//{*}spreadsheet/{*}table/{*}table-row"):
        cells = ["".join(cell.itertext()) for cell in row.findall("{*}table-cell")]
        if not cells or not re.fullmatch("[0-9]{2}", cells[0]):
            continue
        uf, uf_name = cells[:2]
        code, name = cells[7:9]
        if (
            uf not in SIGLAS
            or not re.fullmatch("[0-9]{7}", code)
            or not code.startswith(uf)
            or not name
            or code in municipalities
            or ufs.setdefault(uf, uf_name) != uf_name
        ):
            raise ValueError(f"Linha territorial inválida: {cells[:9]}")
        municipalities[code] = (name, uf)
    if set(ufs) != SIGLAS.keys() or len(municipalities) != TOTAL_MUNICIPIOS:
        raise ValueError("Quantidade de unidades da DTB 2025 divergente")
    return ufs, municipalities


def write_csv(path: Path, header: tuple[str, ...], rows) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\r\n")
        writer.writerow(header)
        writer.writerows(rows)


def main() -> None:
    with urlopen(URL, timeout=30) as response:
        ufs, municipalities = read_dtb(response.read())
    write_csv(
        DATA / "uf.csv",
        ("codigo_ibge", "sigla", "nome"),
        ((code, SIGLAS[code], name) for code, name in sorted(ufs.items())),
    )
    write_csv(
        DATA / "municipio.csv",
        ("codigo_ibge", "nome", "uf_codigo_ibge"),
        ((code, *fields) for code, fields in sorted(municipalities.items())),
    )
    print(f"DTB 2025: {len(ufs)} UFs, {len(municipalities)} unidades municipais")


if __name__ == "__main__":
    main()
