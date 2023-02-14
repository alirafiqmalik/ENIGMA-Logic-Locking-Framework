module locked(inputA, inputB, out);
input [7:0] inputA;
input [7:0] inputB;
output [8:0] out;
assign out=inputA+inputB;
endmodule





// module locked(inputs, key, out);
// input [7:0] inputs;
// input [7:0] key;
// output [1:0]out;
// sarlock s(.inputs(inputs), .key(key), .lock_out(out[0]));
// sarlock s1(.inputs(inputs), .key(key), .lock_out(out[1]));
// endmodule

// module ckt(a,b,c);
// input [3:0] a,b;
// output [4:0] c;
// assign	c = a + b;
// endmodule

// module sarlock (inputs, key, lock_out);
// input [7:0] inputs;
// input [7:0] key;
// output lock_out;
// wire [4:0]ckt_out; 
// reg keyx = 8'b01101101;
// assign lock_out =ckt_out[0]^( (inputs == key) & (inputs != keyx));
// ckt c(.a(inputs[3:0]), .b(inputs[7:4]), .c(ckt_out));
// endmodule

