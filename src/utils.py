import re
import time
import random
import subprocess
from src.path_var import *



#gates=['INVX1', 'AND2X1', 'OR2X1', 'NAND2X1', 'NOR2X1']
#gates=['not_g', 'and_g', 'or_g', 'nand_g', 'nor_g']
#gates=['NOT', 'AND', 'OR', 'NAND', 'NOR']
v_gates_ps="_g"
verilog_gates=['BUF_g','NOT_g', 'AND_g', 'OR_g', 'NAND_g', 'NOR_g','XOR_g','XNOR_g']
bench_gates=['DFF','BUF','NOT', 'AND', 'OR', 'NAND', 'NOR','XOR','XNOR']
gate_to_assign={'BUF':'','NOT':'~', 'AND':'&', 'OR':'|','XOR':'^','NAND':'&', 'NOR':'|','XNOR':'^'}


####################################################################################################################################
####################################################################################################################################

def get_diference(a,b):
    tmpa=list(set(a) - set(b))
    tmpb=list(set(b) - set(a))
    tmplist=[tmpa,tmpb]#list(set(tmpa)|set(tmpb))
    return tmplist

####################################################################################################################################
####################################################################################################################################


def get_difference_abs(*args):
    a = args[0]
    others = args[1:]
    all_others = set().union(*others)
    return list(set(a) - all_others)

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
            inputnodes = inputnodes+mode+" ["+str(tmpdict[i])+":0] "+i+";"
            replace_.append(i)
        else:
            # replace_.remove(i)
            inputnodes = inputnodes+mode+" "+i+";"

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

def getnodeport(netlist, buskey):
    tmpval = re.findall(buskey+" (.*);", netlist)
    if (len(tmpval) != 1):
        raise Exception("CHECK "+buskey.upper()+" NODES")

    portnodes, busnodes,_ = io_port(tmpval[0].split(", "), mode=buskey)
    return portnodes, busnodes



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

def extract_value(encoded_value,bits=None):
    size, encoding_value = encoded_value.split("'")
    base = encoding_value[0]
    value=encoding_value[1:]
    if(bits==None):
        bits=int(size)


    if(len(value)==value.count("x")):
        val_bin="x"*bits
    elif('x' in value):
        raise ValueError(f"Mix of x and numbers in value = {value}")
    elif base == "h":
        val_bin = bin(int(value, 16))[2:]
    elif base == "d":
        val_bin = bin(int(value))[2:]
    elif base == "b":
        val_bin = value
    else:
        raise ValueError(f"Unknown encoding scheme: {base}")

    return val_bin.zfill(bits)

####################################################################################################################################
####################################################################################################################################


def proc_assign_bracket(node): #assign {,}={,.,} 
    node_n=[]
    for node_i in node:
        if(":" in node_i):
            tmpi,ei,si=re.findall(r"(.*)\[(\d+):(\d+)\]",node_i)[0]
            si,ei=int(si),int(ei)
            for k in range(si,ei+1):
                # print(f"{tmpi}[{k}]")
                node_n.append(f"{tmpi}[{k}]")
        elif("'h" in node_i):
            bit_val=extract_value(node_i)
            for k in range(len(bit_val)-1, -1, -1):
                node_n.append(f"1'b{bit_val[k]}")
        else:
            node_n.append(node_i)
    return node_n
            



####################################################################################################################################
####################################################################################################################################


def format_verilog_org(verilog):
    # verilog=re.sub("`","\\`",verilog)
    verilog=re.sub(r"//.*\n","",verilog)
    # verilog=re.sub(r"[/][].[*][/]","",verilog)
    # verilog=re.sub(r"[(][].[*][)]\n","",verilog)
    verilog=re.sub(r"/\*.*?\*/", "", verilog, flags=re.DOTALL)

    verilog=re.sub(r"\n+","",verilog)
    verilog=re.sub(r"\s+"," ",verilog)
    verilog=re.sub(r" ?; ?",";\n",verilog)

    verilog=re.sub(r"endmodule"," endmodule\n",verilog)
    verilog=re.sub(r"end ","end \n",verilog)
    verilog=re.sub(r"begin","begin \n",verilog)

    return verilog


