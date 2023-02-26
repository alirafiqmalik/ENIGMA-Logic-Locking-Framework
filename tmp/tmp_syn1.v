module c17 (tin,N3,N6,N7,N22,N23);
input [1:0]tin;
input N3,N6,N7;
output N22,N23;
wire N10,N11,N16,N19;
nand NAND2_1 (N10, tin[0], N3);
nand NAND2_2 (N11, N3, N6);
nand NAND2_3 (N16, tin[1], N11);
nand NAND2_4 (N19, N11, N7);
nand NAND2_5 (N22, N10, N16);
nand NAND2_6 (N23, N16, N19);
endmodule
