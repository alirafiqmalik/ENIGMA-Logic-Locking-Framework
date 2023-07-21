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

module DFFcell(CLK, D, Q);
input CLK, D;
output reg Q;
always @(posedge CLK) begin
	Q <= D;
end
endmodule


module DFFRcell(CLK, D, RST, Q);
input CLK, D, RST;
wire x;
assign x=~RST;
output reg Q;
always @(posedge CLK, negedge x) begin
	if (!x)
		Q <= 1'b0;
	else
		Q <= D;
end
endmodule



module dffn(CLK, D,Q);
input CLK, D;
output reg Q;

always @(negedge CLK) begin
	Q <= D;
end



endmodule

module dffsr(CLK, D, CLEAR, PRESET, Q);
input CLK, D, CLEAR, PRESET;
output reg Q;

always @(posedge CLK, posedge CLEAR, posedge PRESET) begin
	if (CLEAR)
		Q <= 0;
	else if (PRESET)
		Q <= 1;
	else
		Q <= D;
end
endmodule
