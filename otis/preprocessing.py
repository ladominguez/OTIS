"""Instrument-response removal for OTIS.

This module expects RAW DIGITAL COUNTS, not previously calibrated waveforms.
The RESP files are selected by their actual channel metadata and epochs,
not by the date encoded in their filenames.

Usage from the root of the OTIS repository::

    from otis.preprocessing import remove_instrument_response
    out = remove_instrument_response(
        "data/caig/IG.caig.HHZ.raw.sac",
        response_dir="InstrumentResponse",
        output_path="data/caig/IG.caig.HHZ.acc.sac",
        output="ACC",
    )

For a command-line interface, run::

    python -m otis.preprocessing data/caig/IG.caig.HHZ.raw.sac \\
        --response-dir InstrumentResponse \\
        --output-path data/caig/IG.caig.HHZ.acc.sac
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional, Sequence, Tuple

import numpy as np
from obspy import read, read_inventory
from obspy.core.util.attribdict import AttribDict

_UNITS = {"ACC": "m/s^2", "VEL": "m/s", "DISP": "m"}
_SAC_IDEP = {"ACC": 8, "VEL": 7, "DISP": 6}


def _lookup_response(response_dir, network, station, channel, location, start, end):
    """Return a unique RESP response valid for the entire waveform epoch."""
    response_dir = Path(response_dir)
    files = sorted(response_dir.glob(f"{station.upper()}_{network.upper()}_*.RESP"))
    if not files:
        raise FileNotFoundError(
            f"No RESP file found for {network}.{station} in {response_dir}"
        )

    matches = []
    for filename in files:
        inv = read_inventory(str(filename), format="RESP")
        for net in inv:
            if net.code.upper() != network.upper():
                continue
            for sta in net:
                if sta.code.upper() != station.upper():
                    continue
                for cha in sta:
                    if cha.code.upper() != channel.upper():
                        continue
                    # Some OTIS RESP files use '??' as an unspecified location.
                    resp_loc = cha.location_code or ""
                    if location and resp_loc not in (location, "??"):
                        continue
                    if cha.start_date is not None and start < cha.start_date:
                        continue
                    if cha.end_date is not None and end > cha.end_date:
                        continue
                    if cha.response is None or not cha.response.response_stages:
                        continue
                    matches.append((filename, cha))

    if len(matches) != 1:
        description = (
            f"{network}.{station}.{location}.{channel} "
            f"during {start.isoformat()} to {end.isoformat()}"
        )
        if not matches:
            raise ValueError(
                f"No RESP channel covering the whole trace {description}. "
                "Check response dates/IDs or split data at response changes."
            )
        raise ValueError(
            f"Found {len(matches)} overlapping RESP channels for {description}; "
            "supply a more precise location or correct the response metadata."
        )
    return matches[0]


def remove_instrument_response(
    input_path: str | Path,
    response_dir: str | Path = "InstrumentResponse",
    output_path: Optional[str | Path] = None,
    *,
    output: str = "ACC",
    pre_filt: Sequence[float] = (0.02, 0.05, 5.0, 8.0),
    network: str = "IG",
    station: Optional[str] = None,
    channel: Optional[str] = None,
    location: Optional[str] = None,
    taper_fraction: float = 0.001,
    overwrite: bool = False,
) -> Path:
    """Remove the full instrument response from one continuous raw waveform.

    Parameters
    ----------
    input_path:
        Single-channel raw SAC or miniSEED file in digital counts. The input
        must NOT already have its instrument response removed.
    response_dir:
        OTIS ``InstrumentResponse/`` folder containing station RESP files.
    output_path:
        Corrected SAC destination. Defaults to ``<input_stem>.acc.sac`` etc.
        The original waveform is never modified.
    output:
        ``ACC`` (m/s^2, default), ``VEL`` (m/s), or ``DISP`` (m).
    pre_filt:
        Four frequencies (Hz) defining the cosine taper used to stabilize
        deconvolution. Default preserves OTIS's current 0.1--2 Hz band at
        sampling rates above 16 Hz; tune for other bands/sampling rates.
    network, station, channel, location:
        Trace identifiers. Network defaults to ``IG``; station/channel are
        inferred from SAC/miniSEED headers or, if missing, from filename of
        the form ``IG.station.channel.*``. RESP location ``??`` is accepted
        when it is the only matching response.
    taper_fraction:
        Fraction tapered at EACH end of the full trace during deconvolution.
        Small default avoids discarding hours of data in multi-day records.
    overwrite:
        Refuse to overwrite corrected results unless explicitly set.

    Returns
    -------
    pathlib.Path
        Path to the corrected SAC file. A neighboring ``.sac.json`` records
        the chosen response, output units, and preprocessing settings.

    Raises
    ------
    ValueError
        If multiple traces/gaps, unsupported units, uncertain response epoch,
        ambiguous metadata, or invalid pre-filter are detected.

    Notes
    -----
    * Do not feed outputs from this function back into it.
    * Data spanning instrument-response changes must be split beforehand.
    * The transformation uses ObsPy's full ``Trace.remove_response`` and
      ``water_level=None`` to avoid water-level artifacts during unit
      conversion; use a band-appropriate ``pre_filt`` for stabilization.
    * For extremely long traces, process bounded day-long segments to control
      memory and avoid excessively long FFTs.
    """
    input_path = Path(input_path)
    if not input_path.is_file():
        raise FileNotFoundError(input_path)

    if any(tag in input_path.stem.lower() for tag in ("corrected", "response_removed", ".acc", ".vel", ".disp")):
        raise ValueError(
            "Input filename looks previously processed. Pass the original "
            "RAW COUNTS file instead to avoid a second response removal."
        )

    output = output.upper()
    if output not in _UNITS:
        raise ValueError("output must be ACC, VEL, or DISP")
    if len(pre_filt) != 4:
        raise ValueError("pre_filt must contain 4 frequency corners")
    pre_filt = tuple(float(x) for x in pre_filt)
    if not (0 < pre_filt[0] < pre_filt[1] < pre_filt[2] < pre_filt[3]):
        raise ValueError("pre_filt must satisfy 0 < f1 < f2 < f3 < f4")
    if not (0 <= taper_fraction <= 0.05):
        raise ValueError("taper_fraction must be between 0 and 0.05")

    suffix = output.lower()
    if output_path is None:
        output_path = input_path.with_name(f"{input_path.stem}.{suffix}.sac")
    output_path = Path(output_path)
    sidecar = Path(str(output_path) + ".json")
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Input and output paths must differ")
    if not overwrite and (output_path.exists() or sidecar.exists()):
        raise FileExistsError(f"Output already exists: {output_path} or {sidecar}")

    stream = read(str(input_path))
    if len(stream) != 1:
        raise ValueError(
            f"Input contains {len(stream)} traces. Split by channel/continuous "
            "segment first; do not merge gaps with fabricated zeros."
        )
    tr = stream[0]
    if tr.stats.npts < 2 or np.ma.is_masked(tr.data):
        raise ValueError("Trace must have unmasked, contiguous samples")
    if not np.all(np.isfinite(tr.data)):
        raise ValueError("Raw trace has NaN/Inf values")

    fnyq = tr.stats.sampling_rate / 2.0
    if pre_filt[3] >= fnyq:
        raise ValueError(
            f"pre_filt f4={pre_filt[3]:g} Hz must be below Nyquist "
            f"({fnyq:g} Hz); adjust the filter for this sample rate."
        )

    filename_ids = input_path.name.split(".")
    if len(filename_ids) >= 3:
        fname_network, fname_station, fname_channel = filename_ids[:3]
    else:
        fname_network = fname_station = fname_channel = ""

    def _code(explicit, header, fallback, field):
        explicit = (explicit or "").strip().upper()
        header = (header or "").strip().upper()
        fallback = (fallback or "").strip().upper()
        if explicit and header and explicit != header:
            raise ValueError(f"{field} conflicts with waveform header: {explicit} vs {header}")
        value = explicit or header or fallback
        if not value:
            raise ValueError(f"Missing {field}; specify it explicitly")
        return value

    net = _code(network, tr.stats.network, fname_network, "network")
    sta = _code(station, tr.stats.station, fname_station, "station")
    cha = _code(channel, tr.stats.channel, fname_channel, "channel")
    loc = (location if location is not None else tr.stats.location or "").strip()
    # Preserve full trace ID in the output even if original header was missing it.
    tr.stats.network, tr.stats.station, tr.stats.channel, tr.stats.location = net, sta, cha, loc

    filename, selected_channel = _lookup_response(
        response_dir, net, sta, cha, loc, tr.stats.starttime, tr.stats.endtime
    )
    response = selected_channel.response

    # Attachment avoids lookup issues when RESP files contain '??' location
    # codes but the waveform uses an empty or different location code.
    tr.stats.response = response
    try:
        tr.remove_response(
            inventory=None,
            output=output,
            pre_filt=pre_filt,
            water_level=None,
            zero_mean=True,
            taper=taper_fraction > 0,
            taper_fraction=taper_fraction,
            plot=False,
        )
    finally:
        tr.stats.pop("response", None)

    if not np.all(np.isfinite(tr.data)):
        raise ValueError("Nonfinite corrected values: inspect response/pre-filter")

    # SAC supports a physical-unit header for displacement, velocity and
    # acceleration; this also prevents old raw 'idep' labels being preserved.
    if "sac" not in tr.stats:
        tr.stats.sac = AttribDict()
    elif not isinstance(tr.stats.sac, AttribDict):
        tr.stats.sac = AttribDict(tr.stats.sac)
    tr.stats.sac.idep = _SAC_IDEP[output]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tr.write(str(output_path), format="SAC")
    metadata = {
        "input_raw": str(input_path),
        "output_sac": str(output_path),
        "response_file": str(filename),
        "response_channel": f"{net}.{sta}.{selected_channel.location_code}.{cha}",
        "response_epoch_start": str(selected_channel.start_date),
        "response_epoch_end": str(selected_channel.end_date),
        "waveform_start": str(tr.stats.starttime),
        "waveform_end": str(tr.stats.endtime),
        "output_quantity": output,
        "output_units": _UNITS[output],
        "pre_filt_hz": list(pre_filt),
        "water_level": None,
        "taper_fraction": taper_fraction,
        "method": "ObsPy Trace.remove_response (full response)",
        "input_assumption": "raw digital counts",
    }
    with sidecar.open("w", encoding="utf-8") as fd:
        json.dump(metadata, fd, indent=2)
        fd.write("\n")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_path", help="Raw waveform file in digital counts")
    parser.add_argument("--response-dir", default="InstrumentResponse")
    parser.add_argument("--output-path", default=None)
    parser.add_argument("--output", choices=["ACC", "VEL", "DISP"], default="ACC")
    parser.add_argument("--network", default="IG")
    parser.add_argument("--station")
    parser.add_argument("--channel")
    parser.add_argument("--location")
    parser.add_argument(
        "--pre-filt", type=float, nargs=4,
        metavar=("F1", "F2", "F3", "F4"), default=(0.02, 0.05, 5, 8),
    )
    parser.add_argument("--taper-fraction", type=float, default=0.001)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    out = remove_instrument_response(
        args.input_path,
        response_dir=args.response_dir,
        output_path=args.output_path,
        output=args.output,
        pre_filt=args.pre_filt,
        network=args.network,
        station=args.station,
        channel=args.channel,
        location=args.location,
        taper_fraction=args.taper_fraction,
        overwrite=args.overwrite,
    )
    print(f"Corrected waveform: {out}")
    print(f"Processing record: {out}.json")


if __name__ == "__main__":
    main()