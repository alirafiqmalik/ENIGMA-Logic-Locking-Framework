import os
import re
import random
import subprocess


#gates=['INVX1', 'AND2X1', 'OR2X1', 'NAND2X1', 'NOR2X1']
#gates=['not_g', 'and_g', 'or_g', 'nand_g', 'nor_g']
#gates=['NOT', 'AND', 'OR', 'NAND', 'NOR']
v_gates_ps="_g"
verilog_gates=['BUF_g','NOT_g', 'AND_g', 'OR_g', 'NAND_g', 'NOR_g','XOR_g','XNOR_g']
bench_gates=['DFF','BUF','NOT', 'AND', 'OR', 'NAND', 'NOR','XOR','XNOR']
gate_to_assign={'BUF':'','NOT':'~', 'AND':'&', 'OR':'|','XOR':'^','NAND':'&', 'NOR':'|','XNOR':'^'}




####################################################################################################################################
####################################################################################################################################
testbench="`include \"{top_module}.v\" `timescale 1ns/10ps \n module {testbench_module}();integer count;reg {key_inputs_p};reg {cir_inputs_p};reg clk;wire [{outputlength}:0] Q;wire Z;integer file;initial begin file = $fopen(\"{log_path}\", \"w\"); clk = 0;forever begin #5 clk = ~clk;end end initial begin repeat ({outerloop}) begin {{{key_inputs_p}}} =$random;$fwrite(file, \"iteration\\n\");$fwrite(file, \"keyinputs,Inputs,Q,Z\\n\");count=0;repeat ({innerloop}) begin {{{cir_inputs_p}}} =$random; #10;if(Z==0) begin count=count+1; end $fwrite(file, \"%b,%b,%b,%b\\n\", {{{key_inputs_p}}}, {{{cir_inputs_p}}}, Q, Z);end $fwrite(file, \"OER:, %f\\n\",count*100/{innerloop});end $finish;$fclose(file); end {top_module} dut (.Q(Q),.Z(Z),{top_port});endmodule"
# "`include \"{top_module}.v\" `timescale 1ns/10ps \n module {testbench_module}();integer count;reg {key_inputs_p};reg {cir_inputs_p};reg clk;wire [{outputlength}:0] Q;wire Z;integer file;initial begin file = $fopen(\"{log_path}\", \"w\");$fwrite(file, \"keyinputs,Inputs,Q,Z\n\"); clk = 0;forever begin #5 clk = ~clk;end end initial begin repeat (5) begin {{{key_inputs_p}}} =$random;repeat (10) begin {{{cir_inputs_p}}} =$random; #10;if(Z==1) count=count+1;$fwrite(file, \"%b,%b,%b,%b\\n\", {{{key_inputs_p}}}, {{{cir_inputs_p}}}, Q, Z);end end $finish;$fclose(file); end {top_module} dut (.Q(Q),.Z(Z),{top_port});endmodule"

def gen_miter_testbench(key_inputs_p,
                        cir_inputs_p,
                        top_port,
                        outputlength,
                        testbench_module="testbench",
                        top_module="top",
                        log_path="logfile.txt"):
    return testbench.format(testbench_module=testbench_module,
                            top_module=top_module,
                            outputlength=outputlength,
                            key_inputs_p=key_inputs_p,
                            cir_inputs_p=cir_inputs_p,
                            log_path=log_path,
                            top_port=top_port,
                            innerloop=100,
                            outerloop=32
                            )

