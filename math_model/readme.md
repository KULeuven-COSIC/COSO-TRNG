# Stochastic Model Simulation

This folder contains a script to simulate the stochastic model and generate data suitable for plotting the HTP and min-entropy versus the oscillator period difference (TRNG TDC resolution).
The script will estimate entropy using a simulation approach and a Gaussian distribution approach. Both estimates are stored.

## Usage

Execute the Python script *generate_h_vs_csc.py* without arguments, the HTP and entropy data will be generated in the *results/* folder.
Edit the `JIT_STRENGTH` and `RO_PER` values inside the script to simulate different oscillators/hardware platforms.