####################################################################################################################################
####################################################################################################################################




def format_verilog(verilog):
    verilog=re.sub(r"//.*\n","",verilog)
    verilog=re.sub(r" +\)",")",verilog)
    verilog=re.sub(r"\( +","(",verilog)
    # verilog=re.sub(r"[/][].[*][/]","",verilog)
    # verilog=re.sub(r"[(][].[*][)]\n","",verilog)
    verilog=re.sub(r"/\*.*?\*/", "", verilog, flags=re.DOTALL)
    verilog=re.sub(r"(\w) (\[\d\])", r"\1\2", verilog)
    verilog=re.sub(r"\\","",verilog)

    verilog=re.sub(r"\n+","",verilog)
    verilog=re.sub(r"\s+"," ",verilog)
    verilog=re.sub(r" ?; ?",";\n",verilog)
    verilog=re.sub(r"endmodule","endmodule\n",verilog)
    verilog=re.sub(r"end ","end\n",verilog)
    verilog=re.sub(r"begin","begin\n",verilog)

    
    verilog=re.sub(r"(\w)\.",r"\1",verilog)
    verilog=re.sub(r"\] \[","][",verilog)

    t=re.findall(r"assign (\\?.*) = (\\?.*) ?;\n",verilog)
    verilog=re.sub(r"assign (\\?.*) = (\\?.*) ?;\n","",verilog)

    verilog_without_wire=re.sub("wire .*;\n","",verilog)

    verilog=re.sub(r" \[","[",verilog)
    verilog=re.sub(r"\[(\d+)\](\[\d+\])",r"_\1\2",verilog)

    verilog=re.sub(r"(wire|input|output)\[",r"\1 [",verilog)
    verilog=re.sub(r"(wire|input|output)( \[\d+:\d+\] .*)\[(\d+)\]",r"\1\2_\3",verilog)

    tmpbuf=""
    tmpassign=""
    for i in t:
        L,R=i
        if("{" in L):
            L=re.sub(" +","",L)[1:-1].split(",")
            R=re.sub(" +","",R)[1:-1].split(",")
            if(len(L)!=len(R)):
                L=proc_assign_bracket(L)
                R=proc_assign_bracket(R) 
            for Li,Ri in zip(L,R):
                if(re.findall(re.compile(Li),verilog_without_wire)!=[]):
                    tmp=Ri.split("'")[-1]
                    tmpbuf+=f"BUF_g assignbuf_{Li}_{tmp}_ ( .A({Ri}), .Y({Li}) );\n"
        else:
            if(re.findall(re.compile(L),verilog_without_wire)==[]):
                continue
            # tmpassign+=f"assign {L} = {R};\n"
            node=re.findall(f"wire(.*){L};",verilog)[0]

            if("[" in node):
                ct=extract_value(R)
                end,start=node.strip().split(":")
                end,start=int(end[1:]),int(start[:-1])
                # print(end,start)
                for k in range(start,end+1):
                    tmp=R.split("'")[-1]
                    tmpassign+=f"BUF_g assignbuf_{L}[{k}]_{tmp}_ ( .A(1'b{ct[k]}), .Y({L}[{k}]) );\n"
                    # print(f"BUF_g assignbuf_{L}[{k}]_{R}_ ( .A(1'b{ct[k]}), .Y({L}[{k}]) );\n")
            else:
                tmp=R.split("'")[-1]
                tmpassign+=f"BUF_g assignbuf_{L}_{tmp}_ ( .A({R}), .Y({L}) );\n"
                # print(f"BUF_g assignbuf_{L}_{R}_ ( .A({R}), .Y({L}) );\n")
            
            # print(node,re.findall(f"wire(.*){L};",verilog))
        #     if(node['bits']!=1):
        #         ct=utils.extract_value(i[1])
        #         ei,si=re.findall(f"wire \[(\d+):(\d+)\] {i[0]};",verilog)[0]
        #         si,ei=int(si),int(ei)
        #         # print(node['bits'],len(ct),ct,si,ei)
                # for k in range(si,ei+1):
                #     tmp+=f"BUF_g assignbuf_{i[0]}_{k}_{i[1]}_ ( .A(1'b{ct[k]}), .Y({i[0]}[{k}]) );\n"
                #     print(f"BUF_g assignbuf_{i[0]}_{k}_{i[1]}_ ( .A(1'b{ct[k]}), .Y({i[0]}[{k}]) );\n")
        # else:
        #     print(f"BUF_g assignbuf_{i[0]}_{i[1]}_ ( .A({i[1]}), .Y({i[0]}) );\n")

    verilog=re.sub("endmodule",tmpbuf+tmpassign+"endmodule",verilog)


    return verilog

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

