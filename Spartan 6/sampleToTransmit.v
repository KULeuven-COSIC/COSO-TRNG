`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// 
// Module name:    	sampleToTransmit
// File name:			sampleToTransmit.v
// Project name: 		COSO_TRNG
// Target Device: 	Xilinx Spartan 6 XC6SLX16 FPGA (HECTOR daughterboard)
// Description: 		This file contains the implementation of a controller finite 
//							state machine that handles communication with a PC, when
//							'debugMode' == 1.
//							This module will only work under the following settings:
//								CSCntWidth 	= 16
//								ROLength 	= 3
//								ROCntLength	= 16
//							Data will be send in packets to the receiving PC:
//								| Size [bytes]	| 1		| 2		| 2		| 2		| 2		| 1				| 1				| 1									| 1			| 1		|
//								| Data			| 0x55	| CSCnt	| RO0Cnt | RO1Cnt	| ClkCnt	| {00,RO1Sel}	| {00,RO0Sel	| {matched, noFound, 000000}	| randBits	| 0xaa	|
//	RTL diagram:		No
//	Author:				Adriaan Peetermans
//							imec-COSIC, KU Leuven.
//
//////////////////////////////////////////////////////////////////////////////////

module sampleToTransmit (
		input 					CSReq,				//	Request signal from the coherent sampler module, to indicate that the counter is stable.
		input 					is_transmitting,	// Synchronisation signal from the sending module to indicate that the module is busy sending.
		input						rst,					//	Actibe high reset signal.
		input						clk,					// Clock input.
		input 					matched,				//	Signal from the configuration controller to indicate that a good configuration has been found.
		input						noFound,				//	Signal from the configuration controller to indicate that no good configuration could be found.
		input						locked,				// Signal to indicate the user that the two oscillators might be locked.
		input			[15:0]	CSCnt,				// Coherent sampler counter value.
		input			[11:0]	ROSel,				//	Configuration signal from the configuration controller.
		input			[15:0]	RO0Cnt,				//	RO0 counter value.
		input 		[15:0]	RO1Cnt,				//	RO1 counter value.
		input			[15:0]  	ClkCnt,				// Clock counter value.
		input			[7:0]		randBits,			//	One byte of generated random data.
		output reg 	[7:0] 	tx_byte,				//	Byte to be transmitted to the PC.
		output reg				transmit				//	Synchronisation signal to the sending module to indicate that 'tx_byte' can be transmitted.
	);
	
//	State register:
	reg	[3:0] 	transmitState;

// Helper register to store the coherent sampler counter value when it is stable:
	reg 	[15:0] 	CSCntReg;
	reg	[7:0]		CSCntRegLSB;
	wire 				CSCntCE;

//	Helper registers to store data during transmission:
	reg 	[15:0]	RO0Helper, RO1Helper, ClkHelper;
	reg 	[11:0]	ROSelHelper;
	reg				matchedHelper, noFoundHelper, lockedHelper;
	
// Sender finite state machine:
	always @(posedge clk) begin
		if (rst) begin
			tx_byte 			<= 8'd0;
			transmitState 	<= 4'd0;
			transmit 		<= 1'b0;
			CSCntRegLSB		<= 8'd0;
			RO0Helper		<= 16'd0;
			RO1Helper		<= 16'd0;
			ClkHelper		<= 16'd0;
			ROSelHelper		<= 12'd0;
			matchedHelper	<= 1'b0;
			noFoundHelper	<= 1'b0;
			lockedHelper	<= 1'b0;
		end
		else begin
			if ((is_transmitting == 1'b0) && (transmit == 1'b0)) begin
				transmit <= 1'b1;
				case (transmitState)
					4'd0: begin
						tx_byte 			<= 8'h55;
						transmitState 	<= 4'd1;
					end
					4'd1: begin
						tx_byte 			<= CSCntReg[15:8];
//						Update helpers:
						CSCntRegLSB		<= CSCntReg[7:0];
						RO0Helper		<= RO0Cnt;
						RO1Helper		<= RO1Cnt;
						ClkHelper		<= ClkCnt;
						ROSelHelper		<= ROSel;
						matchedHelper	<= matched;
						noFoundHelper	<= noFound;
						lockedHelper	<= locked;
						transmitState 	<= 4'd2;
					end
					4'd2: begin
						tx_byte 			<= CSCntRegLSB;
						transmitState 	<= 4'd3;
					end
					4'd3: begin
						tx_byte			<= RO0Helper[15:8];
						transmitState	<= 4'd4;
					end
					4'd4: begin
						tx_byte			<= RO0Helper[7:0];
						transmitState	<= 4'd5;
					end
					4'd5: begin
						tx_byte			<= RO1Helper[15:8];
						transmitState	<= 4'd6;
					end
					4'd6: begin
						tx_byte			<= RO1Helper[7:0];
						transmitState	<= 4'd7;
					end
					4'd7: begin
						tx_byte			<= ClkHelper[15:8];
						transmitState	<= 4'd8;
					end
					4'd8: begin
						tx_byte			<= ClkHelper[7:0];
						transmitState	<= 4'd9;
					end
					4'd9: begin
						tx_byte 			<= {2'b00, ROSelHelper[11:6]};
						transmitState	<= 4'd10;
					end
					4'd10: begin
						tx_byte			<= {2'b00, ROSelHelper[5:0]};
						transmitState	<= 4'd11;
					end
					4'd11: begin
						tx_byte			<= {matchedHelper, noFoundHelper, lockedHelper, 5'd0};
						transmitState	<= 4'd12;
					end
					4'd12: begin
						tx_byte			<= randBits;
						transmitState	<= 4'd13;
					end
					4'd13: begin
						tx_byte			<= 8'haa;
						transmitState	<= 4'd0;
					end
				endcase
			end
			if (transmit) begin
				transmit <= 1'b0;
			end
		end
	end
	
//	CSCnt register:
	always @(posedge clk) begin
		if (rst) begin
			CSCntReg <= 16'd0;
		end
		else begin
			if (CSReq) begin
				CSCntReg <= CSCnt;
			end
		end
	end
	
endmodule
