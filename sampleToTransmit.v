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
//								
//	RTL diagram:		No
//	Author:				Adriaan Peetermans
//							imec-COSIC, KU Leuven.
//
//////////////////////////////////////////////////////////////////////////////////

module sampleToTransmit (
		input 					CSReq,				//	Request signal from the coherent sampler module, to indicate that the counter is stable.
		input 					is_transmitting,	// Synchronisation signal to the transmitter controller to indicate that this module is busy sending.
		input						rst,					//	Actibe high reset signal.
		input						clk,					// Clock input.
		input 					matched,				//	Signal from the configuration controller to indicate that a good configuration has been found.
		input						noFound,				//	Signal from the configuration controller to indicate that no good configuration could be found.
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
	reg	[4:0] 	transmitState;

// Helper register to store the coherent sampler counter value when it is stable:
	reg 	[15:0] 	CSCntReg;
	reg	[7:0]		CSCntRegLSB;
	wire 				CSCntCE;

//	Helper registers to store data during transmission:
	reg 	[15:0]	RO0Helper, RO1Helper, ClkHelper;
	reg 	[11:0]	ROSelHelper;
	reg				matchedHelper, noFoundHelper;
	
// Sender finite state machine:
	always @(posedge clk) begin
		if (rst) begin
			tx_byte 			<= 8'd0;
			transmitState 	<= 5'd0;
			transmit 		<= 1'b0;
			CSCntRegLSB		<= 8'd0;
			RO0Helper		<= 16'd0;
			RO1Helper		<= 16'd0;
			ClkHelper		<= 16'd0;
			ROSelHelper		<= 8'd0;
			matchedHelper	<= 1'b0;
			noFoundHelper	<= 1'b0;
		end
		else begin
			if ((is_transmitting == 1'b0) && (transmit == 1'b0)) begin
				transmit <= 1'b1;
				case (transmitState)
					5'd0: begin
						tx_byte 			<= 8'h55;
						transmitState 	<= 5'd1;
					end
					5'd1: begin
						tx_byte 			<= CSCntReg[15:8];
//						Update helpers:
						CSCntRegLSB		<= CSCntReg[7:0];
						RO0Helper		<= RO0Cnt;
						RO1Helper		<= RO1Cnt;
						ClkHelper		<= ClkCnt;
						ROSelHelper		<= ROSel;
						matchedHelper	<= matched;
						noFoundHelper	<= noFound;
						transmitState 	<= 5'd2;
					end
					5'b00000: begin
						tx_byte 			<= CSCntRegLSB;
						transmitState 	<= 5'b00010;
						//transmit 		<= 1'b1;
					end
					5'b00010: begin
						tx_byte 			<= {2'b00, ROSel[11:6]};
						ROSelHelper		<= {2'b00, ROSel[5:0]};
						transmitState 	<= 5'b01011;
					end
					5'b01011: begin
						tx_byte			<= ROSelHelper;
						transmitState	<= 5'b01100;
					end
					5'b01100: begin
						tx_byte			<= 8'd42;
						transmitState	<= 5'b01101;
					end
					5'b01101: begin
						tx_byte			<= 8'd43;
						transmitState	<= 5'b00011;
					end
					5'b00011: begin
						tx_byte			<= RO0Cnt[15:8];
						RO0Helper		<= RO0Cnt[7:0];
						RO1Helper		<= RO1Cnt;
						ClkHelper		<= ClkCnt;
						transmitState	<= 5'b00101;
					end
					5'b00101: begin
						tx_byte			<= RO0Helper;
						transmitState	<= 5'b01001;
					end
					5'b01001: begin
						tx_byte			<= RO1Helper[15:8];
						transmitState	<= 5'b01010;
					end
					5'b01010: begin
						tx_byte			<= RO1Helper[7:0];
						transmitState	<= 5'b00111;
					end
					5'b00111: begin
						tx_byte			<= ClkHelper[15:8];
						transmitState	<= 5'b01000;
					end
					5'b01000: begin
						tx_byte			<= ClkHelper[7:0];
						transmitState	<= 5'b10000;
					end
					5'b10000: begin
						tx_byte			<= duration[31:24];
						durationHelper	<= duration[23:0];
						transmitState	<= 5'b10001;
					end
					5'b10001: begin
						tx_byte			<= durationHelper[23:16];
						transmitState	<= 5'b10010;
					end
					5'b10010: begin
						tx_byte			<= durationHelper[15:8];
						transmitState	<= 5'b10011;
					end
					5'b10011: begin
						tx_byte			<= durationHelper[7:0];
						transmitState	<= 5'b00110;
					end
					5'b00110: begin
						tx_byte			<= 8'haa;
						transmitState	<= 5'b00100;
						//transmit			<= 1'b1;
					end
				endcase
			end
			if (transmit) begin
				transmit <= 1'b0;
			end
		end
	end
	
	//CSCnt register	
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
