`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// 
// Module name:     randShifter
// File name:       randShifter.v
// Project name:    COSO_TRNG
// Target Device:   Microsemi SmartFusion2 M2S025 FPGA (HECTOR daughterboard)
// Description:     This file contains an implementation for a serial to
//                  parallel conversion shift register, to handle random
//                  bits.            
// RTL diagram:     No
// Author:          Adriaan Peetermans
//                  COSIC, KU Leuven.
//
//////////////////////////////////////////////////////////////////////////////////

module randShifter(
        input               clk,        // Clock input.
        input               rst,        // Active high reset signal.
        input               randBit,    // Random bit input for the shift register.
        input               CSReq,      // Request signal from the coherent sampler module, to indicate that the random bit is stable.
        output reg  [7:0]   randByte    // Output random byte from the shift register.
    );

    // Shift register:
    always @(posedge clk) begin
        if (rst) begin
            randByte <= 8'd0;
        end
        else begin
            if (CSReq) begin
                randByte <= {randByte[6:0], randBit};
            end
        end
    end

endmodule
