#!/usr/bin/env python3
"""Assert flow_events.csv carries each queue pair's exploration copies.

A sprayed run forgives nothing, so every data send, original, repair or
copy, ends one of three ways: it arrives and its flow's row counts it in
data_arrivals, a link drops it, or a switch trims it and the receiver's
notice comes back, counted as a trim notification or found stale. Summed
over the flows, the copies sent are the arrivals beyond each flow's packets,
less its repairs, plus both trim counts, plus the data the links dropped.
The fixture this reads sends copies and settles every send before its flow
completes, so the column must equal that sum and be above zero: a column
that is missing, misaligned, or read from another counter fails.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):  # pragma: no cover - script entry
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.ring_3d.analyze import iter_csv  # noqa: E402
from experiments.ring_3d.generate import load_profile  # noqa: E402


def copies_and_accounted(run_dir: Path) -> tuple[int, int]:
    """The exploration copies flow_events.csv reports, and the copies the
    send accounting gives."""
    payload = load_profile(run_dir / "profile.json").network.packet_payload_bytes
    copies = accounted = 0
    for row in iter_csv(run_dir / "telemetry" / "flow_events.csv"):
        packets = -(-int(row["physical_bytes"]) // payload)
        copies += int(row["exploration_copies"])
        accounted += (
            int(row["data_arrivals"])
            - packets
            - int(row["retransmitted_bytes"]) // payload
            + int(row["trim_notifications"])
            + int(row["stale_trim_notifications"])
        )
    accounted += sum(
        int(row["event_count"])
        for row in iter_csv(run_dir / "ns3" / "transport_summary.csv")
        if (row["event"], row["plane"]) == ("link_error_drop", "data")
    )
    return copies, accounted


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    copies, accounted = copies_and_accounted(parser.parse_args().run_dir.resolve())
    if copies == 0 or copies != accounted:
        print(
            f"exploration copies check failed: flow_events.csv reports {copies}, "
            f"the send accounting {accounted}"
        )
        return 1
    print(
        f"exploration copies check holds: {copies} copies, as the send "
        "accounting gives"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
