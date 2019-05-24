`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// 
// Module name:    	matchingController
// File name:			matchingController.v
// Project name: 		COSO_TRNG
// Target Device: 	Microsemi SmartFusion2 M2S025 FPGA (HECTOR daughterboard)
// Description: 		This file contains the
//							implementation of a controller
//							finite state machine. It will drive
//							'RO0Sel' and 'RO1Sel' outputs to
//							obtain a 'CSCnt' value within the
//							given range: ['CSCntThreshL',
//							'CSCntThreshH').
//	RTL diagram:		RTLDiagrams/controller.pdf
//	Author:				Adriaan Peetermans
//							imec-COSIC, KU Leuven.
//
//////////////////////////////////////////////////////////////////////////////////

module matchingController #(
		parameter								CSCntLength 	= 16,							//	Coherent sampler counter width.
		parameter								NBCheckbits		= 10,							//	Number of least significant bits to be used to check coherent sampler counter magnitude.
		parameter	[NBCheckbits-1:0]		CSCntThreshL	= 1<<(NBCheckbits-1),	// Coherent sampler counter minimum allowed value.
		parameter	[NBCheckbits-1:0]		CSCntThreshH	= 1<<(NBCheckbits-1),	//	Coherent sampler counter maximum allowed value.
		parameter								ROLength			= 3,							//	Configurable ring oscillator length.
		parameter								NBSamplesLog	= 7,							//	Number of accumulated samples to check the coherent sampler counter magnitude = 2^('NBSamplesLog').
		parameter	[NBSamplesLog-1:0]	samplesMin		= 1<<(NBSamplesLog-1),	//	Minimal number of coherent sampler counter values that should be within the given bounds for a configuration to be selected.
		parameter								MaxLockCntLog	= 8							// Number of bits for the lock counter, which prevents oscillation locks.
	)(
		input 								clk,													//	Clock input.
		input 								rst,													//	Active high reset signal.
		input 		[CSCntLength-1:0] CSCnt,												//	Coherent sampler counter input.
		input									CSReq,												//	Request signal from the coherent sampler module, to indicate that the counter is stable.
		output 		[ROLength*2-1:0] 	RO0Sel,												//	RO0 configuration signal output.
		output 		[ROLength*2-1:0] 	RO1Sel,												// RO1 configuration signal output.
		output reg							CSAck,												// Acknowledge signal to the coherent sampler module, to indictate that the counter value has been read.
		output reg							matched,												// Signal to indicate the user that a good configuration has been found.
		output reg							noFound,												//	Signal to indicate the user that bo good configuration could be found.
		output reg							locked											// Signal to indicate the user that the two oscillators might be locked.
	);

//	Parameter:
	localparam NBSamples = (1<<NBSamplesLog)-1;	//	Number of accumulated samples to check the coherent sampler counter magnitude.
	
//	State and configuration registers:
	reg [NBSamplesLog-1:0] 	goodSamples, sampleCnt;
	reg [ROLength*4-1:0]		ROSel;
	
//	One single configuration register:
	assign RO0Sel = ROSel[ROLength*2-1:0];
	assign RO1Sel = ROSel[ROLength*4-1:ROLength*2];
	
//	Counter and register to indicate oscillator lock:
	reg [MaxLockCntLog-1:0] lockCnt;

// Controller finite state machine:
	always @(posedge clk) begin
		if (rst) begin
			goodSamples <= {NBSamplesLog{1'b0}};
			sampleCnt 	<= {NBSamplesLog{1'b0}};
			CSAck			<= 1'b0;
			ROSel			<= {ROLength*4{1'b0}};
			matched		<= 1'b0;
			noFound		<=	1'b0;
			lockCnt		<= {MaxLockCntLog{1'b0}};
			locked		<= 1'b0;
		end
		else begin
			if (CSReq == 1'b1) begin
				CSAck 	<= 1'b1;
				lockCnt 	<= {MaxLockCntLog{1'b0}};
				locked 	<= 1'b0;
				if ((CSCnt[CSCntLength-1:CSCntLength-NBCheckbits] >= CSCntThreshL) && (CSCnt[CSCntLength-1:CSCntLength-NBCheckbits] < CSCntThreshH)) begin
					goodSamples <= goodSamples + 1;
				end
				sampleCnt <= sampleCnt + 1;
				if (sampleCnt == NBSamples) begin
					goodSamples <= 0;
					if (goodSamples >= samplesMin) begin
						matched <= 1'b1;
					end
					else begin
						if (matched) begin
							if (goodSamples < samplesMin>>4) begin
								matched <= 1'b0;	//Still gets one chance.
							end
						end
						else begin
							ROSel <= ROSel + 1;
							if (ROSel == {ROLength*4{1'b1}}) begin
								noFound <= 1'b1;
							end
						end
					end
				end
			end
			else begin
				lockCnt <= lockCnt + 1;
				if (lockCnt == {MaxLockCntLog{1'b1}}) begin
					matched 	<= 1'b0;
					locked	<= 1'b1;
					ROSel <= ROSel + 1;
					if (ROSel == {ROLength*4{1'b1}}) begin
						noFound <= 1'b1;
					end
				end
			end
			if (CSAck == 1'b1) begin
				CSAck <= 1'b0;
			end
		end
	end

endmodule
