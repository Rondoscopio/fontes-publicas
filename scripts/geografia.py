"""Identidade e invariantes dos conjuntos de abrangência."""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from collections.abc import Iterable

from import_ibge import SIGLAS, TOTAL_MUNICIPIOS

PAPEIS = ("cobertura", "localidade_declarada")


def abrangencia_id(
    nacional: bool,
    internacional: bool,
    ufs: Iterable[str],
    municipios: Iterable[str],
) -> str:
    conjunto = [nacional, internacional, sorted(set(ufs)), sorted(set(municipios))]
    canonico = json.dumps(conjunto, separators=(",", ":")).encode("ascii")
    return "abr-" + hashlib.sha256(canonico).hexdigest()


def validar_geografia(tabelas: dict[str, list[dict[str, str]]]) -> None:
    ufs = tabelas["uf"]
    municipios = tabelas["municipio"]
    if {linha["codigo_ibge"]: linha["sigla"] for linha in ufs} != SIGLAS:
        raise ValueError("A base deve conter os códigos e siglas das 27 UFs do IBGE")
    if len(municipios) != TOTAL_MUNICIPIOS:
        raise ValueError("A DTB 2025 deve conter 5.571 unidades de nível municipal")
    for linha in municipios:
        codigo = linha["codigo_ibge"]
        if (
            not re.fullmatch("[0-9]{7}", codigo)
            or codigo[:2] != linha["uf_codigo_ibge"]
        ):
            raise ValueError(
                f"Município com código IBGE incompatível com a UF: {codigo}"
            )

    ufs_por_abrangencia = defaultdict(set)
    municipios_por_abrangencia = defaultdict(set)
    for linha in tabelas["abrangencia_uf"]:
        ufs_por_abrangencia[linha["abrangencia_id"]].add(linha["uf_codigo_ibge"])
    for linha in tabelas["abrangencia_municipio"]:
        municipios_por_abrangencia[linha["abrangencia_id"]].add(
            linha["municipio_codigo_ibge"]
        )

    for linha in tabelas["abrangencia"]:
        id_ = linha["id"]
        nacional = linha["nacional"] == "true"
        internacional = linha["internacional"] == "true"
        codigos_uf = ufs_por_abrangencia[id_]
        codigos_municipais = municipios_por_abrangencia[id_]
        if not (nacional or internacional or codigos_uf or codigos_municipais):
            raise ValueError(f"Abrangência vazia: {id_}")
        if id_ != abrangencia_id(
            nacional, internacional, codigos_uf, codigos_municipais
        ):
            raise ValueError(f"ID de abrangência não corresponde ao conjunto: {id_}")

    for linha in tabelas["fonte_abrangencia"]:
        if linha["papel"] not in PAPEIS:
            raise ValueError(f"Papel de abrangência inválido: {linha['papel']}")
