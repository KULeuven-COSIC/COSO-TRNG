`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// 
// Module name:    	matchedNAND
// File name:			matchedNAND.v
// Project name: 		COSO_TRNG
// Target Device: 	Xilinx Spartan 6 XC6SLX16 FPGA (HECTOR daughterboard)
// Description: 		This file contains the
//							implementation of a two input NAND
//							gate using a single lookup table.
//	RTL diagram:		No
//	Author:				Adriaan Peetermans
//							imec-COSIC, KU Leuven.
//
//////////////////////////////////////////////////////////////////////////////////

module matchedNAND(
		 input [1:0] 	in,	//	NAND input.
		 output 			out	//	NAND output.
    );
	
//	Instantiation lookup table:
	LUT6 #(
		.INIT(64'h0000FFFFFFFFFFFF)
	) LUT6_inst (
		.O(out),
		.I0(1'b0),
		.I1(1'b0),
		.I2(1'b0),
		.I3(1'b0),
		.I4(in[0]),
		.I5(in[1])
	);

endmodule