def gen_miterCircuit(verilog,verilogLL):
    LLinp,LLport_i=extract_io_v(verilogLL)
    LLout,LLport_o=extract_io_v(verilogLL,mode="output")
    Uinp,Uport_i=extract_io_v(verilog)

    miter_circuit="module {topname}({inputport}{outputport});\n".format(topname="top",inputport=LLport_i,outputport="Q,Z")
    miter_circuit+="input {};\n".format(LLport_i[:-1])
    # miter_circuit+="output {};\n".format(LLport_o[:-1])

    keyinputs=get_diference_abs(LLinp,Uinp)
    keyinputs.sort(key=lambda x:re.findall(r"\d+",x)[0],reverse=True)
    keyporti=""
    keyports=""
    for i in keyinputs:
        keyporti+=".{}({}),".format(i,i)
        keyports+="{},".format(i)

    orgport_i=""
    orgport_o=""
    encport_o=""
    compare_o="output Z;\noutput [{}:0]Q;\n".format(len(LLout)-1)
    compare_Z="assign Z= "
    for i in Uinp:
        orgport_i+=".{}({}),".format(i,i)

    for count,i in enumerate(LLout):
        orgport_o+=".{}({}),".format(i,i+"_org")
        encport_o+=".{}({}),".format(i,i+"_enc")
        compare_o+="assign {}={}=={};\n".format("Q[{}]".format(count),i+"_enc",i+"_org")
        compare_Z+="Q[{}]&".format(count)

    compare_o+=compare_Z[:-1]+";\n"


    miter_circuit+="orgcir org({});\n".format(orgport_i+orgport_o[:-1])
    miter_circuit+="enccir enc({});\n".format(orgport_i+keyporti+encport_o[:-1])
    miter_circuit+=compare_o

    miter_circuit+="endmodule\n\n\n\n"

    miter_circuit+=verilogLL+"\n\n\n\n"

    miter_circuit+=re.sub(r"module .*\(","module orgcir(",verilog)


    gatemodules=open("./vlib/mycells.v").read()

    miter_circuit+=gatemodules


    miter_testbench=gen_miter_testbench(key_inputs_p=keyports[:-1],
                            cir_inputs_p=Uport_i[:-1],
                            top_port=orgport_i+keyporti[:-1],
                            outputlength=len(LLout)-1,
                            testbench_module="testbench",
                            top_module="top",
                            log_path="logfile.txt",
                            )

    miter_testbench=format_verilog(miter_testbench,remove_wire=False)
    return miter_circuit,miter_testbench

####################################################################################################################################
####################################################################################################################################


####################################################################################################################################
####################################################################################################################################
def text_to_pattern(text):
  text=re.sub(r"\\",r"\\\\",text)

  text=re.sub(r"\[",r"\[",text)
  text=re.sub(r"\]",r"\]",text)

  text=re.sub(r"\{",r"\{",text)
  text=re.sub(r"\}",r"\}",text)
  
  # text=re.sub("","",text)
  return text


####################################################################################################################################
####################################################################################################################################

def gen_busport(node,size:int):
    port=""
    if(type(node)==str):
        for i in range(size):
            port+=node+format(str(size-i-1),"")+", "
        port=port[:-2]
    return port

####################################################################################################################################
####################################################################################################################################


def get_diference(a,b):
    tmpa=list(set(a) - set(b))
    tmpb=list(set(b) - set(a))
    tmplist=[tmpa,tmpb]#list(set(tmpa)|set(tmpb))
    return tmplist

def get_diference_abs(a,b):
    tmpa=list(set(a) - set(b))
    tmpb=list(set(b) - set(a))
    tmplist=list(set(tmpa)|set(tmpb))
    return tmplist

####################################################################################################################################
####################################################################################################################################

def merge_lists(listset):
    tmplist=[]
    if(type(listset[0])==list):
        for i in listset:
            tmplist=list(set(tmplist)|set(i))
    return tmplist


####################################################################################################################################
####################################################################################################################################

def getnodeport(netlist, buskey):
    tmpval = re.findall(buskey+" (.*);", netlist)
    if (len(tmpval) != 1):
        raise Exception("CHECK "+buskey.upper()+" NODES")

    portnodes, busnodes,_ = io_port(tmpval[0].split(", "), mode=buskey)
    # print(io_port(tmpval[0].split(", ")))
    return portnodes, busnodes


####################################################################################################################################
####################################################################################################################################

