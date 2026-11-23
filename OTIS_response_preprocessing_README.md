# OTIS — removing instrument responses

Place `preprocessing.py` inside the existing `otis/` directory in the OTIS repository.

## Dependency

```bash
python -m pip install obspy numpy
```

## Prepare an uncalibrated/raw SAC file

Do not use existing `.corrected.sac` waveforms until it is established what correction they already received. This function assumes input samples are raw digital counts. Sample rate and full trace ID must be valid. The RESP files are under `InstrumentResponse/`.

## Command-line example

Run from repository root, substituting the actual raw SAC filename:

```bash
python -m otis.preprocessing \
    data/caig/IG.caig.HHZ.raw.sac \
    --response-dir InstrumentResponse \
    --output-path data/caig/IG.caig.HHZ.acc.sac \
    --output ACC \
    --pre-filt 0.02 0.05 5 8
```

Programmatic use:

```python
from otis.preprocessing import remove_instrument_response

remove_instrument_response(
    "data/pzig/IG.pzig.HHZ.raw.sac",
    response_dir="InstrumentResponse",
    output_path="data/pzig/IG.pzig.HHZ.acc.sac",
    output="ACC",
)
```

A JSON provenance sidecar `*.sac.json` is written alongside the calibrated SAC.

## Important safeguards

- Input must be raw counts; the check based on filename is only a precaution and does not prove units.
- RESP instrument/channel and start/end epochs are validated from RESP metadata, not filenames.
- If the recording overlaps a response change, the function stops. Split at the epoch boundary before correcting.
- It rejects masked data and multi-trace files; process continuous segments separately.
- Output and sidecar must not already exist unless `overwrite=True` is passed.
- The default 0.02, 0.05, 5.0, 8.0 Hz prefilter is chosen for the current OTIS 0.1–2 Hz analysis and should be checked against the instrument transfer functions and raw sampling rate.
- For multi-day to multi-week data, consider splitting into one-day segments before correction to control FFT memory, then compute and merge spectra from those segments (avoid windows overlapping gaps).
- This example does not automatically change the existing `spectrum_parallel.py` pipeline.

## Integrate with the existing spectrum.py

In `otis/spectrum/spectrum.py`, replace the current hard-coded `.corrected.sac` input path with:

```python
input_template = config['spectrum'].get(
    'input_template',
    'data/{station}/IG.{station}.{component}.acc.sac'
)
input_file = input_template.format(
    station=station.lower(), component=component.upper()
)
```

Add to `configuration.ini` under `[spectrum]`:

```ini
input_template = data/{station}/IG.{station}.{component}.acc.sac
input_quantity = ACC
input_units = m/s^2
response_removed = true
```

Change both calls to `round(...stats.delta * 100) / 100` to exact `.stats.delta` to avoid changing sample intervals.

The current spectrum calculator still stores `log10(PSD)`, not `10*log10(PSD)`. Update figure units appropriately for an acceleration-PSD dB plot, and regenerate all calibrated `.pkl` files before comparing stations or hurricanes.

## Validation

Syntax-checked and executed with a mocked ObsPy inventory/trace to exercise response matching, metadata, output writing and no-overwrite safeguards. Could not run a numerical test with actual Resp/Raw SAC in this environment because ObsPy is not installed and no raw waveform was provided.