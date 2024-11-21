# Figure Generation Python Scripts

This folder contains the figure generation Python scripts.

## Scripts:

The scripts are divided in the following categories.

### Stochastic Model:

- **h_vs_csc_s7.py**: Generate estimated min-entropy and HTP versus delta and C figure for Spartan 7.
- **h_vs_csc_sf2.py**: Generate estimated min-entropy and HTP versus delta and C figure for SmartFusion 2.

### `LUTVar` Characterization:

- **intralut_range.py**: Generate `LUTVar` range figure for Spartan 7.
- **intralut_res.py**: Generate `LUTVar` resolution figure for Spartan 7.

### Fixed Single placement:

- **csc_s7_fixed_placement.py**: Generate obtainable C values with fixed placement figure for Spartan 7.

### Global Placement Sweep:

- **ranres_s7_variable_gp.py**: Generate the range-resolution point cloud for all 25 locations, for 1-4 number of stages figure for Spartan 7.
- **csc_s7_placement_sweep_gatevar.py**: Generate calculated C values using the `GateVar` topology at 25 different locations figure for Spartan 7.
- **csc_s7_placement_sweep_wirevar.py**: Generate calculated C values using the `WireVar` topology at 25 different locations figure for Spartan 7.
- **csc_s7_placement_sweep_lutvar0.py**: Generate calculated C values using the `LUTVar0` topology at 25 different locations figure for Spartan 7.
- **csc_s7_placement_sweep_lutvar5.py**: Generate calculated C values using the `LUTVar` topology at 25 different locations figure for Spartan 7.

### No Placement Constraints:

- **csc_s7_no_placement.py**: Generate obtained C values without specified GP and LP constraints figure for Spartan 7.
- **csc_sf2_no_placement.py**: Generate obtained C values without specified GP and LP constraints figure for SmartFusion 2.
- **ranres_s7_no_placement.py**: Generate the measured range and resolution for all RO designs for number stages ranging from 1 to 4, without placement constraints figure for Spartan 7.
- **ranres_sf2_no_placement.py**: Generate the measured range and resolution for all RO designs for number stages ranging from 1 to 4, without placement constraints figure for SmartFusion 2.

### Stage Length:

- **csc_s7_stage_length.py**: Generate obtained C values for different number of RO stages and omitted GP and LP constraints figure for Spartan 7.

### Implementation Strategy:
- **csc_s7_stage_length_area_explore.py**: Generate obtained C values for different number of RO stages and omitted GP and LP constraints, using Area Explore figure for Spartan 7.

### FPGA Congestion:

- **csc_s7_no_placement_congest.py**: Generate obtained C values without specified GP and LP constraints on a heavily congested FPGA figure for Spartan 7.
- **ranres_s7_no_placement_congest.py**: Generate the measured range and resolution for all RO designs for number stages ranging from 1 to 4, on a congested FPGA, without placement constraints figure for Spartan 7.

### Controller Latency:

- **max_counts_s7_no_placement.py**: Generate controller latency for variable upper bound figure for Spartan 7.

## Script Options:

The following script arguments are available:
- `-v`: Enable verbose output.
- `-d`: Generate processed data and store in the *data/* folder.
- `-q`: Quit the script as soon as the processed data is generated, without generating the figure. Should only be used in combination with the `-d` argument.
- `-l`: For lengthy execution times, the log option might be available, indicating the time required to execute the script.