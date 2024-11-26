`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// 
// Module name:     asyncCounter
// File name:       asyncCounter.v
// Project name:    COSO_TRNG
// Target Device:   Xilinx Spartan 6 XC6SLX16 FPGA (HECTOR daughterboard)
// Description:     This file contains the
//                  implementation of a asynchronous
//                  counter module, using toggle flip-flops.
// RTL diagram:     No
// Author:          Adriaan Peetermans
//                  COSIC, KU Leuven.
//
//////////////////////////////////////////////////////////////////////////////////

module asyncCounter #(
        parameter               width = 16  // Counter width.
    )(
        input                   clk,        // Clock input.
        input                   clr,        // Active high, asynchronous reset signal.
        input                   clkEn,      // Counter enable signal.
        output [width-1:0]      cnt         // Counter output.
    );

    // Inverted counter output:
    wire [width-1:0] outN;

    // Generate toggle flip-flops:
    genvar i;

    generate
        for (i = 0; i < width; i = i + 1) begin : counter
            if (i == 0) begin
                TFF tff (.clk(clk), .clr(clr), .outP(cnt[i]), .outN(outN[i]), .clkEn(clkEn));
            end
            else begin
                TFF tff (.clk(outN[i-1]), .clr(clr), .outP(cnt[i]), .outN(outN[i]), .clkEn(clkEn));
            end
        end
    endgenerate

endmodule
