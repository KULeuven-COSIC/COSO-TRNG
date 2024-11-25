# No Placement Constraints and Using Area Explore Strategy on Spartan 7

Implement the ROs using no placement constraints and by using the Area Explore implementation strategy.

## Oscillator Topologies

- **muxnetwork_np_ae**: `GateVar` topology.
- **wireonly_np_ae**: `WireVar` topology.
- **intralut0_np_ae**: `LUTVar0` topology.
- **intralut5_np_ae**: `LUTVar5` topology.

## Data Format

| Column 0 | Column 1 | Column 2 | Column 3 | Column 4 | Column 5 |
| -------- | -------- | -------- | -------- | -------- | -------- |
| Configuration value RO1 | Configuration value RO0 | Mean RO0 delay | Mean RO1 delay | Mean CS count | Variance CS count |
| Unit: - | Unit: - | Unit: ns | Unit: ns | Unit: - | Unit: - |