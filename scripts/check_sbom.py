"""Confere a identidade da imagem e o inventário Python no SBOM da auditoria."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tarfile
from pathlib import Path

LOCK = Path(".config/container/requirements.txt")


def package_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name.split("[", 1)[0].lower())


def image_config_digest(archive_path: Path) -> str:
    with tarfile.open(archive_path) as archive:
        manifest = archive.extractfile("manifest.json")
        if manifest is None:
            raise ValueError("Manifesto da imagem ausente")
        (image,) = json.load(manifest)
        config = archive.extractfile(image["Config"])
        if config is None:
            raise ValueError("Configuração da imagem ausente")
        return "sha256:" + hashlib.file_digest(config, "sha256").hexdigest()


def check(path: Path, archive_path: Path) -> None:
    image_id = image_config_digest(archive_path)
    bom = json.loads(path.read_text(encoding="utf-8"))
    image = bom["metadata"]["component"]
    properties = {item["name"]: item["value"] for item in image.get("properties", [])}
    hashes = {item["content"] for item in image.get("hashes", [])}
    if properties.get("aquasecurity:trivy:ImageID") != image_id and (
        image_id.removeprefix("sha256:") not in hashes
    ):
        raise ValueError("O SBOM não identifica a imagem analisada")
    packages = {
        (package_name(component["name"]), component.get("version"))
        for component in bom.get("components", [])
        if component.get("purl", "").startswith("pkg:pypi/")
    }
    expected = {
        (package_name(name), version)
        for name, version in (
            line.split("==", 1)
            for line in LOCK.read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#")
        )
    }
    missing = expected - packages
    if missing:
        raise ValueError(f"Dependências Python ausentes do SBOM: {sorted(missing)}")
    print(f"Imagem {image_id}, {len(expected)} dependências Python conferidas.")


if __name__ == "__main__":
    try:
        check(Path(sys.argv[1]), Path(sys.argv[2]))
    except (OSError, ValueError, KeyError) as exc:
        sys.exit(f"ERRO: {exc}")
