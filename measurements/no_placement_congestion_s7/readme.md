# No Placement Constraints and Congested FPGA on Spartan 7

Implement the ROs using no placement constraints on a congested FPGA.

## Oscillator Topologies:

- **muxnetwork_np**: `GateVar` topology, reference.
- **muxnetwork_np_cg**: `GateVar` topology, congested.
- **wireonly_np**: `WireVar` topology, reference.
- **wireonly_np_cg**: `WireVar` topology, congested.
- **intralut0_np**: `LUTVar0` topology, reference.
- **intralut0_np_cg**: `LUTVar0` topology, congested.
- **intralut5_np**: `LUTVar5` topology, reference.
- **intralut5_np_cg**: `LUTVar5` topology, congested.