def gen_busport(node,size:int):
    port=""
    if(type(node)==str):
        for i in range(size):
            port+=node+format(str(size-i-1),"")+", "
        port=port[:-2]
    return port
####################################################################################################################################
####################################################################################################################################

def extract_io_b(bench,mode="input"):
    tmp=re.findall(mode.upper()+r"\((.*)\)",bench)
    sortio(tmp)
    return tmp

####################################################################################################################################
####################################################################################################################################
def connector(bits,startbit,endbit) -> None:
    if bits==1:
        return {"bits":bits}
    else:
        return {"bits":bits,"startbit":startbit,"endbit":endbit}



def proc_port(x):
    tmp=x.split("[")    
    if(len(tmp)==3):
        # print(f"{tmp[0]}_{tmp[1][:-1]}[{tmp[2]}")
        return f"{tmp[0]}_{tmp[1][:-1]}[{tmp[2]}"
    elif(len(tmp)>2):
        raise Exception("More than 2d memory in output verilog")
    else:
        return x
    # if("[" in x):
    #     print(x)
    #     port,rbit=x.split("[")
    #     return f"{port}_{rbit}"
    return x


def proc_node_dec(x):
    if("[" in x):
        port,rbit=x.split("[")
        return f"{port}_{rbit[:-1]}"
    return x




def extract_io_v(verilog,mode="input"):
  nodes={}
  port=""
  tmp=re.findall("\n"+mode.lower()+r"[\s\[](.*);",verilog)

  for i in tmp:
    i=re.sub("\[(\d+)\]",r"_\1",i)
    if("[" in i):
        ei,si,tmpi=re.findall(r"\[(\d+):(\d+)\] ?(.*)",i)[0]
        ei,si=int(ei),int(si)
        # print(ei,si,tmpi)
        if("," in tmpi):
            tmpi=tmpi.split(",")
            for k in tmpi:
                nodes[k]=connector(ei-si+1,si,ei)
                port+=k+","
        else:
            nodes[tmpi]=connector(ei-si+1,si,ei)
            port+=tmpi+","
    elif("," in i):
        tmpi=i.split(",")
        for k in tmpi:
            nodes[k]=connector(1,0,0)
            port+=k+","
    else:
      nodes[i]=connector(1,0,0)
      port+=i+","

  return nodes,port

####################################################################################################################################
####################################################################################################################################

def check_port(i):
    tmptxt=re.findall(r"\[",i)
    if(len(tmptxt)!=1):
        tmptxt=re.sub("(.*\[\d+\])\[\d+\]",r"\1",i)
    else:
        tmptxt=re.sub("\[\d+\]","",i)
    return tmptxt
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
            tmpx=re.findall(r"\n ?"+i + r" .* \( .A\((.*)\), .Y\((.*)\) \) ?;",verilog)
        else:
            tmpx=re.findall(r"\n ?"+i +r" .* \( .A\((.*)\), .B\((.*)\), .Y\((.*)\) \) ?;",verilog)

        tmpi=re.sub("_g","",i)
        tmp[tmpi]=tmpx
        gate_count[i] = len(tmp[tmpi])
            
    return tmp,gate_count


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

