`include "top.v" `timescale 1ns/10ps module testbench();
integer count,xc;
reg CLOCK_50;
reg [3:0] KEY_N;
reg [9:0] SW;
reg [49:0] lockingkeyinput;
reg clk;
wire [18:0] Q;
wire Z;
integer file;
initial begin
 file = $fopen("logfile.txt", "w");
clk = 0;
forever begin
 #5 clk = ~clk;
end
end
initial begin
 xc=0;
repeat (32) begin
 if(xc==10)begin
 {lockingkeyinput} =50'b11010101111010101101010000111011101010011101110101;
$fwrite(file, "iteration with Correct key \n");
end
else begin
 {lockingkeyinput} =$random;
$fwrite(file, "iteration \n ");
end
$fwrite(file, "keyinputs,Inputs,Q,Z \n");
count=0;
xc=xc+1;
repeat (100) begin
 {CLOCK_50,KEY_N,SW} =$random;
#10;
if(Z==0) begin
 count=count+1;
end
$fwrite(file, "%b,%b,%b,%b \n", {lockingkeyinput}, {CLOCK_50,KEY_N,SW}, Q, Z);
end
$fwrite(file, "OER:, %f \n ",count*100/100);
end
$finish;
$fclose(file);
end
top dut (.Q(Q),.Z(Z),.CLOCK_50(CLOCK_50),.KEY_N(KEY_N),.SW(SW),.lockingkeyinput(lockingkeyinput));
endmodule
