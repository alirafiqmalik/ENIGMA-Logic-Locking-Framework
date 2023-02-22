`include "topv" `timescale 1ns/10ps module testbench();
integer count;
reg N1;
reg N2;
reg N3;
reg N6;
reg N7;
reg clk;
wire [1:0] Q;
wire Z;
integer file;
initial begin
 file = $fopen("logfiletxt", "w");
clk = 0;
forever begin
 #5 clk = ~clk;
end
end
initial begin
 repeat (32) begin
 {} =$random;
$fwrite(file, "iterationn");
$fwrite(file, "keyinputs,Inputs,Q,Zn");
count=0;
repeat (100) begin
 {N1,N2,N3,N6,N7} =$random;
#10;
if(Z==0) begin
 count=count+1;
end
$fwrite(file, "%b,%b,%b,%bn", {}, {N1,N2,N3,N6,N7}, Q, Z);
end
$fwrite(file, "OER:, %fn",count*100/100);
end
$finish;
$fclose(file);
end
top dut (.Q(Q),.Z(Z),.N1(N1),.N2(N2),.N3(N3),.N6(N6),.N7(N7),);
endmodule
