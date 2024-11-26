`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// 
// Module name:     matchedRO
// File name:       matchedRO.v
// Project name:    COSO_TRNG
// Target Device:   Microsemi SmartFusion2 M2S025 FPGA (HECTOR daughterboard)
// Description:     This file contains the
//                  implementation of a
//                  reconfigurable ring oscillator.
// RTL diagram:     RTLDiagrams/matchedRO.pdf
// Author:          Adriaan Peetermans
//                  COSIC, KU Leuven.
//
//////////////////////////////////////////////////////////////////////////////////

module matchedRO #(
        parameter               length = 3  // Ring oscillator length.
    )(
        input   [length*2-1:0]  sel,        // Configuration signal.
        input                   enable,     // Enable this ring oscillator.
        output                  out         // Output of the last stage that was selected by the 'sel' signal.
    );

    // Stage output:
    wire [length*4+3:0] O;

    // Enable NAND gates:
    matchedNAND N0 (.in({enable, O[length*4-4]}), .out(O[length*4]));
    matchedNAND N1 (.in({enable, O[length*4-3]}), .out(O[length*4+1]));
    matchedNAND N2 (.in({enable, O[length*4-2]}), .out(O[length*4+2]));
    matchedNAND N3 (.in({enable, O[length*4-1]}), .out(O[length*4+3]));

    // Generate RO stages:
    genvar i;

    generate
        for (i = 0; i < length; i = i + 1) begin : stage
            if (i == 0) begin
                matchedStage    S0 (.in(O[length*4+3:length*4]),    .out(O[i*4]),   .sel(sel[i*2+1:i*2]));
                matchedStage    S1 (.in(O[length*4+3:length*4]),    .out(O[i*4+1]), .sel(sel[i*2+1:i*2]));
                matchedStage    S2 (.in(O[length*4+3:length*4]),    .out(O[i*4+2]), .sel(sel[i*2+1:i*2]));
                matchedStage    S3 (.in(O[length*4+3:length*4]),    .out(O[i*4+3]), .sel(sel[i*2+1:i*2]));
            end
            else begin
                matchedStage    S0 (.in(O[4*i-1:4*i-4]),            .out(O[i*4]),   .sel(sel[i*2+1:i*2]));
                matchedStage    S1 (.in(O[4*i-1:4*i-4]),            .out(O[i*4+1]), .sel(sel[i*2+1:i*2]));
                matchedStage    S2 (.in(O[4*i-1:4*i-4]),            .out(O[i*4+2]), .sel(sel[i*2+1:i*2]));
                matchedStage    S3 (.in(O[4*i-1:4*i-4]),            .out(O[i*4+3]), .sel(sel[i*2+1:i*2]));
            end
        end
    endgenerate

    // Output Multiplexer:
    matchedStage MUX (.in(O[length*4-1:length*4-4]), .out(out), .sel(sel[1:0]));

endmodule
