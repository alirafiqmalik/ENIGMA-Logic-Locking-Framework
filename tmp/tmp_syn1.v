module top(CLOCK_50,KEY_N,SW,vga_x,vga_y,vga_plot,vga_colour);
input CLOCK_50;
input [9:0]SW;
input [3:0]KEY_N;
output reg [7:0] vga_x;
output reg [6:0] vga_y;
output reg [2:0]vga_colour;
output reg vga_plot;
wire [7:0] x;
wire [6:0] y;
wire [7:0] xc;
wire [6:0] yc;
assign xc=79;
assign yc=59;
wire [7:0] x1,x2;
wire [6:0] y1,y2;
wire Reset,key,writeR,plotclear,plotcircle;
wire Done,Clear;
assign Reset=KEY_N[3];
assign key=KEY_N[0];
wire [2:0]colourcircle;
wire [2:0]colourclear;
always@(*)begin
 if(Done)begin
 vga_x=x2;
vga_y=y2;
vga_plot=plotcircle;
vga_colour=colourcircle;
end
else begin
 vga_x=x1;
vga_y=y1;
vga_plot=plotclear;
vga_colour=colourclear;
end
end
task2 T2(CLOCK_50,Reset,SW[9],x1,y1,colourclear,plotclear,Done);
task3 T3(CLOCK_50,Reset,Done,key,xc,yc,SW[8:0],x,y,x2,y2,plotcircle,colourcircle);
endmodule
module task3(CLOCK_50,Reset,Done,key,xc,yc,SW,x,y,xp,yp,plot,colourcircle);
input key,Reset,Done;
input CLOCK_50;
output reg [7:0] xp;
output reg [6:0] yp;
output reg [7:0] x;
output reg [6:0] y;
output reg [2:0]colourcircle;
output plot;
input [7:0] xc;
input [6:0] yc;
input [8:0] SW;
wire ch;
assign ch=(x>y);
reg [5:0]r;
reg [3:0]state,nstate;
parameter R=4'd0,P1=4'd1,P2=4'd2,P3=4'd3,P4=4'd4,P5=4'd5,P6=4'd6,P7=4'd7,P8=4'd8;
always@(*)begin
 case(state) R:nstate=key?R:P1;
P1:nstate=P2;
P2:nstate=P3;
P3:nstate=P4;
P4:nstate=P5;
P5:nstate=P6;
P6:nstate=P7;
P7:nstate=(y==0)?R:P8;
P8:nstate=ch?R:P1;
default:nstate=state;
endcase end
always@(posedge CLOCK_50,negedge Reset)begin
 if(~Reset)state<=R;
else if(Done) state<=nstate;
else state<=state;
end
reg [8:0]d;
always@(posedge CLOCK_50)begin
 case(state) R:begin
 if(SW[8:3]>59) r=59;
else r=SW[8:3];
colourcircle=SW[2:0];
d=(9'd3)-(9'd2*r);
x=(8'd0);
y=r;
xp=xc + x;
yp=yc + y;
end
P1:begin
 xp=xc + x;
yp=yc + y;
end
P2:begin
 xp=xc - x;
yp=yc + y;
end
P3:begin
 xp=xc + x;
yp=yc - y;
end
P4:begin
 xp=xc - x;
yp=yc - y;
end
P5:begin
 xp=xc + y;
yp=yc + x;
end
P6:begin
 xp=xc - y;
yp=yc + x;
end
P7:begin
 xp=xc + y;
yp=yc - x;
end
P8:begin
 xp=xc - y;
yp=yc - x;
x=x+8'd1;
if ((d>256))begin
 d=d+((9'd4)*x)+(9'd6);
end
else if ((d<=256))begin
 d=d+((9'd4)*(x-y))+(9'd10);
y=y-7'd1;
end
else d=d;
end
endcase end
assign plot=~(state==R);
endmodule
module task2(CLOCK_50,Reset,Enable,x,y,colour,plot,Done);
input CLOCK_50,Reset,Enable;
output reg plot;
output reg[2:0]colour;
output reg [7:0] x;
output reg [6:0] y;
output Done;
always@(posedge CLOCK_50,negedge Reset)begin
 if(~Reset)begin
 plot<=1;
x<=0;
y<=0;
end
else if((x<159)) begin
 x<=x+1;
colour<=Enable?(y%8):3'b000;
end
else if(x==159 & y<119) begin
 y<=y+1;
x<=0;
end
else if((y==119)&(x==159))begin
 plot<=0;
end
else begin
 x<=0;
y<=0;
end
end
assign Done=(~plot);
endmodule
 