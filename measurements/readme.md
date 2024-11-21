# Measurement Data Folder

This folder contains all measurement data. Different measurements are available:
- **lp_variable_gp_s7**: Vary global placement over 25 locations in a Spartan 7 FPGA. Local placement is maintained.
- **no_placement_s7**: Remove all placement constraints for Spartan 7.
- **no_placement_sf2***: Remove all placement constraints for SmartFusion 2.
- **no_placement_area_explore_s7**: No placement constraints, using the area explore implementation strategy for Spartan 7.
- **no_placement_congestion_s7**: No placement constraints, on a congested FPGA for Spartan 7.
- **no_placement_matched_control_s7**: Matching controller latency measurements for variable upper C bound on Spartan 7.