module locked(inputs, key, out);
input [7:0] inputs;
input [7:0] key;
output out;
wire lock_out;
sarlock s(.inputs(inputs), .key(key), .lock_out(lock_out));
assign out = lock_out;
endmodule
