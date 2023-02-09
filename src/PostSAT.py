import src.utils as utils
import re

####################################################################################################################################
####################################################################################################################################

# "module {name} (inputs, keys, lock_output); parameter n={ic};input [n-1:0] inputs;input [n-1:0] keys;output lock_output;reg key = {ic}'d{key}; assign lock_output = (ckt_output ^ ((inputs == keys) & (inputs != key))); endmodule"

def gencc_SarLock(modulename, inputs,key):
    codestr="module {name} (inputs, keys, lock_output); parameter n={ic};input [n-1:0] inputs;input [n-1:0] keys;output lock_output;reg key = {ic}'d{key}; assign lock_output = (((inputs == keys) & (inputs != key))); endmodule"
    ic = len(inputs)
    portnodes, _,_ = utils.io_port(inputs)
    
    comver = codestr.format(name=modulename,ic=ic,key=key)
    port=modulename+" {init} ("+"{portnodes},"+"{KEY}"+",{Q}); "

    return re.sub(";", ";\n", comver), portnodes,port



####################################################################################################################################
####################################################################################################################################


def gencc_AntiSAT(modulename, inputs):
    codestr="module {name} (A,KEY,Q);parameter n={ic};input [n-1:0] A; input [2*n-1:0] KEY; output Q; wire Q1,Q2; g_block g(A,KEY[n-1:0],Q1); g_block gc(A,KEY[2*n-1:n],Q2); assign Q = Q1 & (~Q2);endmodule \n\nmodule g_block(X,KEY_X,Q);parameter n={ic};input [n-1:0]X;input [n-1:0]KEY_X;output reg Q;wire [n-1:0]X_xor;assign X_xor=X^KEY_X;integer k;always@(*)begin Q=1;for(k=0;k<n-1;k=k+1)begin if(X_xor[k]==0) Q=0;end end endmodule"
    ic = len(inputs)
    portnodes, _,_ = utils.io_port(inputs)
    
    comver = codestr.format(name=modulename,ic=ic)
    port=modulename+" {init} ("+"{portnodes},"+"{KEY}"+",{Q}); "

    return re.sub(";", ";\n", comver), portnodes,port


####################################################################################################################################
####################################################################################################################################

def gencc(modulename, inputs, key):
    ic = len(inputs)
    portnodes, inputnodes,_ = utils.io_port(inputs)
    if (key == None):
        comver = "module "+modulename+"("+portnodes+",KEY,Q); " + inputnodes + "input ["+str(ic-1)+":0]KEY;" + " wire ["+str(
            ic-1)+":0]A; assign A={"+portnodes+"}; output reg Q; always@(*)begin if(A==KEY)Q=1;else Q=0;end endmodule"
        port=modulename+" {init} ("+portnodes+",{key},{Q}); "
    else:
        comver = "module "+modulename+"("+portnodes+",Q); " + inputnodes + " wire ["+str(
            ic-1)+":0]A; assign A={"+portnodes+"}; output reg Q; always@(*)begin if(A=="+str(ic)+"'d"+str(key)+")Q=1;else Q=0;end endmodule"
        port=modulename+" {init} ("+portnodes+",{Q}); "

    return re.sub(";", ";\n", comver), portnodes,port


####################################################################################################################################
####################################################################################################################################


def hammingcc(modulename, inputs, h, key=None):
    ic = len(inputs)
    portnodes, inputnodes,_ = utils.io_port(inputs)
    # print("HERE ",utils.io_port(inputs))
    if (key == None):
        comver = "module "+modulename+"("+portnodes+",KEY,Q); " + inputnodes + "input ["+str(ic-1)+":0]KEY; wire ["+str(
            ic-1)+":0]A; assign A={"+portnodes+"}; output reg Q; integer Qr,count,i; always@(*)begin Qr=KEY^A;count=0; for(i=0;i<"+str(ic)+";i=i+1)begin if(Qr[i]) count=count+1;end if(count=="+str(h)+")Q=1;else Q=0; end endmodule"
        port=modulename+" {init} ("+portnodes+",{key},{Q}); "
    else:
        comver = "module "+modulename+"("+portnodes+",Q); " + inputnodes + " wire ["+str(ic-1)+":0]A; assign A={"+portnodes+"}; output reg Q; integer Qr,count,i; always@(*)begin Qr="+str(
            ic)+"'d"+str(key)+"^A;count=0; for(i=0;i<"+str(ic)+";i=i+1)begin if(Qr[i]) count=count+1;end if(count=="+str(h)+")Q=1;else Q=0; end endmodule"
        port=modulename+" {init} ("+portnodes+",{Q}); "
    return re.sub(";", ";\n", comver), portnodes,port


