# No Placement Constraints Matched Controller Latency

Implement the full TRNG, including the matching controller and measure out the set-up latency for a given upper bound on C.

## Oscillator Topologies

- **muxnetwork_np_mc**: `GateVar` topology.
- **wireonly_np_mc**: `WireVar` topology.

## Data Format

| Column 0 | Column 1 |
| -------- | -------- |
| Upper bound CS count | Controller latency |
| Unit: - | Unit: number of clock periods (10 ns) |