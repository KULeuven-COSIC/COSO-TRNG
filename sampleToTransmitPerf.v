`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// 
// Module name:    	sampleToTransmitPerf
// File name:			sampleToTransmitPerf.v
// Project name: 		COSO_TRNG
// Target Device: 	Xilinx Spartan 6 XC6SLX16 FPGA (HECTOR daughterboard)
// Description: 		This file contains the
//							implementation of a controller
//							finite state machine that handles 
//							communication with a PC, when
//							'debugMode' == 0.
//	RTL diagram:		No
//	Author:				Adriaan Peetermans
//							imec-COSIC, KU Leuven.
//
//////////////////////////////////////////////////////////////////////////////////

module sampleToTransmitPerf # (
		parameter 				NBLSB = 1			// Number of least significant bits to be used as random data. Allowed values: 1, 2, 4, and 8.
	)(
		input 					CSReq,				//	Request signal from the coherent sampler to indicate that the counter is stable.
		input 					is_transmitting,	// Synchronisation signal from the sending module to indicate that the module is busy sending.
		input 					rst,					// Active high reset signal.
		input 					clk,					// Clock input.
		input 		[15:0] 	CSCnt,				// Coherent sampler counter input.	
		output reg	[7:0] 	tx_byte,				// Byte to be transmitted to the PC.
		output reg				transmit				// Synchronisation signal to the sending module to indicate that 'tx_byte' can be transmitted.
	);

//	Parameter:
	localparam NBIt = 8/NBLSB;				//	Number coherent sampler counter values that are needed to fill one byte of random data.

// Counter state:
	reg [$clog2(NBIt)-1:0] it;
	
// Sender finite state machine:
	always @(posedge clk) begin
		if (rst) begin
			it 		<= 0;
			transmit <= 1'b0;
			tx_byte 	<= 8'd0;
		end
		else begin
			if (is_transmitting == 1'b0) begin
				if (CSReq) begin
					case (NBLSB)
						1: begin
							tx_byte[it] <= CSCnt[0];
						end
						2: begin
							case (it)
								0: begin
									tx_byte[1:0] <= CSCnt[1:0];
								end
								1: begin
									tx_byte[3:2] <= CSCnt[1:0];
								end
								2: begin
									tx_byte[5:4] <= CSCnt[1:0];
								end
								3: begin
									tx_byte[7:6] <= CSCnt[1:0];
								end
							endcase
						end
						4: begin
							case (it)
								0: begin
									tx_byte[3:0] <= CSCnt[3:0];
								end
								1: begin
									tx_byte[7:4] <= CSCnt[3:0];
								end
							endcase
						end
						8: begin
							tx_byte <= CSCnt[7:0];
						end
					endcase
					it <= it + 1;
					if (it == NBIt-1) begin
						transmit <= 1'b1;
					end
				end
			end
			if (transmit == 1'b1) begin
				transmit <= 1'b0;
			end
		end
	end

endmodule