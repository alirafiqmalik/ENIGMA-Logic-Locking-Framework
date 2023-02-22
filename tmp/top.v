module top(N1,N2,N3,N6,N7,lockingkeyinput,Q,Z);
input N1;
input N2;
input N3;
input N6;
input N7;
input [1:0] lockingkeyinput;
wire N22_enc, N22_org;
wire N23_enc, N23_org;
orgcir org(.N1(N1),.N2(N2),.N3(N3),.N6(N6),.N7(N7),.N22(N22_org),.N23(N23_org));
enccir enc(.N1(N1),.N2(N2),.N3(N3),.N6(N6),.N7(N7),.lockingkeyinput(lockingkeyinput),.N22(N22_enc),.N23(N23_enc));
output Z;
output [1:0]Q;
assign Q[0]=N22_enc==N22_org;
assign Q[1]=N23_enc==N23_org;
assign Z= Q[0]&Q[1];
endmodule



module enccir(N1,N2,N3,N6,N7,lockingkeyinput,N22,N23);
input N1;
input N2;
input N3;
input N6;
input N7;
input [1:0] lockingkeyinput;
output N22;
output N23;
wire _0_;
wire _1_;
wire _2_;
wire _3_;
wire keywire4;
wire keywire5;
NAND_g NAND_g_4_(.A(N6), .B(N3), .Y(_2_));
NAND_g NAND_g_5_(.A(_2_), .B(N2), .Y(_3_));
NAND_g NAND_g_6_(.A(_2_), .B(N7), .Y(_0_));
NAND_g NAND_g_7_(.A(_0_), .B(_3_), .Y(N23));
NAND_g NAND_g_8_(.A(N3), .B(N1), .Y(keywire5));
NAND_g NAND_g_9_(.A(_1_), .B(_3_), .Y(keywire4));
XNOR_g keygate_XNOR_0(.A(keywire4), .B(lockingkeyinput[0]), .Y(N22));
XOR_g keygate_XOR_1(.A(keywire5), .B(lockingkeyinput[1]), .Y(_1_));
endmodule





module orgcir(N1, N2, N3, N6, N7, N22, N23);
wire _0_;
wire _1_;
wire _2_;
wire _3_;
input N1;
wire N1;
input N2;
wire N2;
output N22;
wire N22;
output N23;
wire N23;
input N3;
wire N3;
input N6;
wire N6;
input N7;
wire N7;
NAND_g _4_ ( .A(N3), .B(N6), .Y(_2_) );
NAND_g _5_ ( .A(N2), .B(_2_), .Y(_3_) );
NAND_g _6_ ( .A(N7), .B(_2_), .Y(_0_) );
NAND_g _7_ ( .A(_3_), .B(_0_), .Y(N23) );
NAND_g _8_ ( .A(N1), .B(N3), .Y(_1_) );
NAND_g _9_ ( .A(_3_), .B(_1_), .Y(N22) );
endmodule
module BUF_g(A, Y);
input A;
output Y;
assign Y=A;
endmodule

 
module NOT_g(A, Y);
input A;
output Y;
assign Y=~A;
endmodule

module AND_g(A, B, Y);
input A, B;
output Y;
assign Y=(A & B);
endmodule

module OR_g(A, B, Y);
input A, B;
output Y;
assign Y= (A | B);
endmodule

module NAND_g(A, B, Y);
input A, B;
output Y;
assign Y= ~(A & B);

endmodule

module NOR_g(A, B, Y);
input A, B;
output Y;
assign Y = ~(A | B);
endmodule


module XOR_g(A, B, Y);
input A, B;
output Y;
assign Y = (A ^ B);
endmodule

module XNOR_g(A, B, Y);
input A, B;
output Y;
assign Y = ~(A ^ B);
endmodule

module DFFcell(C, D, Q);
input C, D;
output reg Q;
always @(posedge C)
	Q <= D;
endmodule


module DFFRcell(C, D, Q, R);
input C, D, R;
output reg Q;
always @(posedge C, negedge R)
	if (!R)
		Q <= 1'b0;
	else
		Q <= D;
endmodule
