`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// 
// Module name:    	sendController
// File name:			sendController.v
// Project name: 		COSO_TRNG
// Target Device: 	Microsemi SmartFusion2 M2S025 FPGA (HECTOR daughterboard)
// Description: 		This file contains the implementation of a module that
//							enables comunication with a PC.
//	RTL diagram:		No
//	Author:				Adriaan Peetermans
//							imec-COSIC, KU Leuven.
//
//////////////////////////////////////////////////////////////////////////////////

module sendController(
		input 		clk,					// Clock input.
		input 		rst,					// Active high reset signal.
		input 		transmit,			// Synchronisation signal from the send controller to indicate that 'tx_byte' can be transmitted.
		input [7:0] tx_byte,				// Data to be transmitted from the send controller.
		output 		dataClkP,			// Positive differential data clock output.
		output 		dataClkN,			// Negative differential data clock output.
		output 		dataP,				// Positive differential data output.
		output 		dataN,				// Negative differential data output.
		output 		syncOutP,			// Positive differential synchronization output.
		output 		syncOutN,			// negative differential synchronization output.
		output reg 	is_transmitting	// Synchronisation signal to the sending controller to indicate that this module is busy sending.
	);
	 
//	State and data registers:
	wire 			clkOut;
	reg 			dataOut 		= 1'b0;
	reg 			syncOut 		= 1'b0;
	reg [7:0] 	byteBuf 		= 8'd0;
	reg 			state 		= 1'b0;
	reg [2:0] 	bitCnt 		= 3'd7;
	reg [1:0] 	syncCnt 		= 2'd0;
	reg 			clkOutSel 	= 1'b0;
	
//	State parameters:
	localparam IDLE 			= 1'b0;
	localparam TRANS 			= 1'b1;

//	Output buffers:
	lvds_out lvds_out_data (
		.D(dataOut),
		.PADN_OUT(dataN),
		.PADP_OUT(dataP)
	);

	lvds_out lvds_out_clk (
		.D(clkOut),
		.PADN_OUT(dataClkN),
		.PADP_OUT(dataClkP)
	);

	lvds_out lvds_out_sync (
		.D(syncOut),
		.PADN_OUT(syncOutN),
		.PADP_OUT(syncOutP)
	);

	assign clkOut = clkOutSel ? clk : 1'b0;
	
// Sender finite state machine:
	always @(posedge clk) begin
		if (rst) begin
			dataOut 				<= 1'b0;
			syncOut 				<= 1'b0;
			byteBuf 				<= 8'd0;
			state 				<= 3'd0;
			is_transmitting 	<= 1'b0;
			bitCnt 				<= 3'd7;
			syncCnt 				<= 2'd0;
		clkOutSel 				<= 1'b0;
		end
		else begin
			case(state)
				IDLE : begin
					clkOutSel 	<= 1'b0;
					syncOut 		<= 1'b0;
					if (transmit == 1'b1) begin
						state 				<= TRANS;
						byteBuf 				<= tx_byte;
						is_transmitting 	<= 1'b1;
					end
					else begin
						state <= IDLE;
					end
				end
				TRANS : begin
					clkOutSel 	<= 1'b1;
					dataOut 		<= byteBuf[bitCnt];
					if (bitCnt == 3'd0) begin
						bitCnt 				<= 3'd7;
						state 				<= IDLE;
						is_transmitting 	<= 1'b0;
						if (syncCnt == 2'd3) begin
							syncCnt <= 2'd0;
							syncOut <= 1'b1;
						end
						else begin
							syncOut <= 1'b0;
							syncCnt <= syncCnt + 1;
						end
					end
					else begin
						syncOut 	<= 1'b0;
						bitCnt 	<= bitCnt - 1;
						state 	<= TRANS;
					end
				end
			endcase
		end
	end

endmodule