def io_port(inputs, mode="input"):
    tmpdict = {}
    replace_=[]
    for i in inputs:
        # if(re.findall("(.*)_(\d+)_?",i)!=[]):
        #     i=re.sub("(.*)_(\d+)_?",r"\1"+"["+r"\2"+"]",i)
        if ("[" in i and "]" in i):
            tmpis = i.split("[")
            if tmpis[0] in tmpdict:
                tmpdict[tmpis[0]] += 1
            else:
                tmpdict[tmpis[0]] = 0
                # print(tmpis[0],tmpis[1][:-1])
        elif ("[" in i or "]" in i):
            print("ERROR INVALID SYNTAX")
        else:
            tmpdict[i] = 0

    inputnodes = ""
    portnodes = ""
    for i in tmpdict.keys():
        portnodes = portnodes+i+","
        if (tmpdict[i] != 0):
            #print("["+str(tmpdict[i])+":0] "+i)
            inputnodes = inputnodes+mode+" ["+str(tmpdict[i])+":0] "+i+"; "
            replace_.append(i)
        else:
            # replace_.remove(i)
            inputnodes = inputnodes+mode+" "+i+"; "

    # inputnodes=inputnodes[:]
    portnodes = portnodes[:-1]
    return portnodes, inputnodes,replace_

####################################################################################################################################
####################################################################################################################################


def sortio(tmp, reverse=True):
    tmpl = list(set([re.sub(r"\[[0-9]+\]", "", i) for i in tmp]))
    tmpl.sort(reverse=False)
    def x(inp): return (tmpl.index(
        re.sub(r"(\[[0-9]+\])", "", inp)), re.sub(r".*\[?([0-9]+)\]?.*", r"\1", inp))
    tmp.sort(key=x, reverse=reverse)

####################################################################################################################################
####################################################################################################################################

def HammingDistance(x: str, y: str) -> int:
    h = 0
    for i in range(len(x)):
        h += (x[i] != y[i])
    return h

####################################################################################################################################
####################################################################################################################################

def randKey(bits, seed=None):
    if(seed!=None):
        random.seed(seed)
    intkey = random.randint(0, (2**bits)-1)
    tmpkey = format(intkey, "0"+str(bits)+"b")
    return intkey, tmpkey



####################################################################################################################################
####################################################################################################################################

# "module {name} (inputs, keys, lock_output); parameter n={ic};input [n-1:0] inputs;input [n-1:0] keys;output lock_output;reg key = {ic}'d{key}; assign lock_output = (ckt_output ^ ((inputs == keys) & (inputs != key))); endmodule"

def gencc_SarLock(modulename, inputs,key):
    codestr="module {name} (inputs, keys, lock_output); parameter n={ic};input [n-1:0] inputs;input [n-1:0] keys;output lock_output;reg key = {ic}'d{key}; assign lock_output = (((inputs == keys) & (inputs != key))); endmodule"
    ic = len(inputs)
    portnodes, _,_ = io_port(inputs)
    
    comver = codestr.format(name=modulename,ic=ic,key=key)
    port=modulename+" {init} ("+"{portnodes},"+"{KEY}"+",{Q}); "

    return re.sub(";", ";\n", comver), portnodes,port



####################################################################################################################################
####################################################################################################################################


# "module antisat_{name} (A,B,Q);parameter keyval = {key},n={ic}; input [n-1:0] A; input [2n-1:0] B; output Q;always @ (A or B) begin  if (B == keyval) begin    Q = 1;  end else begin    Q = 0;end end endmodule"
# "module antisat_{name} (A,KEY,Q);parameter n={ic}; input [n-1:0] A; input [2n-1:0] B; output Q;always @ (A or B) begin  if (B == {keyval}) begin    Q = 1;  end else begin    Q = 0;end end endmodule"

# "module antisat_{name} (A,KEY,Q);parameter n={ic};input [n-1:0] A; input [2n-1:0] KEY; output Q; wire Q1,Q2; g_block g(A,KEY[n-1:0],Q1); g_block gc(A,KEY[2n-1:n],Q2); assign Q = Q1 & Q2;endmodule \nmodule g_block(X,KEY_X,Q);parameter n={ic};input [n-1:0]X;input [n-1:0]KEY_X;output reg Q;wire [n-1:0]X_xor;assign X_xor=X^KEY_X;integer k;always@(*)begin Q=1;for(k=0;k<n-1;k=k+1)begin if(X_xor[k]==0) Q=0;end end endmodule"

