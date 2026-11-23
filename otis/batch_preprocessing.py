"""Batch removal of instrument responses from daily Hurricane John miniSEED.

Run with `python -m otis.batch_preprocessing --help`.
Uses the existing, validated `otis.preprocessing.remove_instrument_response`
function; does not require the separate mtspec environment.
"""

from __future__ import annotations

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import re
import sys
import time

from .preprocessing import remove_instrument_response


# Daily filenames in the Hurricane John archive, e.g.
# caig.ig.hhz.d.2024.256.0000 (miniSEED, no filename extension).
DAILY_NAME = re.compile(
    r"^(?P<station>[a-z0-9]+)\.(?P<network>[a-z0-9]+)\."
    r"(?P<channel>[a-z0-9]+)\.d\.(?P<year>\d{4})\."
    r"(?P<jday>\d{3})\.(?P<time>\d{4})$",
    re.IGNORECASE,
)
LOG_FIELDS = ("utc", "status", "input", "output", "seconds",
              "response_file", "message")


def discover(input_root: Path, stations: set[str] | None = None,
             channels: set[str] | None = None,
             first: date | None = None,
             last: date | None = None):
    """Find daily raw records using filenames, without reading gigabytes."""
    for path in sorted(input_root.rglob("*")):
        if not path.is_file() or "processed" in path.relative_to(input_root).parts:
            continue
        match = DAILY_NAME.fullmatch(path.name)
        if not match:
            continue
        fields = match.groupdict()
        station = fields["station"].upper()
        channel = fields["channel"].upper()
        if stations and station not in stations:
            continue
        if channels and channel not in channels:
            continue
        year = int(fields["year"])
        jday = int(fields["jday"])
        try:
            day = date(year, 1, 1) + timedelta(days=jday - 1)
            if jday < 1 or day.year != year:
                continue
        except ValueError:
            continue
        if first and day < first:
            continue
        if last and day > last:
            continue
        yield path


def corrected_path(raw: Path, input_root: Path, output_root: Path) -> Path:
    """Keep input subdirectories and the complete station/channel/day name."""
    relative = raw.relative_to(input_root)
    return output_root / relative.parent / (relative.name + ".vel.sac")


def previous_result(output: Path, raw: Path,
                    pre_filt: tuple[float, ...],
                    taper_fraction: float) -> tuple[bool, str]:
    """Return whether an existing result can safely be skipped.

    Incomplete outputs or metadata inconsistent with the current settings
    are errors unless the caller explicitly requests --overwrite.
    """
    sidecar = Path(str(output) + ".json")
    exists, has_json = output.exists(), sidecar.exists()
    if not exists and not has_json:
        return False, ""
    if not exists or not has_json:
        return False, "Incomplete output/JSON pair; use --overwrite to regenerate"
    try:
        with sidecar.open(encoding="utf-8") as handle:
            meta = json.load(handle)
        if (
            meta.get("input_raw") != str(raw)
            or meta.get("output_sac") != str(output)
            or meta.get("output_quantity") != "VEL"
            or meta.get("output_units") != "m/s"
            or tuple(meta.get("pre_filt_hz", [])) != pre_filt
            or float(meta.get("taper_fraction", -1)) != taper_fraction
            or not meta.get("response_file")
            or output.stat().st_size <= 632
        ):
            return False, "Existing result differs from settings or is invalid; use --overwrite"
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return False, f"Cannot validate existing result: {exc}; use --overwrite"
    return True, "Matching velocity SAC and provenance JSON exist"


def _process_one(raw: str, output: str, response_dir: str,
                 pre_filt: tuple[float, ...], taper_fraction: float,
                 overwrite: bool) -> dict[str, str]:
    """Worker: one daily trace per process, failure isolated to its file."""
    started = time.monotonic()
    try:
        remove_instrument_response(
            raw,
            response_dir=response_dir,
            output_path=output,
            output="VEL",
            pre_filt=pre_filt,
            taper_fraction=taper_fraction,
            overwrite=overwrite,
        )
        sidecar = Path(output + ".json")
        with sidecar.open(encoding="utf-8") as handle:
            selected_response = json.load(handle).get("response_file", "")
        return dict(status="SUCCESS", seconds=f"{time.monotonic() - started:.2f}",
                    response_file=selected_response, message="")
    except Exception as exc:
        return dict(status="FAILED", seconds=f"{time.monotonic() - started:.2f}",
                    response_file="", message=f"{type(exc).__name__}: {exc}")