def invert_gate(operator):
    operator_map = {
        'AND': 'NAND',
        'OR': 'NOR',
        'XOR': 'XNOR',
        'NAND': 'AND',
        'NOR': 'OR',
        'XNOR': 'XOR'
    }
    return operator_map.get(operator, operator)




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


def verify_verilog(path,top):
  cmd = """
     {yosys_path} -q -p'
      read_verilog {path}
      hierarchy -check -top {top}
      '
  """
  path=f"\"{path}\""
  result = subprocess.run(cmd.format(yosys_path=yosys_path,path=path,top=top), shell=True)
  if(result.returncode==1):
    print(result)
    raise Exception("Error code 1\nVerilog Code Syntax Error")
  elif(result.returncode==0):
    return True
    # print("Verilog Code Working Without Error")
  else:
    print(result)
    raise Exception(f"Unknown Error Code {result.returncode}")


import os
def synthesize_verilog(verilog, top,flag = "flatten"):
    with open("./tmp/tmp_syn1.v", "w") as f:
        f.write(verilog)
    file_name=f"{top}_2_{flag}.v"
    output_file_path=f"./tmp/{file_name}"
    output_file_path2=f"./tmp/{top}_unformated.v"
    readin="read_verilog ./tmp/tmp_syn1.v"
    
    if(os.path.isfile(output_file_path)):
        print(f"File Already Synthesize, Delete file in tmp to re-synthesize file {file_name}")
    else:
        if flag == "flatten":
            cmd = """
                {yosys_path} -q -p'
                {readin}
                hierarchy -check -top {module_name}
                proc; opt; fsm; opt; memory; opt;
                techmap; opt
                flatten
                opt_clean -purge
                dfflibmap -liberty ./vlib/mycells.lib
                abc -liberty ./vlib/mycells.lib  
                opt_clean -purge
                write_verilog -noattr {out_file}
                write_verilog -noattr {out_file2}
                '
            """
            
        elif flag == "dont_flatten":
            cmd = """
                {yosys_path} -q -p'
                {readin}
                hierarchy -check -top {module_name}
                proc; opt; fsm; opt; memory; opt;
                techmap; opt
                dfflibmap -liberty ./vlib/mycells.lib
                abc -liberty ./vlib/mycells.lib 
                opt_clean -purge
                write_verilog -noattr {out_file}
                write_verilog -noattr {out_file2}
                '
            """
        else:
            Exception("Enter either 'flatten' or 'don't flatten' ")
        # Run the command and capture the output
        
        
        result=subprocess.run(cmd.format(yosys_path=yosys_path,module_name=top,out_file=output_file_path,out_file2=output_file_path2,readin=readin), shell=True)

        if(result.returncode==1):
            raise Exception("Error code 1\nVerilog Code Syntax Error or yosys Path not found")
        elif(result.returncode==0):
            pass
            # print("Verilog Code Working Without Error")
        else:
            raise Exception(f"Unknown Error Code {result.returncode}")
        
    
    synthesized_verilog = open(output_file_path, "r").read()
    synthesized_verilog = format_verilog(synthesized_verilog)

    with open(output_file_path,"w") as f:
        f.write(synthesized_verilog)
    #os.remove("./tmp/tmp_syn1.v")
    #os.remove("./tmp/tmp_syn2.v")

    return synthesized_verilog