def gencc_AntiSAT(modulename, inputs):
    codestr="module {name} (A,KEY,Q);parameter n={ic};input [n-1:0] A; input [2*n-1:0] KEY; output Q; wire Q1,Q2; g_block g(A,KEY[n-1:0],Q1); g_block gc(A,KEY[2*n-1:n],Q2); assign Q = Q1 & (~Q2);endmodule \n\nmodule g_block(X,KEY_X,Q);parameter n={ic};input [n-1:0]X;input [n-1:0]KEY_X;output reg Q;wire [n-1:0]X_xor;assign X_xor=X^KEY_X;integer k;always@(*)begin Q=1;for(k=0;k<n-1;k=k+1)begin if(X_xor[k]==0) Q=0;end end endmodule"
    ic = len(inputs)
    portnodes, _,_ = io_port(inputs)
    
    comver = codestr.format(name=modulename,ic=ic)
    port=modulename+" {init} ("+"{portnodes},"+"{KEY}"+",{Q}); "

    return re.sub(";", ";\n", comver), portnodes,port


####################################################################################################################################
####################################################################################################################################

def gencc(modulename, inputs, key):
    ic = len(inputs)
    portnodes, inputnodes,_ = io_port(inputs)
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
    portnodes, inputnodes,_ = io_port(inputs)
    # print("HERE ",io_port(inputs))
    if (key == None):
        comver = "module "+modulename+"("+portnodes+",KEY,Q); " + inputnodes + "input ["+str(ic-1)+":0]KEY; wire ["+str(
            ic-1)+":0]A; assign A={"+portnodes+"}; output reg Q; integer Qr,count,i; always@(*)begin Qr=KEY^A;count=0; for(i=0;i<"+str(ic)+";i=i+1)begin if(Qr[i]) count=count+1;end if(count=="+str(h)+")Q=1;else Q=0; end endmodule"
        port=modulename+" {init} ("+portnodes+",{key},{Q}); "
    else:
        comver = "module "+modulename+"("+portnodes+",Q); " + inputnodes + " wire ["+str(ic-1)+":0]A; assign A={"+portnodes+"}; output reg Q; integer Qr,count,i; always@(*)begin Qr="+str(
            ic)+"'d"+str(key)+"^A;count=0; for(i=0;i<"+str(ic)+";i=i+1)begin if(Qr[i]) count=count+1;end if(count=="+str(h)+")Q=1;else Q=0; end endmodule"
        port=modulename+" {init} ("+portnodes+",{Q}); "
    return re.sub(";", ";\n", comver), portnodes,port




####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################


def format_verilog(verilog,remove_wire=False):
    verilog=re.sub("//.*\n","",verilog)
    verilog=re.sub("[/][].[*][/]","",verilog)
    verilog=re.sub("[(][].[*][)]\n","",verilog)

    if(remove_wire):
        verilog=re.sub("wire .*;\n","",verilog)

    verilog=re.sub("\n+","",verilog)
    verilog=re.sub(r"\s+"," ",verilog)
    verilog=re.sub(" ?; ?",";\n",verilog)
    verilog=re.sub("endmodule","endmodule\n",verilog)
    verilog=re.sub("end ","end\n",verilog)
    verilog=re.sub("begin","begin\n",verilog)

    assign_nodes=re.findall(r"assign (\\?.) = (\\?.) ?;\n",verilog)
    # for i in assign_nodes:
    #     if(i[0]=="N241_O"):
    #         print(i)

    verilog=re.sub(r"assign (\\?.) = (\\?.) ?;\n","",verilog) #BUF_g node\1_ ( .A(\2), .Y(\1) );\n

    # print(re.findall("N241_O",verilog))
    # print(re.findall("N241_I",verilog))
    tmpstr=""
    count=0
    for i in assign_nodes:
        if(re.findall(i[0],verilog)!=[]):
            if("1'h" in i[1]):
                print(i,re.findall(i[0],verilog))
                raise Exception("\n\n\n\t   GONNA HAVE TO FIX THIS NOW!!!!!!!!!! \n\n =====>>> Binary value on left Side of assign <<<=====")
            else:
                tmpstr+="BUF_g assignbuffer{} ( .A({}), .Y({}) );\n".format(count,i[1],i[0])
                count+=1

    verilog=re.sub("endmodule",tmpstr+"endmodule",verilog)
    return verilog

