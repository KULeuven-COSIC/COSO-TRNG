`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// 
// Module name:     matchedNAND
// File name:       matchedNAND.v
// Project name:    COSO_TRNG
// Target Device:   Microsemi SmartFusion2 M2S025 FPGA (HECTOR daughterboard)
// Description:     This file contains the
//                  implementation of a two input NAND
//                  gate.
// RTL diagram:     No
// Author:          Adriaan Peetermans
//                  COSIC, KU Leuven.
//
//////////////////////////////////////////////////////////////////////////////////

module matchedNAND(
    input   [1:0]   in, // NAND input.
    output          out // NAND output.
    );

    // Instantiation NAND gate:
    NAND2 NAND2_inst (
        .A(in[0]),
        .B(in[1]),
        .Y(out)
    );

endmodule
