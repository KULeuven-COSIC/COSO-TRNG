`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// 
// Module name:    	matchedStage
// File name:			matchedStage.v
// Project name: 		COSO_TRNG
// Target Device: 	Microsemi SmartFusion2 M2S025 FPGA (HECTOR daughterboard)
// Description: 		This file contains the
//							implementation of a
//							reconfigurable ring oscillator
//							stage (multiplexer), using a single
//							lookup table.
//	RTL diagram:		No
//	Author:				Adriaan Peetermans
//							imec-COSIC, KU Leuven.
//
//////////////////////////////////////////////////////////////////////////////////

module matchedStage(
		input [3:0] 	in,	// Four stage inputs, one will be selected.
		input [1:0] 	sel,	// Configuration signal.
		output 			out	//	Delayed version of the selected input.
	);

//	Instantiation multiplexer:
	MX4 MX4_inst (
		.S0(sel[0]),
		.S1(sel[1]),
		.D0(in[0]),
		.D1(in[1]),
		.D2(in[2]),
		.D3(in[3]),
		.Y(out)
	);

endmodule
