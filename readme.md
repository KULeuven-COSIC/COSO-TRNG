# COSO-TRNG

This is a reference implementation for the COherent Sampling ring Oscillator (COSO) based True Random Number Generator (TRNG), making use of configurable Ring Oscillators (ROs).

## Archive Structure

This archive contains the following folders:
- *measurements*: Contains measurement data for Spartan 7 and SmartFusion 2 implementations.
- *math_model*: Contains a Python implementation of the stochastic model for the COSO-TRNG.
- *hardware*: Contains Verilog reference implementation for the COSO-TRNG, using configurable ROs.
- *figures*: Contains Python scripts to generate the figures in the publications below and visualizes the data in the *measurement* folder.
- *lib*: Contains helper Python scripts and figure generation options.

## Publications

The data contained in this archive supports the following publications:
- Adriaan Peetermans, Vladimir Rožić, and Ingrid Verbauwhede. **[A Highly-Portable True Random Number Generator Based on Coherent Sampling](https://ieeexplore.ieee.org/abstract/document/8892076)**. In: *International Conference of Field Programmable Logic and Applications (FPL)*, Sept. 2019.
- Adriaan Peetermans, Vladimir Rožić, and Ingrid Verbauwhede. **[Design and Analysis of Configurable Ring Oscillators for True Random Number Generation Based on Coherent Sampling](https://dl.acm.org/doi/abs/10.1145/3433166)**. In *ACM Transactions on Reconfigurable Technology and Systems (TRETS)*, vol. 14, no. 2, pp. 1-20, 2021.