####################################################################################################################################
####################################################################################################################################
####################################################################################################################################


def format_bench(netlist):
#   netlist=re.sub("//.*\n","",netlist)
#   netlist=re.sub("[/][*].*[*][/]","",netlist)
#   netlist=re.sub("#.*\n","\n",netlist)
  netlist=re.sub("#.*\n","\n",netlist)
  netlist=re.sub("="," = ",netlist)
  netlist=re.sub("\n+","",netlist)
  netlist=re.sub("\s+"," ",netlist)
  netlist=re.sub(r"\)",")\n",netlist)

  return netlist


####################################################################################################################################
####################################################################################################################################

def extract_io_b(bench,mode="input"):
    tmp=re.findall(mode.upper()+r"\((.*)\)",bench)
    sortio(tmp)
    return tmp

####################################################################################################################################
####################################################################################################################################
def extract_gates_b(bench):
    tmp={i:[] for i in bench_gates}
    gate_count = {i: 0 for i in tmp}
    for i in bench_gates:
        if(i.lower() in bench):
            ix=i.lower()
        else:
            ix=i

        if i=='NOT' or i=='BUF' or i=='DFF':
            tmp[i]=re.findall(r" ?(.*) = "+ ix +r"\((.*)\)\n?",bench)

            i.lower()
        else:
            tmp[i]=re.findall(r" ?(.*) = "+ ix +r"\((.*), ?(.*)\)\n?",bench)
        
        gcount = len(tmp[i])
        if (gcount == 0):
            tmp.pop(i, None)
        else:
            gate_count[i] = gcount
    return tmp,gate_count

####################################################################################################################################
####################################################################################################################################


def dict_to_bin(output,printo=False,reverse=True):
    bin=""
    outkeys=list(output.keys())
    sortio(outkeys,reverse=reverse)
    if(printo):
        print(outkeys)
    for i in outkeys:
        val=output[i] if(type(output[i])==bool) else output[i].value()
        if(val==None):
            return -1
        bin+="1" if val else "0"
    return bin	

####################################################################################################################################
####################################################################################################################################

def bin_to_dict(vdict,bin):
	val=list(vdict.keys())
	tmp={}
	for i in range(len(val)):
		if(type(bin[i])==bool):
			tmp[val[i]]=bin[i]
		else:
			tmp[val[i]]=True if (bin[i]=='1') else False
	return tmp



####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################


# def extract_io_v(verilog,mode="input"):
#     tmp=re.findall(mode.lower()+" (.*);",verilog)
#     for i in tmp:
#         tmpi=i.split(",")
#         print(tmpi)


# def getio_v(verilog,mode="input"):
#   tmp=re.findall(mode.lower()+" (.*);",verilog)
#   tmp=tmp[0].split(",")
# #   print(tmp[0].split(","))
#   #if("," in i) 
#   port=""
#   nodes=[]
#   for ii in tmp:
#     i=ii.strip()
#     if(("[" in i) and ("]" in i)):
#       tmpi=re.findall("(.*)\[(.*):(.*)]",i)[0]
#       port+=tmpi[0]+","
#       for j in range(int(tmpi[2]),int(tmpi[1])+1):
#         # print(tmpi[0]+"["+str(j)+"]")
#         nodes.append(tmpi[0]+"["+str(j)+"]")
#     else:
#       port+=i+","
#       nodes.append(i)
# #   print(nodes)
#   return nodes,port



####################################################################################################################################
####################################################################################################################################


