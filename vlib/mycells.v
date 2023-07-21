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
always @(posedge C) begin
	Q <= D;
end
endmodule


module DFFRcell(C, D, Q, R);
input C, D, R;
wire x;
assign x=~R;
output reg Q;
always @(posedge C, negedge x) begin
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

module dffsr(input CLK, D, CLEAR, PRESET, output reg Q);
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
