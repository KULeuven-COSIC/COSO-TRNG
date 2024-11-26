`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// 
// Module name:     TFF
// File name:       TFF.v
// Project name:    COSO_TRNG
// Target Device:   Microsemi SmartFusion2 M2S025 FPGA (HECTOR daughterboard)
// Description:     This file contains the
//                  implementation of a toggle
//                  flip-flop, using a data flip-flop
//                  primitive and an inverter.
// RTL diagram:     No
// Author:          Adriaan Peetermans
//                  COSIC, KU Leuven.
//
//////////////////////////////////////////////////////////////////////////////////

module TFF(
        input   clk,    // Clock input.
        input   clr,    // Active high, asynchronous reset signal.
        input   clkEn,  // Enable signal.
        output  outP,   // Output signal.
        output  outN    // Inverted ouput signal.
    );

    // Instantiation of data flip-flop:
    DFN1E1C0 DFF (
        .Q(outP),
        .CLK(clk),
        .E(clkEn),
        .CLR(~clr),
        .D(outN)
    );

    // Instantiation of inverter:
    assign outN = ~outP;

endmodule
