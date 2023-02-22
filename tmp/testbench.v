`include "topv" `timescale 1ns/10ps module testbench();
integer count;
reg [7:0] inputs;
reg [7:0] key;
reg [255:0] lockingkeyinput;
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
 {inputs,key} =$random;
#10;
if(Z==0) begin
 count=count+1;
end
$fwrite(file, "%b,%b,%b,%bn", {lockingkeyinput}, {inputs,key}, Q, Z);
end
$fwrite(file, "OER:, %fn",count*100/100);
end
$finish;
$fclose(file);
end
top dut (.Q(Q),.Z(Z),.inputs(inputs),.key(key),.lockingkeyinput(lockingkeyinput));
endmodule
