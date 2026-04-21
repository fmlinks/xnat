from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .xnat_client import XnatClient


NII_GZ_RE = re.compile(r"^(?P<id>.+)\.nii\.gz$", flags=re.IGNORECASE)


def subject_id_from_filename(filename: str) -> Optional[str]:
    m = NII_GZ_RE.match(filename)
    return m.group("id") if m else None


@dataclass(frozen=True)
class LocalSubjectFiles:
    subject: str
    image: Path
    labels_vessel: Path
    labels_aneurysm: Path


def iter_subjects_from_images(images_dir: Path) -> List[str]:
    ids = set()
    for p in images_dir.glob("*.nii.gz"):
        sid = subject_id_from_filename(p.name)
        if sid:
            ids.add(sid)
    return sorted(ids)


def collect_subject_files(
    root_dir: Path,
    images_subdir: str,
    labels_vessel_subdir: str,
    labels_aneurysm_subdir: str
) -> List[LocalSubjectFiles]:
    images_dir = root_dir / images_subdir
    vessel_dir = root_dir / labels_vessel_subdir
    aneurysm_dir = root_dir / labels_aneurysm_subdir

    if not images_dir.is_dir():
        raise FileNotFoundError(f"Missing folder: {images_dir}")
    if not vessel_dir.is_dir():
        raise FileNotFoundError(f"Missing folder: {vessel_dir}")
    if not aneurysm_dir.is_dir():
        raise FileNotFoundError(f"Missing folder: {aneurysm_dir}")

    subjects = iter_subjects_from_images(images_dir)
    out: List[LocalSubjectFiles] = []
    for sid in subjects:
        img = images_dir / f"{sid}.nii.gz"
        ves = vessel_dir / f"{sid}.nii.gz"
        ane = aneurysm_dir / f"{sid}.nii.gz"
        out.append(LocalSubjectFiles(subject=sid, image=img, labels_vessel=ves, labels_aneurysm=ane))
    return out


def upload_subject_files(
    client: XnatClient,
    subject_files: LocalSubjectFiles,
    resource: str,
    overwrite: bool,
    require_all_files: bool,
    remote_names: Dict[str, str],
    dry_run: bool = False,
) -> None:
    sid = subject_files.subject

    local_map = {
        "image": subject_files.image,
        "labels_vessel": subject_files.labels_vessel,
        "labels_aneurysm": subject_files.labels_aneurysm,
    }

    existing = {k: p for k, p in local_map.items() if p.is_file()}
    missing = {k: p for k, p in local_map.items() if not p.is_file()}

    if require_all_files and missing:
        raise FileNotFoundError(
            "Missing files (require_all_files=true):\n  "
            + "\n  ".join(f"{k}: {p}" for k, p in missing.items())
        )

    if not existing:
        raise FileNotFoundError("No files found for subject (all missing).")

    subj_path = f"/data/projects/{client.project}/subjects/{sid}"
    res_path = f"/data/projects/{client.project}/subjects/{sid}/resources/{resource}"

    if dry_run:
        return

    # Create subject + resource (idempotent)
    client.put_empty(subj_path)
    client.put_empty(res_path)

    def put_one(local_path: Path, remote_name: str) -> None:
        params = {"overwrite": "true"} if overwrite else None
        path = f"/data/projects/{client.project}/subjects/{sid}/resources/{resource}/files/{remote_name}"
        client.put_file(path, str(local_path), params=params)

    for key, local_path in existing.items():
        put_one(local_path, remote_names[key])