def synthesize_verilog_flatten_gate(verilog, top):
    filesintmp=os.listdir("./tmp")
    if("tmp_syn2.v" in filesintmp):
        print("File already exists, Returning Old File")
        return open("./tmp/tmp_syn2.v").read()
         
    with open("./tmp/tmp_syn2.v", "w") as f:
        f.write(verilog)
    file_name=f"{top}_outgatelevel_flatten.v"
    output_file_path=f"./tmp/{file_name}"
    output_file_path2=f"./tmp/{top}_unformated.v"
    readin="read_verilog ./tmp/tmp_syn2.v"
    
    cmd = """
        {yosys_path} -q -p'
        {readin}
        hierarchy -check -top {module_name}
        proc; opt; fsm; opt; memory; opt;
        techmap; opt
        flatten
        opt_clean -purge
        write_verilog -noattr {out_file}
        write_verilog -noattr {out_file2}
        '
    """
        
    result=subprocess.run(cmd.format(yosys_path=yosys_path,module_name=top,out_file=output_file_path,out_file2=output_file_path2,readin=readin), shell=True)

    if(result.returncode==1):
        raise Exception("Error code 1\nVerilog Code Syntax Error or yosys Path not found")
    elif(result.returncode==0):
        pass
        # print("Verilog Code Working Without Error")
    else:
        raise Exception(f"Unknown Error Code {result.returncode}")
    
    
    synthesized_verilog = open(output_file_path, "r").read()
    synthesized_verilog = format_verilog_org(synthesized_verilog)

    with open(output_file_path,"w") as f:
        f.write(synthesized_verilog)
    
    return synthesized_verilog




def clean_dir(dir):
    files=os.listdir(dir)
    for i in files:
        if(".svg" in i):
            continue
        path_i=os.path.join(os.path.abspath(dir),i)
        if(os.path.isfile(path_i)):
            os.remove(path_i)











# def synthesize_bench(bench):
#     text_file = open("./tmp/tmp_syn1.bench", "w")
#     text_file.write(bench)
#     text_file.close()
    
#     cmd = """
#         ~/FYP/linux/yosys/build/yosys-abc'
#         read_bench ./tmp/tmp_syn1.bench
#         write_bench -l ./tmp/tmp_syn2.bench
#         '
#     """
#     synthesized_verilog = open(f"./tmp/tmp_syn2.v", "r").read()
#     synthesized_verilog = format_verilog(synthesized_verilog)
#     with open(f"./tmp/tmp_syn2.v","w") as f:
#         f.write(synthesized_verilog)
#     #os.remove("./tmp/tmp_syn1.v")
#     #os.remove("./tmp/tmp_syn2.v")
#     return synthesized_verilog

def module_extraction (verilog):
        modules = re.findall(r'(module\s+(\w+)\s*\(.*?\)\s*;.*?endmodule)', format_verilog_org(verilog), re.DOTALL)
        module_dict = dict((module[1], module[0]) for module in modules)
        return module_dict      #module_dict = {'modulename' : "module code"}

