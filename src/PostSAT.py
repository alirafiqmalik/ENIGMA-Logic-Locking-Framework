import src.utils as utils
import random
import re

####################################################################################################################################
####################################################################################################################################

# "module {name} (inputs, keys, lock_output);parameter n={ic};input [n-1:0] inputs;input [n-1:0] keys;output lock_output;reg key = {ic}'d{key};assign lock_output = (ckt_output ^ ((inputs == keys) & (inputs != key)));endmodule"

def gencc_SarLock(modulename, inputs,key):
    codestr="module {name} (inputs, keys, lock_output);parameter n={ic};input [n-1:0] inputs;input [n-1:0] keys;output lock_output;reg key = {ic}'d{key};assign lock_output = (((inputs == keys) & (inputs != key)));endmodule"
    ic = len(inputs)
    comver = codestr.format(name=modulename,ic=ic,key=key)
    port=modulename+" {init} ({portnodes}, {KEY}, {Q});" 
    return re.sub(";", ";\n", comver),port















####################################################################################################################################
####################################################################################################################################


def gencc_AntiSAT(modulename, inputs):
    codestr="module {name} (A,KEY,Q);parameter n={ic};input [n-1:0] A;input [2*n-1:0] KEY;output Q;wire Q1,Q2;g_block g(A,KEY[n-1:0],Q1);g_block gc(A,KEY[2*n-1:n],Q2);assign Q = Q1 & (~Q2);endmodule"
    submodule="module g_block(X,KEY_X,Q);parameter n={ic};input [n-1:0]X;input [n-1:0]KEY_X;output reg Q;wire [n-1:0]X_xor;assign X_xor=X^KEY_X;integer k;always@(*)begin Q=1;for(k=0;k<n-1;k=k+1)begin if(X_xor[k]==0) Q=0;end end endmodule"
    ic = len(inputs)
    
    comver = codestr.format(name=modulename,ic=ic)+f"\n\n{submodule}"
    port=modulename+" {init} ({portnodes}, {KEY}, {Q});" 
    

    return re.sub(";", ";\n", comver),port


####################################################################################################################################
####################################################################################################################################

def gencc(modulename, inputs, key):
    ic = len(inputs)
    portnodes, inputnodes,_ = utils.io_port(inputs)
    if (key == None):
        comver = "module "+modulename+"("+portnodes+",KEY,Q);" + inputnodes + "input ["+str(ic-1)+":0]KEY;" + "wire ["+str(
            ic-1)+":0]A;assign A={"+portnodes+"};output reg Q;always@(*)begin if(A==KEY)Q=1;else Q=0;end endmodule"
        port=modulename+" {init} ({portnodes}, {KEY}, {Q});" 
             
    else:
        comver = "module "+modulename+"("+portnodes+",Q);" + inputnodes + "wire ["+str(
            ic-1)+":0]A;assign A={"+portnodes+"};output reg Q;always@(*)begin if(A=="+str(ic)+"'d"+str(key)+")Q=1;else Q=0;end endmodule"
        port=modulename+" {init} ({portnodes}, {Q});" 
        

    return re.sub(";", ";\n", comver), portnodes,port


####################################################################################################################################
####################################################################################################################################


def hammingcc(modulename, inputs, h, key=None):
    ic = len(inputs)
    portnodes, inputnodes,_ = utils.io_port(inputs)
    # print("HERE ",utils.io_port(inputs))
    if (key == None):
        comver = "module "+modulename+"("+portnodes+",KEY,Q);" + inputnodes + "input ["+str(ic-1)+":0]KEY;wire ["+str(
            ic-1)+":0]A;assign A={"+portnodes+"};output reg Q;integer Qr,count,i;always@(*)begin Qr=KEY^A;count=0;for(i=0;i<"+str(ic)+";i=i+1)begin if(Qr[i]) count=count+1;end if(count=="+str(h)+")Q=1;else Q=0;end endmodule"
        port=modulename+" {init} ("+portnodes+",{key},{Q});"
    else:
        comver = "module "+modulename+"("+portnodes+",Q);" + inputnodes + " wire ["+str(ic-1)+":0]A;assign A={"+portnodes+"};output reg Q;integer Qr,count,i;always@(*)begin Qr="+str(
            ic)+"'d"+str(key)+"^A;count=0;for(i=0;i<"+str(ic)+";i=i+1)begin if(Qr[i]) count=count+1;end if(count=="+str(h)+")Q=1;else Q=0;end endmodule"
        port=modulename+" {init} ("+portnodes+",{Q});"
    return re.sub(";", ";\n", comver), portnodes,port









