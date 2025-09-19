#!/usr/bin/env python3
"""
run_heudiconv_from_heuristic.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Launch HeuDiConv using *auto_heuristic.py*,
handling cleaned-vs-physical folder names automatically.
"""

from __future__ import annotations
from pathlib import Path
import importlib.util
import subprocess
import os
from typing import Dict, List, Optional
import pandas as pd
import re

# Acceptable DICOM file extensions (lower case)
# Some Siemens datasets omit file extensions; we therefore supplement the
# extension check with a quick sniff of the header for the ``DICM`` tag.
DICOM_EXTS = (".dcm", ".ima")


def is_dicom_file(path: str) -> bool:
    """Return ``True`` if *path* appears to be a DICOM file."""

    name = Path(path).name.lower()
    if name.endswith(DICOM_EXTS):
        return True
    if "." in name:
        return False
    try:
        with open(path, "rb") as f:
            f.seek(128)
            return f.read(4) == b"DICM"
    except Exception:
        return False

# ────────────────── helpers ──────────────────
def load_sid_map(heur: Path) -> Dict[str, str]:
    """Load the ``SID_MAP`` dictionary from a heuristic file."""

    spec = importlib.util.spec_from_file_location("heuristic", heur)
    module = importlib.util.module_from_spec(spec)         # type: ignore
    assert spec.loader
    spec.loader.exec_module(module)                        # type: ignore
    return module.SID_MAP                                  # type: ignore


def clean_name(raw: str) -> str:
    """Return alphanumeric-only version of ``raw``."""

    return "".join(ch for ch in raw if ch.isalnum())

def safe_stem(text: str) -> str:
    """Return filename-friendly version of *text* (used for study names)."""
    return re.sub(r"[^0-9A-Za-z_-]+", "_", text.strip()).strip("_")


def physical_by_clean(raw_root: Path) -> Dict[str, str]:
    """Return mapping cleaned_name → relative folder path for all subdirs."""
    mapping: Dict[str, str] = {
        "": "",
        ".": "",
        raw_root.name: "",
        clean_name(raw_root.name): "",
    }
    for p in raw_root.rglob("*"):
        if not p.is_dir():
            continue
        rel = str(p.relative_to(raw_root))
        base = p.name
        mapping.setdefault(rel, rel)
        mapping.setdefault(clean_name(rel), rel)
        mapping.setdefault(base, rel)
        mapping.setdefault(clean_name(base), rel)
    return mapping



def detect_depth(folder: Path) -> int:
    """Minimum depth (#subdirs) from *folder* to any DICOM file."""

    for root, _dirs, files in os.walk(folder):
        if any(is_dicom_file(os.path.join(root, f)) for f in files):
            rel = Path(root).relative_to(folder)
            return len(rel.parts)
    raise RuntimeError(f"No DICOMs under {folder}")


def heudi_cmd(raw_root: Path,
              phys_folders: List[str],
              heuristic: Path,
              bids_out: Path,
              depth: int) -> List[str]:
    """Build the ``heudiconv`` command for the given parameters."""
    wild = "*/" * depth

    if len(phys_folders) == 1 and phys_folders[0] == "":
        subj = clean_name(raw_root.name) or "root"
        return [
            "heudiconv",
            "--files",
            str(raw_root),
            "-s",
            subj,
            "-f",
            str(heuristic),
            "-c",
            "dcm2niix",
            "-o",
            str(bids_out),
            "-b",
            "--minmeta",
            "--overwrite",
        ]

    # Use "*" instead of "*.*" so DICOMs without extensions are also matched
    template = f"{raw_root}/" + "{subject}/" + wild + "*"
    subjects = [p or clean_name(raw_root.name) for p in phys_folders]
    return [
        "heudiconv",
        "-d",
        template,
        "-s",
        *subjects,
        "-f",
        str(heuristic),
        "-c",
        "dcm2niix",
        "-o",
        str(bids_out),
        "-b",
        "--minmeta",
        "--overwrite",
    ]


def _parse_age(value: str) -> str:
    """Return numeric age from DICOM-style age strings (e.g. '032Y')."""
    m = re.match(r"(\d+)", str(value))
    if not m:
        return str(value)
    age = m.group(1).lstrip("0")
    return age or "0"