def _date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Expected YYYY-MM-DD") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True,
                        help="Read-only raw miniSEED directory")
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="Writable directory for velocity SAC and JSON files")
    parser.add_argument("--response-dir", type=Path, default=Path("InstrumentResponse"))
    parser.add_argument("--stations", nargs="+", metavar="STATION",
                        help="Only process these stations, e.g. CAIG MEIG")
    parser.add_argument("--channels", nargs="+", metavar="CHANNEL",
                        help="Only these channels, e.g. HHZ HHN HHE")
    parser.add_argument("--from-date", type=_date, help="First day, YYYY-MM-DD")
    parser.add_argument("--to-date", type=_date, help="Last day, YYYY-MM-DD")
    parser.add_argument("--pre-filt", nargs=4, type=float,
                        metavar=("F1", "F2", "F3", "F4"),
                        default=(0.02, 0.05, 5.0, 8.0),
                        help="Four frequency corners in Hz")
    parser.add_argument("--taper-fraction", type=float, default=0.001)
    parser.add_argument("--workers", type=int, default=1,
                        help="Simultaneous ObsPy processes (default: 1)")
    parser.add_argument("--limit", type=int, metavar="N",
                        help="Process at most N matching files, for pilot runs")
    parser.add_argument("--log", type=Path,
                        help="Append CSV log (default: <output-dir>/batch_velocity_log.csv)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Regenerate matching, mismatched, or incomplete outputs")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print selected files without writing anything")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    input_root = args.input_dir.expanduser().resolve()
    output_root = args.output_dir.expanduser().resolve()
    response_dir = args.response_dir.expanduser().resolve()
    pre_filt = tuple(args.pre_filt)

    if not input_root.is_dir():
        parser.error(f"Input directory does not exist: {input_root}")
    if not response_dir.is_dir():
        parser.error(f"Response directory does not exist: {response_dir}")
    if input_root == output_root:
        parser.error("Input and output directory must be different")
    if output_root == input_root or input_root in output_root.parents:
        parser.error("Output directory must not be inside the raw directory")
    if args.workers < 1 or (args.limit is not None and args.limit < 1):
        parser.error("--workers and --limit must be positive")
    if args.from_date and args.to_date and args.from_date > args.to_date:
        parser.error("--from-date cannot be later than --to-date")
    if not (0 < pre_filt[0] < pre_filt[1] < pre_filt[2] < pre_filt[3]):
        parser.error("--pre-filt must contain four increasing positive frequencies")
    if not 0 <= args.taper_fraction <= 0.05:
        parser.error("--taper-fraction must be between 0 and 0.05")

    stations = {s.upper() for s in args.stations} if args.stations else None
    channels = {s.upper() for s in args.channels} if args.channels else None
    selected = list(discover(input_root, stations, channels, args.from_date, args.to_date))
    if args.limit is not None:
        selected = selected[:args.limit]

    print(f"Found {len(selected)} daily miniSEED files")
    if args.dry_run:
        for raw in selected[:20]:
            print(f"  {raw} -> {corrected_path(raw, input_root, output_root)}")
        if len(selected) > 20:
            print(f"  ... and {len(selected) - 20} more")
        print("DRY RUN: no files created")
        return 0
    if not selected:
        return 0

    log_path = args.log.expanduser().resolve() if args.log else output_root / "batch_velocity_log.csv"
    output_root.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    counts = {"SUCCESS": 0, "SKIPPED": 0, "FAILED": 0}
    with log_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=LOG_FIELDS)
        if handle.tell() == 0:
            writer.writeheader()
            handle.flush()

        def record(raw: Path, output: Path, result: dict[str, str]) -> None:
            status = result["status"]
            counts[status] += 1
            writer.writerow({
                "utc": datetime.now(timezone.utc).isoformat(),
                "status": status,
                "input": str(raw),
                "output": str(output),
                "seconds": result.get("seconds", ""),
                "response_file": result.get("response_file", ""),
                "message": result.get("message", ""),
            })
            handle.flush()
            print(f"[{status}] {raw.name}" +
                  (f": {result['message']}" if result.get("message") else ""),
                  flush=True)

        jobs = []
        for raw in selected:
            output = corrected_path(raw, input_root, output_root)
            exists = output.exists() or Path(str(output) + ".json").exists()
            if exists and not args.overwrite:
                is_valid, reason = previous_result(output, raw, pre_filt,
                                                   args.taper_fraction)
                record(raw, output, {
                    "status": "SKIPPED" if is_valid else "FAILED",
                    "message": reason,
                })
                continue
            jobs.append((raw, output))

        if args.workers == 1:
            for raw, output in jobs:
                record(raw, output, _process_one(str(raw), str(output),
                       str(response_dir), pre_filt, args.taper_fraction,
                       args.overwrite))
        else:
            with ProcessPoolExecutor(max_workers=args.workers) as executor:
                future_to_paths = {
                    executor.submit(_process_one, str(raw), str(output),
                                    str(response_dir), pre_filt,
                                    args.taper_fraction, args.overwrite): (raw, output)
                    for raw, output in jobs
                }
                for future in as_completed(future_to_paths):
                    raw, output = future_to_paths[future]
                    try:
                        result = future.result()
                    except Exception as exc:
                        result = {"status": "FAILED",
                                  "message": f"Worker crashed: {type(exc).__name__}: {exc}"}
                    record(raw, output, result)

    print("Summary:", ", ".join(f"{key}={value}" for key, value in counts.items()))
    print(f"CSV log: {log_path}")
    return 1 if counts["FAILED"] else 0


if __name__ == "__main__":
    sys.exit(main())
