`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// 
// Module name:    	matchedStage
// File name:			matchedStage.v
// Project name: 		COSO_TRNG
// Target Device: 	Xilinx Spartan 6 XC6SLX16 FPGA (HECTOR daughterboard)
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

//	Instantiation lookup table:
	LUT6 #(
		.INIT(64'hAAAACCCCF0F0FF00)
	) LUT6_inst (
		.O(out),
		.I0(in[3]),
		.I1(in[2]),
		.I2(in[1]),
		.I3(in[0]),
		.I4(sel[0]),
		.I5(sel[1])
	);

endmodule