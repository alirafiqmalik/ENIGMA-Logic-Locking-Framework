module INV_X12(I, ZN);
input I;
output ZN;
assign ZN=~I;
endmodule


module BUF_X8(I, Z);
input I;
output Z;
assign Z=I;
endmodule

module INV_X8(I, ZN);
input I;
output ZN;
assign ZN=~I;
endmodule


module BUF_X4(I, Z);
input I;
output Z;
assign Z=I;
endmodule

module INV_X4(I, ZN);
input I;
output ZN;
assign ZN=~I;
endmodule

module BUF_X2(I, Z);
input I;
output Z;
assign Z=I;
endmodule

module INV_X2(I, ZN);
input I;
output ZN;
assign ZN=~I;
endmodule

module AND2_X2(A1, A2, Z);
input A1, A2;
output Z;
assign Z=(A1 & A2);
endmodule

module OR2_X2(A1, A2, Z);
input A1, A2;
output Z;
assign Z=(A1 | A2);
endmodule

module NAND2_X2(A1, A2, ZN);
input A1, A2;
output ZN;
assign ZN=~(A1 & A2);
endmodule


module NOR2_X2(A1, A2, ZN);
input A1, A2;
output ZN;
assign ZN=~(A1 | A2);
endmodule


module XOR2_X2(A1, A2, Z);
input A1, A2;
output Z;
assign Z=(A1 ^ A2);
endmodule

module XNOR2_X2(A1, A2, ZN);
input A1, A2;
output ZN;
assign ZN=~(A1 ^ A2);
endmodule


module BUF_X1(I, Z);
input I;
output Z;
assign Z=I;
endmodule

module INV_X1(I, ZN);
input I;
output ZN;
assign ZN=~I;
endmodule

module AND2_X1(A1, A2, Z);
input A1, A2;
output Z;
assign Z=(A1 & A2);
endmodule

module OR2_X1(A1, A2, Z);
input A1, A2;
output Z;
assign Z=(A1 | A2);
endmodule

module NAND2_X1(A1, A2, ZN);
input A1, A2;
output ZN;
assign ZN=~(A1 & A2);
endmodule


module NOR2_X1(A1, A2, ZN);
input A1, A2;
output ZN;
assign ZN=~(A1 | A2);
endmodule


module XOR2_X1(A1, A2, Z);
input A1, A2;
output Z;
assign Z=(A1 ^ A2);
endmodule

module XNOR2_X1(A1, A2, ZN);
input A1, A2;
output ZN;
assign ZN=~(A1 ^ A2);
endmodule





module DFFRNQ_X1 (D,CLK,RN,Q);
input CLK,RN, D;
output reg Q;
always @(posedge CLK,negedge RN)begin
    if(!RN)Q<=0;
    else Q <= D;
end	
endmodule



module DFFSNQ_X1 (D,CLK,SN,Q);
input CLK,SN, D;
output reg Q;
always @(posedge CLK,negedge SN)begin
    if(!SN)Q<=1;
    else Q <= D;
end	
endmodule

