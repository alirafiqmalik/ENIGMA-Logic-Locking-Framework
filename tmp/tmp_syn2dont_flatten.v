module ckt(a, b, c);
wire _00_;
wire _01_;
wire _02_;
wire _03_;
wire _04_;
wire _05_;
wire _06_;
wire _07_;
wire _08_;
wire _09_;
wire _10_;
wire _11_;
input [3:0] a;
wire [3:0] a;
input [3:0] b;
wire [3:0] b;
output [4:0] c;
wire [4:0] c;
AND_g _12_ ( .A(a[0]), .B(b[0]), .Y(_00_) );
NAND_g _13_ ( .A(a[1]), .B(b[1]), .Y(_01_) );
XOR_g _14_ ( .A(a[1]), .B(b[1]), .Y(_02_) );
NAND_g _15_ ( .A(_00_), .B(_02_), .Y(_03_) );
XOR_g _16_ ( .A(_00_), .B(_02_), .Y(c[1]) );
NAND_g _17_ ( .A(_01_), .B(_03_), .Y(_04_) );
NAND_g _18_ ( .A(a[2]), .B(b[2]), .Y(_05_) );
XOR_g _19_ ( .A(a[2]), .B(b[2]), .Y(_06_) );
NAND_g _20_ ( .A(_04_), .B(_06_), .Y(_07_) );
XOR_g _21_ ( .A(_04_), .B(_06_), .Y(c[2]) );
NAND_g _22_ ( .A(_05_), .B(_07_), .Y(_08_) );
NAND_g _23_ ( .A(a[3]), .B(b[3]), .Y(_09_) );
XOR_g _24_ ( .A(a[3]), .B(b[3]), .Y(_10_) );
NAND_g _25_ ( .A(_08_), .B(_10_), .Y(_11_) );
XOR_g _26_ ( .A(_08_), .B(_10_), .Y(c[3]) );
XOR_g _27_ ( .A(a[0]), .B(b[0]), .Y(c[0]) );
NAND_g _28_ ( .A(_09_), .B(_11_), .Y(c[4]) );
endmodule
module locked(inputs, key, out);
input [7:0] inputs;
wire [7:0] inputs;
input [7:0] key;
wire [7:0] key;
output [1:0] out;
wire [1:0] out;
sarlock s ( .inputs(inputs), .key(key), .lock_out(out[0]) );
sarlock s1 ( .inputs(inputs), .key(key), .lock_out(out[1]) );
endmodule
module sarlock(inputs, key, lock_out);
wire _00_;
wire _01_;
wire _02_;
wire _03_;
wire _04_;
wire _05_;
wire _06_;
wire _07_;
wire _08_;
wire _09_;
wire _10_;
wire _11_;
wire _12_;
wire _13_;
wire _14_;
wire _15_;
wire _16_;
wire _17_;
wire _18_;
wire _19_;
wire _20_;
wire _21_;
wire _22_;
wire _23_;
wire [4:0] ckt_out;
input [7:0] inputs;
wire [7:0] inputs;
input [7:0] key;
wire [7:0] key;
output lock_out;
wire lock_out;
NOT_g _24_ ( .A(inputs[3]), .Y(_00_) );
XNOR_g _25_ ( .A(inputs[0]), .B(key[0]), .Y(_01_) );
XNOR_g _26_ ( .A(inputs[7]), .B(key[7]), .Y(_02_) );
AND_g _27_ ( .A(_01_), .B(_02_), .Y(_03_) );
XNOR_g _28_ ( .A(inputs[1]), .B(key[1]), .Y(_04_) );
XNOR_g _29_ ( .A(inputs[3]), .B(key[3]), .Y(_05_) );
AND_g _30_ ( .A(_04_), .B(_05_), .Y(_06_) );
AND_g _31_ ( .A(_03_), .B(_06_), .Y(_07_) );
NOR_g _32_ ( .A(inputs[5]), .B(inputs[6]), .Y(_08_) );
NOR_g _33_ ( .A(inputs[4]), .B(inputs[7]), .Y(_09_) );
AND_g _34_ ( .A(_08_), .B(_09_), .Y(_10_) );
NOR_g _35_ ( .A(inputs[1]), .B(inputs[2]), .Y(_11_) );
AND_g _36_ ( .A(inputs[0]), .B(_00_), .Y(_12_) );
AND_g _37_ ( .A(_11_), .B(_12_), .Y(_13_) );
NAND_g _38_ ( .A(_10_), .B(_13_), .Y(_14_) );
XNOR_g _39_ ( .A(inputs[5]), .B(key[5]), .Y(_15_) );
XNOR_g _40_ ( .A(inputs[2]), .B(key[2]), .Y(_16_) );
AND_g _41_ ( .A(_15_), .B(_16_), .Y(_17_) );
XNOR_g _42_ ( .A(inputs[6]), .B(key[6]), .Y(_18_) );
XNOR_g _43_ ( .A(inputs[4]), .B(key[4]), .Y(_19_) );
AND_g _44_ ( .A(_18_), .B(_19_), .Y(_20_) );
AND_g _45_ ( .A(_17_), .B(_20_), .Y(_21_) );
AND_g _46_ ( .A(_14_), .B(_21_), .Y(_22_) );
NAND_g _47_ ( .A(_07_), .B(_22_), .Y(_23_) );
XNOR_g _48_ ( .A(ckt_out[0]), .B(_23_), .Y(lock_out) );
ckt c ( .a(inputs[3:0]), .b(inputs[7:4]), .c(ckt_out) );
endmodule
