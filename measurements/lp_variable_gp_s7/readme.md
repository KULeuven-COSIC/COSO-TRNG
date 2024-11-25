# Global Placement Sweep on Spartan 7

Sweep the global RO placement on a 5 x 5 grid, while maintaining local placement constraints for symmetry reasons.

## Sweeping Range

- `x` coordinate is swept over: `[0, 10, 28, 36, 52]`.
- `y` coordinate is swept over: `[0, 37, 74, 111, 148]`.

## Oscillator Topologies

- **muxnetwork**: `GateVar` topology.
- **muxnetwork_s**: `GateVar` topology at shifted `y` location.
- **wireonly**: `WireVar` topology.
- **wireonly_s**: `WireVar` topology at shifted `y` location.
- **intralut0**: `LUTVar0` topology.
- **intralut0_s**: `LUTVar0` topology at shifted `y` location.
- **intralut1**: `LUTVar1` topology.
- **intralut2**: `LUTVar2` topology.
- **intralut3**: `LUTVar3` topology.
- **intralut4**: `LUTVar4` topology.
- **intralut5**: `LUTVar5` topology.
- **intralut5_s**: `LUTVar5` topology at shifted `y` location.

## Data Format

| Column 0 | Column 1 |
| -------- | -------- |
| Configuration value | Mean oscillator delay |
| Unit: - | Unit: ns |