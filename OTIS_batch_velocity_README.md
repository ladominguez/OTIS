# Batch velocity preprocessing for Hurricane John

The new `otis.batch_preprocessing` command processes one daily miniSEED file at a time using the **same** validated ObsPy response-removal function used in `otis.preprocessing`.

The original data can stay on a read-only SSHFS mount. Outputs are ground **velocity (m/s)** as SAC files, together with JSON provenance records. This stage uses the `obspy` environment; `mtspec` is not required.

## Install/update on shuanshuan

From the OTIS repository, after checking your local work:

```bash
git fetch origin
git switch --create hurricane-john-batch --track origin/feature/hurricane-john-batch-velocity
python -m otis.batch_preprocessing --help
```

This creates a *local test branch* rather than changing your local `main`. If you already have that branch, choose a different local name or switch to it.

## Preview the first five vertical records

```bash
python -m otis.batch_preprocessing \
  --input-dir /mnt/tohui/Huracan_John \
  --output-dir /mnt/tohui/Huracan_John_processed \
  --response-dir InstrumentResponse \
  --stations CAIG \
  --channels HHZ \
  --limit 5 --dry-run
```

## Pilot conversion

```bash
python -m otis.batch_preprocessing \
  --input-dir /mnt/tohui/Huracan_John \
  --output-dir /mnt/tohui/Huracan_John_processed \
  --response-dir InstrumentResponse \
  --stations CAIG \
  --channels HHZ \
  --limit 5 \
  --workers 1 \
  --pre-filt 0.02 0.05 5.0 8.0
```

The already-corrected CAIG HHZ day 256 should be marked `SKIPPED` if its SAC and JSON provenance match.

## Full batch, after reviewing pilot results

```bash
python -m otis.batch_preprocessing \
  --input-dir /mnt/tohui/Huracan_John \
  --output-dir /mnt/tohui/Huracan_John_processed \
  --response-dir InstrumentResponse \
  --channels HHZ HHN HHE \
  --workers 2 \
  --pre-filt 0.02 0.05 5.0 8.0
```

Start with one worker for a pilot, then two for the full run. Each 100 Hz daily trace contains about 8.64 million samples and needs substantially more RAM during response removal. Multiple workers can also increase SSHFS traffic.

## Naming, status and safety

Each input `caig.ig.hhz.d.2024.256.0000` becomes:

```
/mnt/tohui/Huracan_John_processed/
  caig.ig.hhz.d.2024.256.0000.vel.sac
  caig.ig.hhz.d.2024.256.0000.vel.sac.json
```

Subdirectories beneath the input directory are preserved in the output. A CSV log is appended at `<output-dir>/batch_velocity_log.csv` with `SUCCESS`, `SKIPPED`, or `FAILED` per input file. Failed or missing-response records do not stop other records; a nonzero exit status indicates at least one failure.

By default, existing outputs are skipped **only if** both files exist and the JSON records the same input path, output path, velocity units, prefilter and taper fraction. Incomplete or conflicting results are marked as failures rather than silently overwritten. To *explicitly* regenerate outputs, add `--overwrite`; treat this option carefully because it replaces files.

A matching JSON file is a *resume heuristic*, not proof that the waveform or RESP file has not changed since the earlier run. When source data or RESP metadata change, review outputs and rerun with `--overwrite`.

You may choose a date range using `--from-date YYYY-MM-DD --to-date YYYY-MM-DD`, or choose stations with `--stations CAIG MEIG`. The discovery routine recognizes daily names of the form `station.network.channel.d.YYYY.JJJ.HHMM`, not arbitrary SAC filenames. Validate raw-data calibration and inspect PSDs before using converted traces for scientific analysis.

The batch tool does **not** detect transient earthquakes, fix data gaps, or compute multitaper PSD. Those are later processing stages.
