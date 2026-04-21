from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

import yaml


def _expand_env_vars(value: Any) -> Any:
    """
    Expand strings like "${VAR}" or "$VAR" (basic support).
    """
    if not isinstance(value, str):
        return value
    return os.path.expandvars(value)


def _deep_expand(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _deep_expand(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_deep_expand(x) for x in obj]
    return _expand_env_vars(obj)


@dataclass(frozen=True)
class XnatConfig:
    base_url: str
    project: str
    alias: Optional[str]
    secret: Optional[str]
    verify_tls: bool = True


@dataclass(frozen=True)
class LocalDataConfig:
    root_dir: Path
    images_subdir: str = "images"
    labels_vessel_subdir: str = "labels_vessel"
    labels_aneurysm_subdir: str = "labels_aneurysm"


@dataclass(frozen=True)
class UploadConfig:
    resource: str = "RAW"
    overwrite: bool = True
    # If true, each subject must have all 3 files (image + 2 labels).
    # If false, upload what exists (still requires at least 1 file).
    require_all_files: bool = True
    remote_image: str = "image.nii.gz"
    remote_labels_vessel: str = "labels_vessel.nii.gz"
    remote_labels_aneurysm: str = "labels_aneurysm.nii.gz"


@dataclass(frozen=True)
class DemographicsConfig:
    enabled: bool = False
    mode: str = "random"
    only_missing: bool = True
    seed: Optional[int] = None
    yob_min: int = 1940
    yob_max: int = 1980
    include_unknown: bool = False
    unknown_probability: float = 0.05
    out_csv: Optional[Path] = None


@dataclass(frozen=True)
class RunConfig:
    dry_run: bool = False


@dataclass(frozen=True)
class AppConfig:
    xnat: XnatConfig
    local_data: LocalDataConfig
    upload: UploadConfig
    demographics: DemographicsConfig
    run: RunConfig


def load_config(config_path: Union[str, Path]) -> AppConfig:
    p = Path(config_path)
    if not p.is_file():
        raise FileNotFoundError(f"Config not found: {p}")

    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    raw = _deep_expand(raw)

    xnat = raw.get("xnat", {}) or {}
    local = raw.get("local_data", {}) or {}
    upload = raw.get("upload", {}) or {}
    demo = raw.get("demographics", {}) or {}
    run = raw.get("run", {}) or {}

    alias = xnat.get("alias") or os.getenv("XNAT_ALIAS")
    secret = xnat.get("secret") or os.getenv("XNAT_SECRET")

    base_url = str(xnat.get("base_url", "")).rstrip("/")
    project = str(xnat.get("project", ""))

    if not base_url or not project:
        raise ValueError("Config must include xnat.base_url and xnat.project")

    xnat_cfg = XnatConfig(
        base_url=base_url,
        project=project,
        alias=alias,
        secret=secret,
        verify_tls=bool(xnat.get("verify_tls", True)),
    )

    root_dir = Path(str(local.get("root_dir", "")))
    if not str(root_dir):
        raise ValueError("Config must include local_data.root_dir")

    local_cfg = LocalDataConfig(
        root_dir=root_dir,
        images_subdir=str(local.get("images_subdir", "images")),
        labels_vessel_subdir=str(local.get("labels_vessel_subdir", "labels_vessel")),
        labels_aneurysm_subdir=str(local.get("labels_aneurysm_subdir", "labels_aneurysm")),
    )

    remote_names = upload.get("remote_filenames", {}) or {}
    upload_cfg = UploadConfig(
        resource=str(upload.get("resource", "RAW")),
        overwrite=bool(upload.get("overwrite", True)),
        require_all_files=bool(upload.get("require_all_files", True)),
        remote_image=str(remote_names.get("image", "image.nii.gz")),
        remote_labels_vessel=str(remote_names.get("labels_vessel", "labels_vessel.nii.gz")),
        remote_labels_aneurysm=str(remote_names.get("labels_aneurysm", "labels_aneurysm.nii.gz")),
    )

    out_csv = demo.get("out_csv")
    demo_cfg = DemographicsConfig(
        enabled=bool(demo.get("enabled", False)),
        mode=str(demo.get("mode", "random")),
        only_missing=bool(demo.get("only_missing", True)),
        seed=demo.get("seed", None),
        yob_min=int(demo.get("yob_min", 1940)),
        yob_max=int(demo.get("yob_max", 1980)),
        include_unknown=bool(demo.get("include_unknown", False)),
        unknown_probability=float(demo.get("unknown_probability", 0.05)),
        out_csv=Path(out_csv) if out_csv else None,
    )

    run_cfg = RunConfig(dry_run=bool(run.get("dry_run", False)))

    return AppConfig(
        xnat=xnat_cfg,
        local_data=local_cfg,
        upload=upload_cfg,
        demographics=demo_cfg,
        run=run_cfg,
    )
