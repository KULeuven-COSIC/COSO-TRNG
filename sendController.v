`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: KULeuven
// Engineer: Adriaan Peetermans
// 
// Create Date:    14:47:45 10/04/2018 
// Design Name: 
// Module Name:    sendController 
// Project Name: 
// Target Devices: 
// Tool versions: 
// Description: 
//
// Dependencies: 
//
// Revision: 
// Revision 0.01 - File Created
// Additional Comments: 
//
//////////////////////////////////////////////////////////////////////////////////
module sendController(
	input clk,
	input rst,
	// output lines
	output dataClkP,
	output dataClkN,
	output dataP,
	output dataN,
	output syncOutP,
	output syncOutN,
	// transmit
	input transmit,
	input [7:0] tx_byte,
	// state
	output reg is_transmitting
    );
	 
	reg dataOut = 1'b0;
	wire clkOut;
	reg syncOut = 1'b0;

	reg [7:0] txByteBuf = 8'd0;
	
	reg trState = 1'b0;
	reg [2:0] trBitCnt = 3'd7;
	reg [1:0] trSyncCnt = 2'd0;
	reg clkOutSel = 1'b0;
	
	localparam TR_IDLE 		= 1'b0;
	localparam TR_TRANS1 	= 1'b1;
	
	OBUFDS #(
		.IOSTANDARD("DEFAULT")
	) OBUFDS_DATA (
		.O(dataP),
		.OB(dataN),
		.I(dataOut)
	);
	
	OBUFDS #(
		.IOSTANDARD("DEFAULT")
	) OBUFDS_CLOCK (
		.O(dataClkP),
		.OB(dataClkN),
		.I(clkOut)
	);
	
	OBUFDS #(
		.IOSTANDARD("DEFAULT")
	) IBUFDS_SYNC (
		.O(syncOutP),
		.OB(syncOutN),
		.I(syncOut)
	);
	
	assign clkOut = clkOutSel ? clk : 1'b0;
	
	//Send controller
	always @(posedge clk) begin
		if (rst) begin
			dataOut <= 1'b0;
			syncOut <= 1'b0;
			txByteBuf <= 8'd0;
			trState <= 3'd0;
			is_transmitting <= 1'b0;
			trBitCnt <= 3'd7;
			trSyncCnt <= 2'd0;
			clkOutSel <= 1'b0;
		end
		else begin
			case(trState)
				TR_IDLE : begin
					clkOutSel <= 1'b0;
					syncOut <= 1'b0;
					if (transmit == 1'b1) begin
						trState <= TR_TRANS1;
						txByteBuf <= tx_byte;
						is_transmitting <= 1'b1;
					end
					else begin
						trState <= TR_IDLE;
					end
				end
				TR_TRANS1 : begin
					clkOutSel <= 1'b1;
					dataOut <= txByteBuf[trBitCnt];
					if (trBitCnt == 3'd0) begin
						trBitCnt <= 3'd7;
						trState <= TR_IDLE;
						is_transmitting <= 1'b0;
						if (trSyncCnt == 2'd3) begin
							trSyncCnt <= 2'd0;
							syncOut <= 1'b1;
						end
						else begin
							syncOut <= 1'b0;
							trSyncCnt <= trSyncCnt + 1;
						end
					end
					else begin
						syncOut <= 1'b0;
						trBitCnt <= trBitCnt - 1;
						trState <= TR_TRANS1;
					end
				end
			endcase
		end
	end

endmodule