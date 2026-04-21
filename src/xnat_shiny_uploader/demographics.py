from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from .xnat_client import XnatClient


@dataclass(frozen=True)
class Demographics:
    gender: str
    handedness: str
    yob: int


def _is_empty(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and v.strip() == "":
        return True
    return False


def _extract_subject_fields(subject_json: Dict[str, Any]) -> Dict[str, Any]:
    # XNAT classic REST typically: {"ResultSet": {"Result": [ { ... } ]}}
    rs = subject_json.get("ResultSet", {}).get("Result")
    if isinstance(rs, list) and rs:
        return rs[0]
    if isinstance(rs, dict):
        return rs
    return {}


def random_demographics(
    rng: random.Random,
    yob_min: int,
    yob_max: int,
    include_unknown: bool,
    unknown_probability: float,
) -> Demographics:
    if include_unknown and rng.random() < unknown_probability:
        gender = "unknown"
    else:
        gender = rng.choice(["male", "female"])

    if include_unknown and rng.random() < unknown_probability:
        handedness = "unknown"
    else:
        handedness = rng.choice(["right", "left"])

    yob = rng.randint(yob_min, yob_max)
    return Demographics(gender=gender, handedness=handedness, yob=yob)


def put_subject_demographics(
    client: XnatClient,
    subject: str,
    demo: Demographics,
    only_missing: bool,
    dry_run: bool = False,
) -> Demographics:
    """
    Write demographics to:
      PUT /data/projects/<P>/subjects/<S>?req_format=qs&gender=...&handedness=...&yob=...

    If only_missing=True, we first GET existing fields and do not overwrite non-empty values.
    """
    subj_path = f"/data/projects/{client.project}/subjects/{subject}"

    if only_missing and not dry_run:
        current_json = client.get_json(f"{subj_path}?format=json")
        current = _extract_subject_fields(current_json)

        gender = demo.gender if _is_empty(current.get("gender")) else current.get("gender")
        handedness = demo.handedness if _is_empty(current.get("handedness")) else current.get("handedness")
        yob = demo.yob if _is_empty(current.get("yob")) else current.get("yob")

        try:
            yob = int(yob)
        except Exception:
            yob = demo.yob

        demo = Demographics(gender=str(gender), handedness=str(handedness), yob=int(yob))

    if dry_run:
        return demo

    params = {
        "req_format": "qs",
        "gender": demo.gender,
        "handedness": demo.handedness,
        "yob": str(demo.yob),
    }
    client.put_empty(subj_path, params=params)
    return demo


def write_demographics_csv(rows: list[dict[str, Any]], out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["subject", "gender", "handedness", "yob"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