def extract_gates_va(verilog):
  tmp={}
  gate_count = {}
  tmp["BUF"]=re.findall("assign (.*) = (.*) ?;",verilog)
  tmp["NOT"]=re.findall("assign (.*) = ~(.*) ?;",verilog)
  tmp["AND"]=re.findall("assign (.*) = (.*) & (.*) ?;",verilog)
  tmp["OR"]=re.findall("assign (.*) = (.*) | (.*) ?;",verilog)
  tmp["XOR"]=re.findall("assign (.*) = (.*) ^ (.*) ?;",verilog)
  
  for i in tmp.keys():
    if(tmp[i]!=[]):    
        gate_count[i] = len(tmp[i])
  return tmp,gate_count


####################################################################################################################################
####################################################################################################################################


def extract_io_v(verilog,mode="input"):
  nodes=[]
  port=""
  tmp=re.findall(mode.lower()+" (.*);",verilog)
  for i in tmp:
    if("[" in i):
      ei,si,tmpi=re.findall(r"\[(\d+)\:(\d+)\] (.*)",i)[0]
      port+=tmpi+","
      for i in range(int(si),int(ei)+1):
        nodes.append(tmpi+"["+str(i)+"]")
    elif("," in i):
        tmpi=i.split(",")
        nodes=merge_lists((nodes,tmpi))
    else:
      nodes.append(i)
      port+=i+","
  return nodes,port

####################################################################################################################################
####################################################################################################################################

def extract_gates_v(verilog):
    tmp={}
    gate_count = {}
    #   tmp[re.sub("_g","",verilog_gates[0])]=re.findall(" "+verilog_gates[0] +" .* \( .A\((.*)\), .Y\((.*)\) \) ?;",verilog)
    #   gate_count[verilog_gates[0]] = len(tmp[re.sub("_g","",verilog_gates[0])])
    #   tmp[re.sub("_g","",verilog_gates[1])]=re.findall(" "+verilog_gates[1] +" .* \( .A\((.*)\), .Y\((.*)\) \) ?;",verilog)
    #   gate_count[verilog_gates[1]] = len(tmp[re.sub("_g","",verilog_gates[1])])

    for i in verilog_gates:
        if(i=="NOT_g" or i=="BUF_g"):
            tmpx=re.findall("\n ?"+i + r" .* \( .A\((.*)\), .Y\((.*)\) \) ?;",verilog)
        else:
            tmpx=re.findall(r"\n ?"+i +r" .* \( .A\((.*)\), .B\((.*)\), .Y\((.*)\) \) ?;",verilog)

        if(tmpx!=[]):    
            tmpi=re.sub("_g","",i)
            tmp[tmpi]=tmpx
            gate_count[i] = len(tmp[tmpi])
        
    return tmp,gate_count








####################################################################################################################################
####################################################################################################################################
##AST help functions

def extract_module_name(verilog):
    # Regular expression to match the module name
    module_pattern = re.compile(r"module\s+(\w+)")

    # Search for the module name in the Verilog code
    module_match = module_pattern.search(verilog)

    if module_match:
        module_name = module_match.group(1)
    return module_name

def synthesize_verilog(verilog, flag = "flatten"):
    text_file = open("./tmp/tmp_syn1.v", "w")
    n = text_file.write(verilog)
    text_file.close()
    if flag == "flatten":
        cmd = """
             ~/FYP/linux/yosys/build/yosys -q -p'
            read_verilog ./tmp/tmp_syn1.v
            hierarchy -check -top {}
            proc; opt; fsm; opt; memory; opt;
            techmap; opt
            dfflibmap -liberty ./vlib/mycells.lib
            abc -liberty ./vlib/mycells.lib  
            flatten
            clean
            write_verilog -noattr ./tmp/tmp_syn2.v
            '
        """
    elif flag == "don't flatten":
        cmd = """
             ~/FYP/linux/yosys/build/yosys -q -p'
            read_verilog ./tmp/tmp_syn1.v
            hierarchy -check -top {}
            proc; opt; fsm; opt; memory; opt;
            techmap; opt
            dfflibmap -liberty ./vlib/mycells.lib
            abc -liberty ./vlib/mycells.lib 
            clean
            write_verilog -noattr ./tmp/tmp_syn2.v
            '
        """
    else:
        Exception("Enter either 'flatten' or 'don't flatten' ")
    # Run the command and capture the output
    module_name = extract_module_name(verilog)
    subprocess.run(cmd.format(module_name), shell=True)
    text_file = open("./tmp/tmp_syn2.v", "r")
    synthesized_verilog = text_file.read()
    text_file.close()
    #os.remove("./tmp/tmp_syn1.v")
    #os.remove("./tmp/tmp_syn2.v")

    return synthesized_verilog

