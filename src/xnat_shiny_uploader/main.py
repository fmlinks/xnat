from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path
from typing import Dict, Union

from .config import load_config
from .demographics import (
    put_subject_demographics,
    random_demographics,
    write_demographics_csv,
)
from .upload import collect_subject_files, upload_subject_files
from .xnat_client import XnatClient


def run(config_path: Union[str, Path], dry_run_override: Union[bool, None] = None) -> int:
    cfg = load_config(config_path)

    if not cfg.xnat.alias or not cfg.xnat.secret:
        print(
            "ERROR: Missing XNAT credentials. Set env XNAT_ALIAS/XNAT_SECRET or fill config xnat.alias/xnat.secret.",
            file=sys.stderr,
        )
        return 2

    dry_run = cfg.run.dry_run if dry_run_override is None else dry_run_override

    client = XnatClient(
        base_url=cfg.xnat.base_url,
        project=cfg.xnat.project,
        alias=cfg.xnat.alias,
        secret=cfg.xnat.secret,
        verify_tls=cfg.xnat.verify_tls,
    )

    if not dry_run:
        # fail fast if base/project/auth is wrong
        client.smoke_test_project_access()

    subjects = collect_subject_files(
        root_dir=cfg.local_data.root_dir,
        images_subdir=cfg.local_data.images_subdir,
        labels_vessel_subdir=cfg.local_data.labels_vessel_subdir,
        labels_aneurysm_subdir=cfg.local_data.labels_aneurysm_subdir,
    )

    print(f"Found {len(subjects)} subjects from local folder: {cfg.local_data.root_dir}")
    if not subjects:
        print("ERROR: No subjects found (no *.nii.gz in images folder).", file=sys.stderr)
        return 2

    remote_names: Dict[str, str] = {
        "image": cfg.upload.remote_image,
        "labels_vessel": cfg.upload.remote_labels_vessel,
        "labels_aneurysm": cfg.upload.remote_labels_aneurysm,
    }

    ok = 0
    fail = 0

    rng = random.Random(cfg.demographics.seed) if cfg.demographics.seed is not None else random.Random()
    demo_rows = []

    for sf in subjects:
        sid = sf.subject
        print(f"\n==> Subject: {sid}")

        try:
            if dry_run:
                local_map = {
                    "image": sf.image,
                    "labels_vessel": sf.labels_vessel,
                    "labels_aneurysm": sf.labels_aneurysm,
                }
                existing = {k: p for k, p in local_map.items() if p.is_file()}
                missing = {k: p for k, p in local_map.items() if not p.is_file()}

                if cfg.upload.require_all_files and missing:
                    raise FileNotFoundError(
                        "Missing files (require_all_files=true):\n  "
                        + "\n  ".join(f"{k}: {p}" for k, p in missing.items())
                    )
                if not existing:
                    raise FileNotFoundError("No files found for subject (all missing).")

                print("    [DRY-RUN] would create subject + resource and upload:")
                for k, p in existing.items():
                    print(f"      - {k}: {p.name}  ->  {remote_names[k]}")
            else:
                upload_subject_files(
                    client=client,
                    subject_files=sf,
                    resource=cfg.upload.resource,
                    overwrite=cfg.upload.overwrite,
                    require_all_files=cfg.upload.require_all_files,
                    remote_names=remote_names,
                    dry_run=False,
                )
                print("    uploaded: OK")

            if cfg.demographics.enabled:
                if cfg.demographics.mode.lower() != "random":
                    raise ValueError(f"Unsupported demographics.mode: {cfg.demographics.mode} (supported: random)")

                demo = random_demographics(
                    rng=rng,
                    yob_min=cfg.demographics.yob_min,
                    yob_max=cfg.demographics.yob_max,
                    include_unknown=cfg.demographics.include_unknown,
                    unknown_probability=cfg.demographics.unknown_probability,
                )

                demo_final = put_subject_demographics(
                    client=client,
                    subject=sid,
                    demo=demo,
                    only_missing=cfg.demographics.only_missing,
                    dry_run=dry_run,
                )

                print(
                    f"    demographics: gender={demo_final.gender}, handedness={demo_final.handedness}, yob={demo_final.yob}"
                )
                demo_rows.append(
                    {
                        "subject": sid,
                        "gender": demo_final.gender,
                        "handedness": demo_final.handedness,
                        "yob": demo_final.yob,
                    }
                )

            ok += 1
        except Exception as e:
            print(f"    [FAIL] {sid}: {e}", file=sys.stderr)
            fail += 1

    if cfg.demographics.enabled and cfg.demographics.out_csv and demo_rows:
        outp = cfg.demographics.out_csv
        if not outp.is_absolute():
            repo_root = Path(config_path).resolve().parent.parent
            outp = repo_root / outp
        write_demographics_csv(demo_rows, outp)
        print(f"\nSaved demographics CSV -> {outp}")

    print(f"\nDone. Success: {ok}, Failed: {fail}")
    return 0 if fail == 0 else 1


def build_arg_parser() -> argparse.ArgumentParser:
    repo_root = Path(__file__).resolve().parents[2]
    default_config = repo_root / "config" / "config.yaml"

    p = argparse.ArgumentParser(
        description=(
            "One-click bulk upload to XNAT using config.yaml. "
            "If --config is omitted, defaults to <repo>/config/config.yaml"
        )
    )
    p.add_argument("--config", default=str(default_config), help="Path to config.yaml")
    p.add_argument("--dry-run", action="store_true", help="Override config and do a dry run")
    return p


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)

    # Helpful first-run behavior: if default config path does not exist,
    # auto-create it from config.example.yaml and ask the user to edit it.
    cfg_path = Path(args.config)
    if not cfg_path.is_file():
        repo_root = Path(__file__).resolve().parents[2]
        example = repo_root / "config" / "config.example.yaml"
        if example.is_file() and cfg_path.name == "config.yaml" and cfg_path.parent.name == "config":
            cfg_path.parent.mkdir(parents=True, exist_ok=True)
            cfg_path.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"Config not found. Created template at: {cfg_path}")
            print("Please edit this file (set base_url/project/root_dir/credentials) and run again.")
            return 2
        print(f"ERROR: Config not found: {cfg_path}", file=sys.stderr)
        return 2

    return run(str(cfg_path), dry_run_override=True if args.dry_run else None)


if __name__ == "__main__":
    raise SystemExit(main())
