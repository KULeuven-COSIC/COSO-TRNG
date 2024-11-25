# No Placement Constraints on SmartFusion 2

Implement the ROs using no placement constraints.

## Oscillator Topologies

- **muxnetwork_np**: `GateVar` topology.
- **wireonly_np**: `WireVar` topology.
- **intralut0_np**: `LUTVar0` topology.
- **intralut1_np**: `LUTVar1` topology.
- **intralut2_np**: `LUTVar2` topology.
- **intralut3_np**: `LUTVar3` topology.

## Data Format

| Column 0 | Column 1 | Column 2 | Column 3 | Column 4 | Column 5 |
| -------- | -------- | -------- | -------- | -------- | -------- |
| Configuration value RO1 | Configuration value RO0 | Mean RO0 delay | Mean RO1 delay | Mean CS count | Variance CS count |
| Unit: - | Unit: - | Unit: ns | Unit: ns | Unit: - | Unit: - |