def synthesize_bench(bench):
    text_file = open("./tmp/tmp_syn1.bench", "w")
    text_file.write(bench)
    text_file.close()
    
    cmd = """
        ~/FYP/linux/yosys/build/yosys-abc'
        read_bench ./tmp/tmp_syn1.bench
        write_bench -l ./tmp/tmp_syn2.bench
        '
    """
    # Run the command and capture the output
    result = subprocess.run(cmd, shell=True, capture_output=True)
    text_file = open("./tmp/tmp_syn2.bench", "r")
    synthesized_verilog = text_file.read()
    text_file.close()
    #os.remove("./tmp/tmp_syn1.v")
    #os.remove("./tmp/tmp_syn2.v")

    return synthesized_verilog

def module_extraction (verilog):
        modules = re.findall(r'(module\s+(\w+)\s*\(.*?\)\s*;.*?endmodule)', verilog, re.DOTALL)
        module_dict = dict((module[1], module[0]) for module in modules)
        return module_dict      #module_dict = {'modulename' : "module code"}

def gates_extraction (verilog):
    pattern = r"(\w+)_g\s+(\w+)\s+\(\s*.*\((.*)\),\s*\.B\((.*)\),\s*\.Y\((.*)\)\s*\);"
    regex = re.compile(pattern)
    matches = regex.finditer(verilog)
    # Initialize an empty dictionary to store the gate information
    gates = {}

    # Iterate over the matches
    for match in matches:
        # Extract the gate type, input A, input B, and output from the match
        gate_type, gate_name, input_a, input_b, output = match.groups()
        
        # Add the gate information to the dictionary
        gates[gate_name] = {
            "type": gate_type,
            "inputs": [input_a, input_b],
            "output": output
        }

    return gates

def submodule_links_extraction(verilog):
    linkages = {}
    for match in re.finditer(r"(\w+)\s+(\w+)\s*\((.*?)\);", verilog):
        module_name = match.group(1)
        instance_name = match.group(2)
        inputs_str = match.group(3)
        input_list = re.findall(r"\.(\w+)\((.*?)\)", inputs_str)
        linkages[instance_name] =  {"module_name": module_name, "linkages": input_list}
    
    first_key = next(iter(linkages))
    linkages.pop(first_key)
    
    return linkages

def submodules_info(sub):
    dictionary = {}
    for ii in sub:
        module_name = ii
        module_code = sub[ii]
        inputs, input_ports = extract_io_v(module_code)
        outputs, output_ports = extract_io_v(module_code, "output")
        io = dict({'inputs':inputs,'outputs':outputs,'input_ports':input_ports,'output_ports':output_ports})
        gates = gates_extraction(module_code)
        linkages = submodule_links_extraction(module_code)
        number_of_submodules = len(linkages)-1
        dictionary[ii]  =  dict({"module_name": module_name, "io":io, "gates": gates, "linkages":linkages, "number_of_submodules":number_of_submodules})
    
    return dictionary





####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################


# def extract_io_v(netlist,mode="input"):
#   for i in re.findall(mode+" .*;\n",netlist):
#     if("[" in i):
#       tmpstr=""
#       tmp=re.findall(mode+" \[(\d+):(\d+)\] (.*);",i)[0]
#       for k in range(int(tmp[1]),int(tmp[0])+1):
#         tmpstr=tmpstr+mode.upper()+"("+tmp[2]+"["+str(k)+"]);"+"\n"
#     else:
#       tmp=i.split(" ")[-1][:-2]
#       tmpstr=mode.upper()+"("+tmp+");"
    
#     tmpi=re.sub("\[","\[",i)
#     tmpi=re.sub("\]","\]",tmpi)
#     netlist=re.sub(tmpi,tmpstr,netlist)
#   netlist=re.sub(r" \[",r"[",netlist)
#   return netlist