class PostSAT:
    def __init__(self,module) -> None:
        self.module=module

    def set_key(self, n, key=None,inputs=None,outputs=None):
        self.keycount=n
        if(key==None):
            self.keyint,self.bitkey=utils.randKey(self.keycount)
        else:  
            self.keyint=key
            self.bitkey = format(key, "b")

        if (n > len(self.bitkey)):
            self.bitkey = format(self.keyint, "0"+str(n)+"b")
        elif (n < len(self.bitkey)):
            print("ERROR")
            print("Number of Gates < Number of Key-Bits")
            return None
        self.module.bitkey=self.bitkey+self.module.bitkey
        print(self.module.bitkey)

        if(inputs==None):    
            tmpin=self.module.io['inputs'].copy()
            utils.remove_key(tmpin,"lockingkeyinput")
            utils.remove_key(tmpin,self.module.io["Clock_pins"])
            
            self.inputs={}
            self.inputs=utils.rand_selection(tmpin,"bits",self.keycount)
            # print(self.keycount,self.inputs)
        else:
            sum_counts = sum(inputs[key]['bits'] for key in inputs)
            if(sum_counts!=self.keycount):
                raise Exception(f"Keybits for inputs {inputs} must be less than equal to total input bits count ")
        
        
        if(outputs==None):
            self.outputs=self.module.io['outputs']
        else:
            self.outputs=self.module.io['outputs']

 
    def AntiSAT(self):
        no_of_init=len(self.module.linkages)
        modulename=f"antisat_{no_of_init}"
        nodes,ic=utils.node_to_txt(self.inputs,mode="input",return_bits=True)
        initname=f"{modulename}_init{self.module.module_name}_{no_of_init}"

        c=len(self.module.io['wires'])

        outQ=f"Q_int_{c}"

        lockinginputs_count=len(self.module.lockingdata["inputs"])
        a=lockinginputs_count+ic-1
        b=lockinginputs_count
        links=[]
        port=""
        portnodes=""
        for i in self.inputs:
            links.append((i,i,"I"))
            port+=f".{i}({i}), "
            portnodes+=f"{i}, "
        portnodes=portnodes[:-2]
        port+=f".KEY(lockingkeyinput[{b}:{a}]), "
        port+=f".Q({outQ})"

        links.append(("KEY",f"lockingkeyinput[{b}:{a}]","I"))
        links.append(("Q",outQ,"O"))

        tmp=f"module {modulename}({portnodes}, KEY, Q);\n{nodes}input [{ic-1}:0] KEY;\nwire [{ic-1}:0] A;\nassign A={{{portnodes}}};\noutput reg Q;\nalways@(*)begin \nif(A==KEY)Q=1;\nelse Q=0;\nend \nendmodule"

        self.module.io['wires'][outQ]=utils.connector(1,0,0)

        # self.module.linkages={}
        self.module.linkages[initname]={"module_name": modulename,"links":links,"port":port,"code":tmp}
        
        if("lockingkeyinput" not in self.module.io['inputs']):
            self.module.io['inputs']["lockingkeyinput"]=utils.connector(a+1,0,a)
            self.module.io["input_ports"]+="lockingkeyinput,"
        else:
            self.module.io['inputs']["lockingkeyinput"]=utils.connector(a+1,0,a)
        
        key_bit=len(self.bitkey)
        # print("here",key_bit,range(b,a+1))
        for i,bitval in enumerate(range(b,a+1)):
            keygate_input_name=f"lockingkeyinput[{bitval}]"
            bit=self.bitkey[key_bit-1-i]
            # print(bit,key_bit-1-i)
            # bit="0" if new_gatetype=="XOR" else "1" 
            # self.keyint,self.bitkey=randKey(self.keycount)
            self.module.lockingdata["inputs"].append((keygate_input_name,bit))
        
        








