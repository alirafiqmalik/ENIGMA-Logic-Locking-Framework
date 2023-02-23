`include "topv" `timescale 1ns/10ps module testbench();
integer count;
reg N1;
reg N107;
reg N116;
reg N124;
reg N125;
reg N128;
reg N13;
reg N132;
reg N137;
reg N143;
reg N150;
reg N159;
reg N169;
reg N179;
reg N190;
reg N20;
reg N200;
reg N213;
reg N222;
reg N223;
reg N226;
reg N232;
reg N238;
reg N244;
reg N250;
reg N257;
reg N264;
reg N270;
reg N274;
reg N283;
reg N294;
reg N303;
reg N311;
reg N317;
reg N322;
reg N326;
reg N329;
reg N33;
reg N330;
reg N343;
reg N349;
reg N350;
reg N41;
reg N45;
reg N50;
reg N58;
reg N68;
reg N77;
reg N87;
reg N97;
reg [49:0] lockingkeyinput;
reg clk;
wire [21:0] Q;
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
 {N1,N107,N116,N124,N125,N128,N13,N132,N137,N143,N150,N159,N169,N179,N190,N20,N200,N213,N222,N223,N226,N232,N238,N244,N250,N257,N264,N270,N274,N283,N294,N303,N311,N317,N322,N326,N329,N33,N330,N343,N349,N350,N41,N45,N50,N58,N68,N77,N87,N97} =$random;
#10;
if(Z==0) begin
 count=count+1;
end
$fwrite(file, "%b,%b,%b,%bn", {lockingkeyinput}, {N1,N107,N116,N124,N125,N128,N13,N132,N137,N143,N150,N159,N169,N179,N190,N20,N200,N213,N222,N223,N226,N232,N238,N244,N250,N257,N264,N270,N274,N283,N294,N303,N311,N317,N322,N326,N329,N33,N330,N343,N349,N350,N41,N45,N50,N58,N68,N77,N87,N97}, Q, Z);
end
$fwrite(file, "OER:, %fn",count*100/100);
end
$finish;
$fclose(file);
end
top dut (.Q(Q),.Z(Z),.N1(N1),.N107(N107),.N116(N116),.N124(N124),.N125(N125),.N128(N128),.N13(N13),.N132(N132),.N137(N137),.N143(N143),.N150(N150),.N159(N159),.N169(N169),.N179(N179),.N190(N190),.N20(N20),.N200(N200),.N213(N213),.N222(N222),.N223(N223),.N226(N226),.N232(N232),.N238(N238),.N244(N244),.N250(N250),.N257(N257),.N264(N264),.N270(N270),.N274(N274),.N283(N283),.N294(N294),.N303(N303),.N311(N311),.N317(N317),.N322(N322),.N326(N326),.N329(N329),.N33(N33),.N330(N330),.N343(N343),.N349(N349),.N350(N350),.N41(N41),.N45(N45),.N50(N50),.N58(N58),.N68(N68),.N77(N77),.N87(N87),.N97(N97),.lockingkeyinput(lockingkeyinput));
endmodule
