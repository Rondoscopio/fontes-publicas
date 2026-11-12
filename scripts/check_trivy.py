"""Aplica o critério de falha ao relatório completo do Trivy."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


def main() -> int:
    try:
        report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        results = report["Results"]
        if not results:
            raise ValueError("Relatório sem resultados de análise")
        vulnerabilities = [
            item for result in results for item in (result.get("Vulnerabilities") or [])
        ]
        blocking = [
            item
            for item in vulnerabilities
            if item["Severity"] == "CRITICAL" or item.get("FixedVersion")
        ]
        print(
            "Achados por gravidade:",
            dict(Counter(v["Severity"] for v in vulnerabilities)),
        )
        print(f"Bloqueantes: {len(blocking)}")
        for item in blocking:
            fix = item.get("FixedVersion") or "sem correção indicada"
            print(
                f"{item['VulnerabilityID']} {item['PkgName']} {item['Severity']} {fix}"
            )
        return 10 if blocking else 0
    except (OSError, KeyError, ValueError, TypeError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
