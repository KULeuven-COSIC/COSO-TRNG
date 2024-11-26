`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// 
// Module name:     coherentSampler
// File name:       coherentSampler.v
// Project name:    COSO_TRNG
// Target Device:   Xilinx Spartan 6 XC6SLX16 FPGA (HECTOR daughterboard)
// Description:     This file contains the
//                  implementation of a coherent
//                  sampler module.
// RTL diagram:     RTLDiagrams/coherentSampler.pdf
// Author:          Adriaan Peetermans
//                  COSIC, KU Leuven.
//
//////////////////////////////////////////////////////////////////////////////////

module coherentSampler # (
        parameter                   cntWidth = 16   // Coherent sampler counter width.
    )(
        input                       clk0,           // Sampled clock input.
        input                       clk1,           // Sampling clock input.
        input                       rst,            // Active high reset.
        input                       ack,            // Acknowledge input from the controller to indicate that the counter has been read.
        output [cntWidth-1:0]       cnt,            // Coherent sampler counter output.
        output                      req             // Request signal for the controller to indicate that the counter is stable.
    );

    wire S0, clk1N, cntRST, cntRSTN;
    reg clkEn;

    // Sampling DFF:
    FDCE DFF0 (
        .Q(S0),
        .C(clk1),   //Sampling clock
        .CE(1'b1),
        .CLR(rst),
        .D(clk0)    //Sampled clock
    );

    assign clk1N = ~clk1;

    // Coherent sampler counter:
    asyncCounter #(
        .width(cntWidth)
    ) counter (
        .clk(clk1N),
        .clr(cntRST),
        .cnt(cnt),
        .clkEn(clkEn)
    );

    // Synchronization with the controller:
    always @(posedge S0) begin
        if (rst) begin
            clkEn <= 1'b0;
        end
        else begin
            if (clkEn == 1'b1) begin
                clkEn <= 1'b0;
            end
            else begin
                if ((req == 1'b0) && (ack == 1'b0)) begin
                    clkEn <= 1'b1;
                end
            end
        end
    end

    // Request generation:
    FDCE reqDFF (
        .Q(req),
        .C(S0),
        .CE(1'b1),
        .CLR(ack),
        .D(cntRSTN)
    );

    // Counter reset generation:
    FDCE cntRSTDFF (
        .Q(cntRSTN),
        .C(S0),
        .CE(cntRST),
        .CLR(ack),
        .D(1'b1)
    );

    assign cntRST = ~cntRSTN;

endmodule
