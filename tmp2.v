module {name} ({portnodes},KEY,Q);
{nodes}
input [2*{ic}-1:0] KEY;
output Q;
wire [{ic-1}:0]A;
assign A={portnodes};
wire Q1,Q2;
g_block g(A,KEY[{ic}-1:0],Q1);
g_block gc(A,KEY[2*{ic}-1:n],Q2);
assign Q = Q1 & (~Q2);
endmodule


module {module_name}({portnodes},KEY,Q);
{nodes}
input [{ic-1}:0]KEY;
wire [{ic-1}:0]A;
assign A={portnodes};
output reg Q;
always@(*)begin if(A==KEY)Q=1;
else Q=0;
end endmodule"

            