def gates_module_extraction(verilog):
  gates=['BUF_g','NOT_g', 'AND_g', 'OR_g', 'NAND_g', 'NOR_g','XOR_g','XNOR_g']
  FF=['DFFcell',"DFFRcell","dffsr"]
  #   DFFRcell _2116_ ( .C(CLOCK_50), .D(_0153_), .Q(T3state[0]), .R(_0149_) );
  #   {'BUF':[],'NOT':[], 'AND':[], 'OR':[],'XOR':[],'NAND':[], 'NOR':[],'XNOR':[]}
  gate_tech={}
  FF_tech={}
  Clock_pins=[]
  Reset_pins=[]
  sub_module={}
  def process_chunk(chunk):
    type_block,init,extra=chunk
    # extra=re.sub(" \[","[",extra)
    # extra=re.sub("\[(\d+)\](\[\d+\])",r"_\1\2",extra)
    if(type_block in gates):
        tmpx=re.findall(r'\.\S+\(([^\(\),]+)\)',extra)
        tmpx.reverse()
        type_block_port=re.sub("_g","",type_block)
        if type_block_port not in gate_tech:
            gate_tech[type_block_port]={}
        gate_tech[type_block_port][type_block_port+init]={"inputs": tmpx[1:] ,"outputs": tmpx[0]}
        
    elif(type_block in FF):
        # print(type_block,init,extra)
        if(type_block=="DFFRcell"):
            type_block_port="DFF_"+init
            regex_pattern = r"\((.*?)\)"
            matches = re.findall(regex_pattern, extra)
            C,D,Q,R = [match for match in matches]
            if(C not in Clock_pins):
                Clock_pins.append(C)
            if(R not in Reset_pins):
                Reset_pins.append(R)
            
            if type_block not in FF_tech:
                FF_tech[type_block]={}
            
            FF_tech[type_block][type_block_port]={"inputs": D ,"outputs": Q,"clock":C,"reset":R}
            
            # print("HERE",C,D,Q,R)
            # print(re.findall(".C(CLOCK_50), .D(_0056_), .Q(T2x[0]), .R(_0040_)",extra))
        elif(type_block=="DFFcell"):
            type_block_port="DFF_"+init
            regex_pattern = r"\((.*?)\)"
            matches = re.findall(regex_pattern, extra)
            C,D,Q = [match for match in matches]
            if(C not in Clock_pins):
                Clock_pins.append(C)
            if type_block not in FF_tech:
                FF_tech[type_block]={}   
            FF_tech[type_block][type_block_port]={"inputs": D ,"outputs": Q,"clock":C}
            # print("HERE",C,D,Q,extra)
        elif(type_block=="dffsr"):
            type_block_port="DFF_"+init
            regex_pattern = r"\((.*?)\)"
            matches = re.findall(regex_pattern, extra)
            Clear,C,D,Preset,Q= [match for match in matches]
            # "inputs": D ,"outputs": Q,"clock":C,"clear":Clear,"preset":Preset
            # dffsr _123757_ (.CLEAR(1'h0), .CLK(clk_i), .D(_158363_Y), .PRESET(1'h0), .Q(_155393_A));s
            if(C not in Clock_pins):
                Clock_pins.append(C)
            if type_block not in FF_tech:
                FF_tech[type_block]={}   
            FF_tech[type_block][type_block_port]={"inputs": D ,"outputs": Q,"clock":C,"clear":Clear,"preset":Preset}
            # print("HERE",C,D,Q,extra)
        else:
            raise Exception("FLIP_FLOP NOT Defined")

    else:
        links=[]
        for i in extra.split(","):
            Li,Ri=re.findall("\.(.*)\((.*)\)",i)[0]
            links.append((Li,Ri,None))

        # links=[re.findall("\.(.*)\((.*)\)",i)[0] for i in extra.split(",")]
        sub_module[init]={"module_name": type_block,"links":links,"port":extra}

  for i in re.findall(r"(\w+) (\w+) \((.*)\);",verilog):
    # print("HERE1 ",i)
    process_chunk(i)


    #   and "1'" not in Clock_pins
  return gate_tech,sub_module,(FF_tech,Clock_pins,Reset_pins)






def submodules_info(sub):
    dictionary = {}
    for ii in sub:
        module_name = ii
        module_code = sub[ii]
        inputs, input_ports = extract_io_v(module_code)
        outputs, output_ports = extract_io_v(module_code, "output")
        io = dict({'inputs':inputs,'outputs':outputs,'input_ports':input_ports,'output_ports':output_ports})
        gates,linkages = gates_module_extraction(module_code)
        number_of_submodules = len(linkages)-1
        dictionary[ii]  =  dict({"module_name": module_name, "io":io, "gates": gates, "linkages":linkages, "number_of_submodules":number_of_submodules})
    
    return dictionary




