import src.utils as utils
import random
import re

####################################################################################################################################
####################################################################################################################################

# "module {name} (inputs, keys, Q);\nparameter n={ic};input [n-1:0] inputs;input [n-1:0] keys;output Q;reg key = {ic}'d{key};assign Q = (ckt_output ^ ((inputs == keys) & (inputs != key)));endmodule"

def gencc_SarLock(modulename, inputs,key):
    codestr="module {name} (inputs, keys, Q);parameter n={ic};input [n-1:0] inputs;input [n-1:0] keys;output Q;assign Q = (((inputs == keys) & (inputs != {ic}'d{key})));endmodule"
    ic = len(inputs)
    comver = codestr.format(name=modulename,ic=ic,key=key)
    port=modulename+" {init} ({portnodes}, {KEY}, {Q});" 
    return re.sub(";", ";\n", comver),port


####################################################################################################################################
####################################################################################################################################


def gencc_AntiSAT(modulename, inputs):
    codestr="module {name} (A,KEY,Q); parameter n={ic}; input [n-1:0] A; input [2*n-1:0] KEY; output Q; wire Q1,Q2; wire [n-1:0] X_xor1; wire [n-1:0] X_xor2; reg [n-1:0] Q1_reg; reg [n-1:0] Q2_reg; assign X_xor1 = A ^ KEY[n-1:0]; assign X_xor2 = A ^ KEY[2*n-1:n]; integer k; always @(*) begin Q1 = 1; Q2 = 1; for(k=0;k<n-1;k=k+1) begin if(X_xor1[k]==0) Q1=0; if(X_xor2[k]==0) Q2=0; end end assign Q1_reg = {{Q1_reg[n-2:0], Q1}}; assign Q2_reg = {{Q2_reg[n-2:0], Q2\}}; assign Q = Q1_reg[n-1] & (~Q2_reg[n-1]);endmodule"
    # codestr="module {name} (A,KEY,Q);parameter n={ic};input [n-1:0] A;input [2*n-1:0] KEY;output Q;wire Q1,Q2;g_block g(A,KEY[n-1:0],Q1);g_block gc(A,KEY[2*n-1:n],Q2);assign Q = Q1 & (~Q2);endmodule"
    # submodule="module g_block(X,KEY_X,Q);parameter n={ic};input [n-1:0]X;input [n-1:0]KEY_X;output reg Q;wire [n-1:0]X_xor;assign X_xor=X^KEY_X;integer k;always@(*)begin Q=1;for(k=0;k<n-1;k=k+1)begin if(X_xor[k]==0) Q=0;end end endmodule"
    ic = len(inputs)
    
    comver = codestr.format(name=modulename,ic=ic)
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
        self.circuitgraph=module.circuitgraph

    def set_key(self,bits:int=128,inputs:list=None,outputs:list=None):
        # self.input_count={i:self.module.io['inputs'][i]['bits'] for i in self.module.io['inputs']}

        self.inputs={i:self.module.io['inputs'][i] for i in self.module.io['inputs']}
        utils.remove_key(self.inputs,"lockingkeyinput")
        utils.remove_key(self.inputs,self.module.io["Clock_pins"])

        if(inputs==None):
            self.key_inputs,returned_bits=utils.rand_selection(self.inputs,'bits',bits)
            bits=returned_bits
            self.key=utils.randKey(bits, seed=None)
        else:     
            # self.key_inputs=inputs
            self.key_inputs={i:self.module.io['inputs'][i] for i in inputs}
            bits=len(self.key_inputs)
            self.key=utils.randKey(bits, seed=None)

        # self.keystart=len(self.module.bitkey)

        self.bits=bits
        self.intkey,self.bitkey=utils.randKey(bits)
        self.module.bitkey=self.bitkey+self.module.bitkey

        if(outputs==None):
            self.key_outputs={i:self.module.io['outputs'][i] for i in self.module.io['outputs']}
        else:     
            # self.key_outputs=outputs
            self.key_outputs={i:self.module.io['outputs'][i] for i in outputs}


    def AntiSAT(self):
        no_of_init=len(self.module.linkages)
        modulename=f"antisat_{no_of_init}"
        nodes,ic=utils.node_to_txt(self.key_inputs,mode="input",return_bits=True)
        initname=f"{modulename}_init{self.module.module_name}_{no_of_init}"

        c=len(self.module.io['wires'])

        outQ=f"Q_int_{c}"

        lockinginputs_count=len(self.module.lockingdata["inputs"])
        a=lockinginputs_count+ic-1
        b=lockinginputs_count
        links=[]
        port=""
        portnodes=""
        for i in self.key_inputs:
            links.append((i,i,"I"))
            port+=f".{i}({i}), "
            portnodes+=f"{i}, "
        portnodes=portnodes[:-2]
        port+=f".KEY(lockingkeyinput[{a}:{b}]), "
        port+=f".Q({outQ})"

        links.append(("KEY",f"lockingkeyinput[{a}:{b}]","I"))
        links.append(("Q",outQ,"O"))

        tmp,port_null=gencc_AntiSAT(modulename, self.inputs)
        # tmp=f"module {modulename}({portnodes}, KEY, Q);\n{nodes}input [{ic-1}:0] KEY;\nwire [{ic-1}:0] A;\nassign A={{{portnodes}}};\noutput reg Q;\nalways@(*)begin \nif(A==KEY)Q=1;\nelse Q=0;\nend \nendmodule"

        self.module.io['wires'][outQ]=utils.connector(1,0,0)

        self.module.linkages[initname]={"module_name": modulename,"links":links,"port":port,"code":tmp}
        print(utils.connector(a+1,0,a),utils.connector(a+1,0,a))
        if("lockingkeyinput" not in self.module.io['inputs']):
            self.module.io['inputs']["lockingkeyinput"]=utils.connector(a+1,0,a)
            self.module.io["input_ports"]+="lockingkeyinput,"
        else:
            self.module.io['inputs']["lockingkeyinput"]=utils.connector(a+1,0,a)
        

        for i,bitval in enumerate(range(b,a+1)):
            keygate_input_name=f"lockingkeyinput[{bitval}]"
            bit=self.bitkey[self.bits-i-1]
            # print(self.bits-i-1,self.bitkey[self.bits-i-1])
            # print(bit,key_bit-1-i)
            # bit="0" if new_gatetype=="XOR" else "1" 
            # self.keyint,self.bitkey=randKey(self.keycount)
            self.module.lockingdata["inputs"].append((keygate_input_name,bit))

    def Sarlock(self):
        no_of_init=len(self.module.linkages)
        modulename=f"antisat_{no_of_init}"
        nodes,ic=utils.node_to_txt(self.key_inputs,mode="input",return_bits=True)
        initname=f"{modulename}_init{self.module.module_name}_{no_of_init}"

        c=len(self.module.io['wires'])

        outQ=f"Q_int_{c}"

        lockinginputs_count=len(self.module.lockingdata["inputs"])
        a=lockinginputs_count+ic-1
        b=lockinginputs_count
        links=[]
        port=""
        portnodes=""
        for i in self.key_inputs:
            links.append((i,i,"I"))
            port+=f".{i}({i}), "
            portnodes+=f"{i}, "
        portnodes=portnodes[:-2]
        port+=f".KEY(lockingkeyinput[{a}:{b}]), "
        port+=f".Q({outQ})"

        links.append(("KEY",f"lockingkeyinput[{b}:{a}]","I"))
        links.append(("Q",outQ,"O"))

        # tmp,port_null=gencc_SarLock(modulename, self.inputs, self.bitkey)
        # tmp=f"module {modulename}({portnodes}, KEY, Q);{nodes}input [{ic-1}:0] KEY;\nwire [{ic-1}:0] A;\nassign A={{{portnodes}}};\noutput reg Q;\nalways@(*)begin \nif(A==KEY)Q=1;\nelse Q=0;\nend \nendmodule"
        # tmp=f"module {modulename}({portnodes}, KEY, Q);\n{nodes}input [{ic-1}:0] KEY;\nwire [{ic-1}:0] A;\nassign A={{{portnodes}}};\noutput Q;\nassign Q = (((A == KEY) & (A != {ic}'b{self.bitkey})));\nendmodule"
        tmp=f"module {modulename}({portnodes}, KEY, Q);{nodes} input [{ic-1}:0] KEY;wire [{ic-1}:0] A;assign A={{{portnodes}}};output Q;assign Q=((A == KEY) & (A !={ic}'b{self.bitkey}));endmodule"



        self.module.io['wires'][outQ]=utils.connector(1,0,0)

        self.module.linkages[initname]={"module_name": modulename,"links":links,"port":port,"code":tmp}

        if("lockingkeyinput" not in self.module.io['inputs']):
            self.module.io['inputs']["lockingkeyinput"]=utils.connector(a+1,0,a)
            self.module.io["input_ports"]+="lockingkeyinput,"
        else:
            self.module.io['inputs']["lockingkeyinput"]=utils.connector(a+1,0,a)
        
        for i,bitval in enumerate(range(b,a+1)):
            keygate_input_name=f"lockingkeyinput[{bitval}]"
            bit=self.bitkey[self.bits-i-1]
            self.module.lockingdata["inputs"].append((keygate_input_name,bit))
        
        # print(self.key_outputs.keys())
        for output in self.key_outputs:
            gatetype="XOR"
            output_data=self.key_outputs[output]
            if(output_data['bits']!=1):
                start=output_data["startbit"]
                end=output_data["endbit"]
                cal_output_i=lambda output,bit_i:f"{output}[{bit_i}]"
            else:
                start=end=1
                cal_output_i=lambda output,_:f"{output}"
            
            for bit_i in range(start,end+1):
                output_i=cal_output_i(output,bit_i)
                keygatecount=len(self.module.gates)
                wirecount=len(self.module.io['wires'])

                # print(output_i,bit_i)


                # print("output  ",output_i)
                pred_i=list(self.circuitgraph.predecessors(output_i))
                if(pred_i==[]):
                    continue
                else:
                    # print("HERE  ",pred_i)
                    pred_i=pred_i[0]

                connection_gate=f"connection_gate_Sarlock_{output}_{bit_i}_{keygatecount}"
                connection_wire=f"connection_wire_Sarlock_{output}_{bit_i}_{wirecount}"


                self.circuitgraph.remove_edge(pred_i, output_i)

                self.circuitgraph.add_node(connection_gate,type="gate",logic=gatetype)
                self.circuitgraph.add_node(connection_wire,type="wire",logic=connection_wire)
                
                self.circuitgraph.add_edge(pred_i, connection_wire)
                self.circuitgraph.add_edge(connection_wire, connection_gate)
                self.circuitgraph.add_edge(outQ, connection_gate)
                self.circuitgraph.add_edge(connection_gate, output_i)

                
                # pred_i, output_i
                Na=self.circuitgraph.nodes[pred_i]
                # Nb=self.circuitgraph.nodes[NodeB]
                # print(NodeA,Na)
                if(Na['type']=='gate'):
                    self.module.gates[Na['logic']][pred_i]['outputs']=connection_wire
                elif('DFF' in Na['type'].upper()):
                    # print("here ",Na,pred_i)
                    # print(self.module.FF_tech[Na['type']][pred_i])
                    self.module.FF_tech[Na['type']][pred_i]['outputs']=connection_wire
                    # print(self.module.FF_tech[Na['type']][pred_i])
                else:
                    raise Exception("NOT A GATE WHYYYYYY???????????")
                

                self.module.io['wires'][connection_wire]=utils.connector(1,0,0)

                if(gatetype not in self.module.gates.keys()):
                    self.module.gates[gatetype]={}
                    
                self.module.gates[gatetype][connection_gate]={"inputs": [connection_wire,outQ] ,"outputs": output_i}
            
        