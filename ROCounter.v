`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// 
// Module name:    	ROCounter
// File name:			ROCounter.v
// Project name: 		COSO_TRNG
// Target Device: 	Xilinx Spartan 6 XC6SLX16 FPGA (HECTOR daughterboard)
// Description: 		This file contains the implementation
//							of a counter, which counts the number
//							of oscillations of 'clk', 'RO0In',
//							and 'RO1In'.
//	RTL diagram:		No
//	Author:				Adriaan Peetermans
//							imec-COSIC, KU Leuven.
//
//////////////////////////////////////////////////////////////////////////////////

module ROCounter #(
		parameter 					length = 16	//	Length of the counter.
	)(
		input 						clk,			//	Clock input.
		input 						rst,			//	Active high reset signal.
		input 						RO0In,		//	RO0 oscillating input.
		input 						RO1In,		//	RO1 oscillating input.
		output reg [length-1:0] RO0Cnt,		//	RO0 counter output.
		output reg [length-1:0] RO1Cnt,		//	RO1 counter output.
		output reg [length-1:0] ClkCnt		//	Clock counter output.
	);
	
//	Clock counter:
	always @(posedge clk) begin
		if (rst) begin
			ClkCnt <= {length-1{1'b0}};
		end
		else begin
			ClkCnt <= ClkCnt + 1;
		end
	end

//	RO0 counter:
	always @(posedge RO0In) begin
		if (rst) begin
			RO0Cnt <= {length-1{1'b0}};
		end
		else begin
			RO0Cnt <= RO0Cnt + 1;
		end
	end
	
//	RO1 counter:
	always @(posedge RO1In) begin
		if (rst) begin
			RO1Cnt <= {length-1{1'b0}};
		end
		else begin
			RO1Cnt <= RO1Cnt + 1;
		end
	end
	
endmodule