####################################################################################################################################
####################################################################################################################################
def node_to_txt(iodict,mode="input",return_bits=False):
    txt=""
    total_bits=0
    for i in iodict:
        tmpi=iodict[i]
        if(tmpi["bits"]==1):
            total_bits+=1
            txt+=f"{mode} {i};\n"
        else:
            total_bits+=tmpi["bits"]
            # # print(i)
            # if("[" in i):
            #     port,rbit=i.split("[")
            #     txt+=f"{mode} [{tmpi['endbit']}:{tmpi['startbit']}] {port}_{rbit[:-1]};\n"
            # else:
            txt+=f"{mode} [{tmpi['endbit']}:{tmpi['startbit']}] {i};\n"

    if(return_bits):
        return txt,total_bits
    else:
        return txt
        

####################################################################################################################################
####################################################################################################################################
def FF_to_txt(FF):
    txt=""
    # DFFcell(C, D, Q)
    for i in FF:
        if(i=="DFFcell"):
            fn =lambda io,initname: f"{i} {initname}(.C({io['clock']}), .D({io['inputs']}), .Q({io['outputs']}));"
        elif(i=="DFFRcell"):
            fn=lambda io,initname: f"{i} {initname}(.C({io['clock']}), .D({io['inputs']}), .Q({io['outputs']}), .R({io['reset']}));"
        elif(i=="dffsr"):
            fn=lambda io,initname: f"{i} {initname}(.CLEAR({io['clear']}), .CLK({io['clock']}), .D({io['inputs']}), .PRESET({io['preset']}), .Q({io['outputs']}));"
            # "inputs": D ,"outputs": Q,"clock":C,"clear":Clear,"preset":Preset
            # dffsr _123757_ (.CLEAR(1'h0), .CLK(clk_i), .D(_158363_Y), .PRESET(1'h0), .Q(_155393_A));
        else:
            raise Exception("FF not defined")
        
        for jj in FF[i]:
            j=FF[i][jj]
            txt+=fn(j,jj)+"\n"
        # print(fn(j['inputs'],j['outputs']))
    return txt

####################################################################################################################################
####################################################################################################################################
def gates_to_txt(gates):
    txt=""
    for i in gates:
        # print(i)
        if(i=="NOT" or i=="BUF"):
            fn =lambda inputs,outputs,initname: f"{i}_g {initname}(.A({inputs[0]}), .Y({outputs}));"
        else:
            fn=lambda inputs,outputs,initname: f"{i}_g {initname}(.A({inputs[0]}), .B({inputs[1]}), .Y({outputs}));"     
        # print(gates[i])
        for jj in gates[i]:
            j=gates[i][jj]
            # print(jj,j)
            # print(j,gates[i][j])
            txt+=fn(j['inputs'],j['outputs'],jj)+"\n"
        # print(fn(j['inputs'],j['outputs']))
    return txt

####################################################################################################################################
####################################################################################################################################
def module_to_txt(linkages):
    txt=""
    for i in linkages:
        tmpi=linkages[i]
        # print(i,tmpi)
        port=""
        for L,R in zip(tmpi["L"],tmpi["R"]):
            if(":" in R):
                print("here   ",L,R)
            port+=f".{L}({R}), "
        txt+=f"{tmpi['module_name']} {i}({port[:-2]});\n"
            # print(f"{tmpi['module_name']} {i}({port[:-2]});")
    return txt




####################################################################################################################################
####################################################################################################################################
def save_graph(G,svg=False):
    import networkx as nx
    nx.drawing.nx_agraph.write_dot(G, "./tmp/tmp.dot")
    import subprocess
    if(svg):
        subprocess.run("dot -Tsvg ./tmp/tmp.dot > ./tmp/tmp.svg", shell=True)

# _0174_
####################################################################################################################################
####################################################################################################################################



