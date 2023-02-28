// memory_with_timer my_memory #(
//     .n(n), // 10 bits for the address
//     .m(m)   // 4 bits for the memory at each address
// ) (
//     .clk(clk),
//     .reset(reset),
//     .count_up_key(count_up_key),
//     .count_down_key(count_down_key),
//     .address(address),
//     .data_out(data_out)
// );

	


module memory_with_timer (
    clk,
    reset,
    count_up_key,
    count_down_key,
    address,
    data_out
);

    parameter n = 2; // Number of address bits
    parameter m = 8; // Number of memory bits per address

    input clk;
    input reset;
    input count_up_key;
    input count_down_key;
    output [n-1:0] address;
    output [m-1:0] data_out;

    reg [n-1:0] address_reg;
    reg [m-1:0] memory [0:2^n-1];

    // Initialize memory with initial values
    initial begin
			integer i;
        for (i = 0; i < (2**n); i=i+1) begin
            memory[i] = i % (2**m);
        end
    end

    // Assign outputs
    assign address = address_reg;
    assign data_out = memory[address_reg];

    // Count-up and count-down logic
    always @ (posedge clk or posedge reset) begin
        if (reset) begin
            address_reg <= 0;
        end else begin
            if (count_up_key && !count_down_key) begin
                address_reg <= address_reg + 1;
            end else if (!count_up_key && count_down_key) begin
                address_reg <= address_reg - 1;
            end
        end
    end

endmodule
