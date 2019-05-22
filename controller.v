`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// 
// Module name:    	controller
// File name:			controller.v
// Project name: 		COSO_TRNG
// Target Device: 	Xilinx Spartan 6 XC6SLX16 FPGA (HECTOR daughterboard)
// Description: 		This file contains the top level
//							module that implements a
//							reconfigurable COSO-TRNG.
//	RTL diagram:		RTLDiagrams/topLevel.pdf
//	Author:				Adriaan Peetermans
//							imec-COSIC, KU Leuven.
//
//////////////////////////////////////////////////////////////////////////////////

module controller(
		input 	n_reset,			//	Active low reset signal.
		input 	[1:0] control,	//	Control signal (should be removed later).
		input 	clkInP,			//	Positive differential clock input (125 MHz).
		input 	clkInN,			//	Negative differential clock input (125 MHz).
		output 	dataClkP,		//	Positive differential data clock output.
		output 	dataClkN,		// Negative differential data clock output.
		output 	dataP,			// Positive differential data output.
		output 	dataN,			// Negative differential data output.
		output 	syncOutP,		//	Positive differential synchronization output.
		output 	syncOutN			// Negative differential synchronization output.
	);
	
//////////////////////////////////////////////////////////////////////////////////
//	Parameters
//////////////////////////////////////////////////////////////////////////////////

//	Debug mode:
	localparam							debugMode		= 1;		//	Generate additional hardware to facilitate debugging.
	
//	Generate parameters:
	localparam 							ROLength 		= 3;		//	Configurable ring oscillator length.
	localparam 							CSCntWidth 		= 16;		//	Coherent sampler counter width.
	localparam							NBLSB				= 1;		// Number of least significant bits to be used as random data.
	
//	Controller paraneters:
	localparam							NBCheckbits		= 16;		// Number of least significant bits to be used to check coherent sampler counter magnitude.
	localparam [NBCheckbits-1:0]	CSCntThreshL	= 74;		//	Coherent sampler counter minimum allowed value.
	localparam [NBCheckbits-1:0]	CSCntThreshH	= 128;	//	Coherent sampler counter maximum allowed value.
	localparam							NBSamplesLog	= 7;		// Number of accumulated samples to check the coherent sampler counter magnitude = 2^('NBSamplesLog').
	localparam [NBSamplesLog-1:0]	samplesMin		= 64;		// Minimal number of coherent sampler counter values that should be within the given bounds for a configuration to be selected.
	
//	RO counter parameters:
	localparam 							ROCntLength		= 16;		// Frequency counter width (should be removed later).

//////////////////////////////////////////////////////////////////////////////////	
//	Reset and clock
//////////////////////////////////////////////////////////////////////////////////

	wire rst, clk;
	
	assign rst = ~n_reset;
	 
	IBUFDS #(
		.DIFF_TERM("FALSE"),
		.IOSTANDARD("DEFAULT")
	) IBUFDS_CLKIN (
		.O(clk),
		.I(clkInP),
		.IB(clkInN)
	);
	
//////////////////////////////////////////////////////////////////////////////////
//	Entropy source and digitisation
//////////////////////////////////////////////////////////////////////////////////

	wire 	[CSCntWidth-1:0] 	CSCnt;
	wire 	[ROLength*2-1:0] 	RO0Sel, RO1Sel;
	wire 							RO0Clk, RO1Clk, CSReq, ROEnable, CSAck;
	
	assign ROEnable = n_reset;
	
//	Instantiate two configurable ROs:
	matchedRO #(
		.length(ROLength)
	) RO0 (
		.sel(RO0Sel),
		.enable(ROEnable),
		.out(RO0Clk)
	);
	
	matchedRO #(
		.length(ROLength)
	) RO1 (
		.sel(RO1Sel),
		.enable(ROEnable),
		.out(RO1Clk)
	);
	
//	Instantiate coherent sampling module:
	coherentSampler #(
		.cntWidth(CSCntWidth)
	) CSSampler (
		.clk0(RO0Clk),		//Sampled clock
		.clk1(RO1Clk),		//Sampling clock
		.rst(rst),
		.cnt(CSCnt),
		.req(CSReq),
		.ack(CSAck)
	);
	
//////////////////////////////////////////////////////////////////////////////////
//	Controller
//////////////////////////////////////////////////////////////////////////////////

	wire matched, noFound;
	
	assign performanceMode = control[0];
	
//	Instantiation controller module:
	matchingController #(
		.CSCntLength(CSCntWidth),
		.NBCheckbits(NBCheckbits),
		.CSCntThreshL(CSCntThreshL),
		.CSCntThreshH(CSCntThreshH),
		.ROLength(ROLength),
		.NBSamplesLog(NBSamplesLog),
		.samplesMin(samplesMin)
	) MC (
		.clk(clk), 
		.rst(rst), 
		.CSCnt(CSCnt), 
		.CSReq(CSReq), 
		.RO0Sel(RO0Sel),
		.RO1Sel(RO1Sel),
		.CSAck(CSAck),
		.matched(matched),
		.noFound(noFound)
	);
	
//////////////////////////////////////////////////////////////////////////////////
//	Additional hardware for debugging
//////////////////////////////////////////////////////////////////////////////////
	
	generate
		if (debugMode) begin
		
//			RO counter
			wire [ROCntLength-1:0] RO0Cnt, ClkCnt, RO1Cnt;
		
			ROCounter #(
				.length(ROCntLength)
			) ROCnter (
				.clk(clk), 
				.rst(rst), 
				.RO0In(RO0Clk),
				.RO1In(RO1Clk),
				.RO0Cnt(RO0Cnt),
				.RO1Cnt(RO1Cnt),
				.ClkCnt(ClkCnt)
			);
			
		end
	endgenerate
	
//////////////////////////////////////////////////////////////////////////////////
//	Communication hardware
//////////////////////////////////////////////////////////////////////////////////
	
	wire [7:0] tx_byte;
	wire transmit, is_transmitting;
	
//	Sample to transmit controller:
	generate
		if (debugMode) begin

//			Sample transmit controller if in debug mode:
			sampleToTransmit S2T (
				.CSReq(CSReq), 
				.is_transmitting(is_transmitting),
				.rst(rst),
				.clk(clk),
				.tx_byte(tx_byte),
				.transmit(transmit),
				.CSCnt(CSCnt),
				.ROSel({RO1Sel, RO0Sel}),
				.RO0Cnt(RO0Cnt),
				.RO1Cnt(RO1Cnt),
				.ClkCnt(ClkCnt),
				.matched(matched),
				.noFound(noFound)
			);
			
		end
		else begin
		
//			Sample transmit controller if not in debug mode:
			sampleToTransmitPerf # (
				.NBLSB(NBLSB)
			) S2TP (
				.CSReq(CSReq), 
				.is_transmitting(is_transmitting), 
				.rst(rst), 
				.clk(clk), 
				.CSCnt(CSCnt),
				.tx_byte(tx_byte), 
				.transmit(transmit)
			);
			
		end
	endgenerate
	
//	Instantiation transmitting controller:
	sendController SC(
		.clk(clk),
		.rst(rst),
		.dataClkP(dataClkP),
		.dataClkN(dataClkN),
		.dataP(dataP),
		.dataN(dataN),
		.syncOutP(syncOutP),
		.syncOutN(syncOutN),
		.transmit(transmit),
		.tx_byte(tx_byte),
		.is_transmitting(is_transmitting)
	);

endmodule