def write_participants(summary_path: Path, bids_root: Path) -> None:
    """Generate ``participants.tsv`` from ``subject_summary.tsv``."""
    if not summary_path.exists():
        return
    df = pd.read_csv(summary_path, sep="\t", keep_default_na=False)
    part_df = (
        df[["BIDS_name", "GivenName", "PatientSex", "PatientAge"]]
        .drop_duplicates(subset=["BIDS_name"])
        .copy()
    )
    if part_df.empty:
        return

    part_df["PatientAge"] = part_df["PatientAge"].apply(_parse_age)
    part_df.rename(
        columns={
            "BIDS_name": "participant_id",
            "GivenName": "given_name",
            "PatientSex": "sex",
            "PatientAge": "age",
        },
        inplace=True,
    )

    part_path = bids_root / "participants.tsv"
    part_df.to_csv(part_path, sep="\t", index=False)


# ────────────────── main runner ──────────────────
def run_heudiconv(raw_root: Path,
                  heuristic: Path,
                  bids_out: Path,
                  per_folder: bool = True,
                  mapping_df: Optional[pd.DataFrame] = None) -> None:
    """Run HeuDiConv using ``heuristic`` and write output to ``bids_out``."""

    sid_map          = load_sid_map(heuristic)          # cleaned → sub-XXX
    clean2phys       = physical_by_clean(raw_root)
    cleaned_ids      = sorted(sid_map.keys())
    phys_folders     = [clean2phys[c] for c in cleaned_ids]

    depth = detect_depth(raw_root / phys_folders[0])

    print("Raw root    :", raw_root)
    print("Heuristic   :", heuristic)
    print("Output BIDS :", bids_out)
    print("Folders     :", phys_folders)
    print("Depth       :", depth, "\n")

    bids_out.mkdir(parents=True, exist_ok=True)

    if per_folder:
        for phys in phys_folders:
            print(f"── {phys} ──")
            cmd = heudi_cmd(raw_root, [phys], heuristic, bids_out, depth)
            print(" ".join(cmd))
            subprocess.run(cmd, check=True)
            print()
    else:
        cmd = heudi_cmd(raw_root, phys_folders, heuristic, bids_out, depth)
        print(" ".join(cmd))
        subprocess.run(cmd, check=True)

    summary_path = bids_out / ".bids_manager" / "subject_summary.tsv"
    if mapping_df is not None:
        dataset = bids_out.name
        mdir = bids_out / ".bids_manager"
        sub_df = mapping_df[mapping_df["StudyDescription"].fillna("").apply(safe_stem) == dataset]
        if not sub_df.empty:
            mdir.mkdir(exist_ok=True)
            mapping_path = mdir / "subject_mapping.tsv"

            if summary_path.exists():
                old_summary = pd.read_csv(summary_path, sep="\t", keep_default_na=False)
                combined = pd.concat([old_summary, sub_df], ignore_index=True)
                combined.drop_duplicates(inplace=True)
            else:
                combined = sub_df
            combined.to_csv(summary_path, sep="\t", index=False)

            new_map = sub_df[["GivenName", "BIDS_name"]].drop_duplicates()
            if mapping_path.exists():
                old_map = pd.read_csv(mapping_path, sep="\t", keep_default_na=False)
                new_map = pd.concat([old_map, new_map], ignore_index=True)
                new_map.drop_duplicates(subset=["GivenName", "BIDS_name"], inplace=True)
            new_map.to_csv(mapping_path, sep="\t", index=False)

    # Always refresh participants.tsv from the accumulated summary
    write_participants(summary_path, bids_out)


# ────────────────── CLI interface ──────────────────
def main() -> None:
    """Command line interface for ``run-heudiconv``."""

    import argparse

    parser = argparse.ArgumentParser(description="Run HeuDiConv using one or more heuristics")
    parser.add_argument("dicom_root", help="Root directory containing DICOMs")
    parser.add_argument("heuristic", help="Heuristic file or directory with heuristic_*.py files")
    parser.add_argument("bids_out", help="Output BIDS directory")
    parser.add_argument("--subject-tsv", help="Path to subject_summary.tsv", default=None)
    parser.add_argument("--single-run", action="store_true", help="Use one heudiconv call for all subjects")
    args = parser.parse_args()

    mapping_df = None
    if args.subject_tsv:
        mapping_df = pd.read_csv(args.subject_tsv, sep="\t", keep_default_na=False)

    heur_path = Path(args.heuristic)
    heuristics = [heur_path] if heur_path.is_file() else sorted(heur_path.glob("heuristic_*.py"))
    for heur in heuristics:
        dataset = heur.stem.replace("heuristic_", "")
        out_dir = Path(args.bids_out) / dataset
        run_heudiconv(Path(args.dicom_root), heur, out_dir, per_folder=not args.single_run, mapping_df=mapping_df)


if __name__ == "__main__":
    main()

