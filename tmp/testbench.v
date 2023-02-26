`include "topv" `timescale 1ns/10ps module testbench();
integer count;
reg N3;
reg N6;
reg N7;
reg [1:0] tin;
reg lockingkeyinput;
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
 {lockingkeyinput} =$random;
$fwrite(file, "iterationn");
$fwrite(file, "keyinputs,Inputs,Q,Zn");
count=0;
repeat (100) begin
 {N3,N6,N7,tin} =$random;
#10;
if(Z==0) begin
 count=count+1;
end
$fwrite(file, "%b,%b,%b,%bn", {lockingkeyinput}, {N3,N6,N7,tin}, Q, Z);
end
$fwrite(file, "OER:, %fn",count*100/100);
end
$finish;
$fclose(file);
end
top dut (.Q(Q),.Z(Z),.N3(N3),.N6(N6),.N7(N7),.tin(tin),.lockingkeyinput(lockingkeyinput));
endmodule