# def extract_gates_v(netlist):
    
#     tmp={re.sub("_g","",i):[] for i in verilog_gates}
#     gate_count = {i: 0 for i in tmp}
#     tmp[re.sub("_g","",verilog_gates[2])]=re.findall(r"("+ verilog_gates[2] +".* \( \.A\()(.*)(\), \.Y\()(.*)(\) \))",netlist)
#     gate_count[verilog_gates[2]] = len(re.sub("_g","",verilog_gates[2]))
    
#     tmp[re.sub("_g","",verilog_gates[1])]=re.findall(r"("+ verilog_gates[1] +".* \( \.A\()(.*)(\), \.Y\()(.*)(\) \))",netlist)
#     gate_count[verilog_gates[1]] += len(re.sub("_g","",verilog_gates[1]))
    
#     tmp[re.sub("_g","",verilog_gates[0])]=re.findall(r"("+ verilog_gates[0] +".* \( \.A\()(.*)(\), \.Y\()(.*)(\) \))",netlist)
#     gate_count[verilog_gates[1]] += len(re.sub("_g","",verilog_gates[1]))

#     for i in verilog_gates[3:]:
#         tmp[re.sub("_g","",i)]=re.findall(r"( "+ i +".* \( \.A\()(.*)(\), \.B\()(.*)(\), \.Y\()(.*)(\) \))",netlist)
#         gate_count[re.sub("_g","",i)] = len(tmp[re.sub("_g","",i)])   
  
    
#     return tmp,gate_count





#   netlist=re.sub("assign .* = .*;","",netlist) #replace with rmassign fn

# def archive_extract_gates_v(netlist):
#     netlist=re.sub("module.*;\n?","",netlist)
#     netlist=re.sub("input.*;\n?","",netlist)
#     netlist=re.sub("endmodule\n?","",netlist)
#     netlist=re.sub("assign.*;\n?","",netlist)
#     netlist=re.sub("DFF.*;\n?","",netlist)
    

    
#     netlist=re.sub(r"("+ verilog_gates[2] +".* \( \.A\()(.*)(\), \.Y\()(.*)(\) \))",r"\4 = NOT(\2)",netlist)
#     netlist=re.sub(r"("+ verilog_gates[1] +".* \( \.A\()(.*)(\), \.Y\()(.*)(\) \))",r"\4 = BUF(\2)",netlist)
#     netlist=re.sub(r"("+ verilog_gates[0] +".* \( \.A\()(.*)(\), \.Y\()(.*)(\) \))",r"\4 = BUF(\2)",netlist)

#     for i in verilog_gates[3:]:
#         netlist=re.sub(r"( "+ i +".* \( \.A\()(.*)(\), \.B\()(.*)(\), \.Y\()(.*)(\) \))",r"\6 = "+ re.sub(v_gates_ps,"",i).upper() +r"(\2,\4)",netlist)   
  
#     return netlist




# def extract_gates_v(netlist):
#     # tmp={i:[] for i in verilog_gates}
#     netlist=re.sub(r"("+ verilog_gates[2] +".* \( \.A\()(.*)(\), \.Y\()(.*)(\) \))",r"\4 = NOT(\2)",netlist)
#     netlist=re.sub(r"("+ verilog_gates[1] +".* \( \.A\()(.*)(\), \.Y\()(.*)(\) \))",r"\4 = BUF(\2)",netlist)
#     netlist=re.sub(r"("+ verilog_gates[0] +".* \( \.A\()(.*)(\), \.Y\()(.*)(\) \))",r"\4 = BUF(\2)",netlist)

#     for i in verilog_gates[3:]:
#         netlist=re.sub(r"( "+ i +".* \( \.A\()(.*)(\), \.B\()(.*)(\), \.Y\()(.*)(\) \))",r"\6 = "+ re.sub(v_gates_ps,"",i).upper() +r"(\2,\4)",netlist)   
  
#     return netlist



####################################################################################################################################
####################################################################################################################################
