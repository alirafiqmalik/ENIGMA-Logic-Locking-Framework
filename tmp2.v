module locked(inputs, key, out);
input [7:0] inputs;
input [7:0] key;
output out;
wire lock_out;
sarlock s(.inputs(inputs), .key(key), .lock_out(lock_out));
assign out = lock_out;
endmodule

module ckt(a,b,c);
input [3:0] a,b;
output [4:0] c;
assign	c = a + b;
endmodule

module sarlock (inputs, key, lock_out);
input [7:0] inputs;
input [7:0] key;
output lock_out;
wire [4:0]ckt_out;
ckt c(.a(inputs[3:0]), .b(inputs[7:4]), .c(ckt_out));

reg keyx = 8'b01101101;
assign lock_out =ckt_out[0] ^((inputs == key) & (inputs != keyx)); 
endmodule