def rand_selection(my_dict,val,req_bits):
    MAX_ITERATIONS=6000
    #req_bits: Set the desired sum of counts

    # Initialize the sum to zero
    sum_counts = 0
    # Initialize the list of selected keys to an empty list
    selected_keys = []
    # Loop until you find a combination of keys that satisfies the condition
    keys=list(my_dict.keys())

    MAX_keys_sample=None
    MAX_num_keys=0
    MIN_Diff_num_keys=999999999
    
    
    
    current_try=0
    while sum_counts != req_bits:
        # print("doing ", sum_counts)
        # Select `num_keys` keys at random
        num_keys=random.randint(1,len(keys)-1)
        selected_keys = random.sample(keys, num_keys)
        # Calculate the sum of counts for the selected keys
        
        sum_counts = sum(my_dict[key][val] for key in selected_keys)        
        # print("Doing ",current_try,req_bits, sum_counts)
        if(sum_counts==req_bits):
            print(f"Match found under max iterations at iteration {current_try}, {sum_counts} ")
            req_bits_i=req_bits
            break
        
        current_try+=1
        
        if(abs(sum_counts-req_bits)<MIN_Diff_num_keys):
            MIN_Diff_num_keys=abs(sum_counts-req_bits)
            MAX_keys_sample=selected_keys
            MAX_num_keys=sum_counts

        if(current_try>MAX_ITERATIONS):
            selected_keys=MAX_keys_sample
            print(f"Match not found under max iterations {MAX_ITERATIONS}")
            print(f"Using key sample with MIN DIFFERENCE {MIN_Diff_num_keys} with Count {MAX_num_keys}")
            req_bits_i=MAX_num_keys
            break

    
    return {i:my_dict[i] for i in my_dict if i in selected_keys},req_bits_i



####################################################################################################################################
####################################################################################################################################

def remove_key(thedict,thekey):
    if(type(thekey)!=list):
        thekey=[thekey]
    for i in thekey:
        if i in thedict: del thedict[i]

####################################################################################################################################
####################################################################################################################################





def timerit_func(func):
  def function_timer(*args, **kwargs):
    start = time.time()
    value = func(*args, **kwargs)
    end = time.time()
    runtime = end - start
    msg = "{func} took {time} seconds to complete its execution."
    print(msg.format(func = func.__name__,time = runtime))
    return value
  return function_timer



def timer_func(func):
  def function_timer(*args, **kwargs):
    start = time.time()
    value = func(*args, **kwargs)
    end = time.time()
    runtime = end - start
    msg = "{func} took {time} seconds to complete its execution."
    print(msg.format(func = func.__name__,time = runtime))
    return value
  return function_timer



checks=["tb",'backup','vrf']
def find_verilog_files_iter(parentdir,code="read_verilog {path}\n"):
  stack = [parentdir]
  tmp=""
  while stack:
      currentdir = stack.pop()
      for i in os.listdir(currentdir):
          if os.path.isfile(os.path.join(currentdir, i)):
              if i.split(".")[-1] != "v":
                  continue
              if(any(x in i for x in checks)):
                  continue
              # print("ITERATIVE", os.path.join(currentdir, i))
              tmp+=code.format(path=os.path.join(os.path.abspath(currentdir),i))
            #   tmp.append(os.path.join(parentdir,i))
          elif os.path.isdir(os.path.join(currentdir, i)):
              stack.append(os.path.join(currentdir, i))
  return tmp[:-1]

@timer_func
def find_verilog_files_recursive(tmp,parentdir):
  for i in os.listdir(parentdir):
    # print(i,i[-2:])
    if os.path.isfile(os.path.join(parentdir,i)):
      if i.split(".")[-1]!="v":
        continue
      # print("ITERATIVE", os.path.join(parentdir, i))
      tmp.append(os.path.join(parentdir,i))
    elif os.path.isdir(os.path.join(parentdir,i)):
      find_verilog_files_recursive(tmp,os.path.join(parentdir,i))
  return tmp






####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################





