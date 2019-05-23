# COSO-TRNG
This is a reference implementation for the COherent Sampling ring Oscillator based True Random Number Generator.
## Module hierarchy
* [controller](Spartan 6/controller.v)
	* [matchedRO](Spartan 6/matchedRO.v)
		* [matchedNAND](Spartan 6/matchedNAND.v)
		* [matchedStage](matchedStage.v)
	* [coherentSampler](Spartan 6/coherentSampler.v)
		* [asyncCounter](Spartan 6/Spartan 6/asyncCounter.v)
			* [TFF](Spartan 6/TFF.v)
	* [matchingController](Spartan 6/matchingController.v)
	* [ROCounter (debug)](Spartan 6/ROCounter.v)
	* [randShifter (debug)](Spartan 6/randShifter.v)
	* [sampleToTransmit (debug)](Spartan 6/sampleToTransmit.v)
	* [sampleToTransmitPerf](Spartan 6/sampleToTransmitPerf.v)
	* [sendController](Spartan 6/sendController.v)
## Synthesis tools used
### Spartan 6
### SmartFusion2
