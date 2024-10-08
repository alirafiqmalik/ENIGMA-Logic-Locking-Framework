import re
import random
import os
import time 




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


@timer_func
def simple_read_verilog(path):
  file=open(path)
  verilog=file.read()
  return format_verilog(verilog)


import mmap
@timer_func
def nmap_read_verilog(path):
  # Open the file in binary mode
  with open(path, "rb") as file:
      # Memory-map the file
      with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mapped_file:
          # Read the entire file
          verilog = mapped_file.read().decode()
  return format_verilog(verilog)



####################################################################################################################################
####################################################################################################################################

def get_common_elements(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    common_elements = set1.intersection(set2)
    return list(common_elements)



def get_difference(a,b):
    tmpa=list(set(a) - set(b))
    tmpb=list(set(b) - set(a))
    tmplist=[tmpa,tmpb]#list(set(tmpa)|set(tmpb))
    return tmplist

from itertools import combinations
def get_differences(*args):
    result = {}
    for list1, list2 in combinations(args, 2):
        set_difference = set(list1) - set(list2)
        result[(list1, list2)] = list(set_difference)
    return result

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
            inputnodes = inputnodes+mode+" ["+str(tmpdict[i])+":0] "+i+";\n"
            replace_.append(i)
        else:
            # replace_.remove(i)
            inputnodes = inputnodes+mode+" "+i+";\n"

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
    verilog=re.sub(r"(\.\S+\() ?",r"\1",verilog)


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
            node=re.findall(f"wire(.*){L};",verilog)
            if(node==None):
                node=L
            else:
                node=[0]

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


####################################################################################################################################
####################################################################################################################################

def check_port(i):
    tmptxt=re.findall(r"\[",i)
    if(len(tmptxt)!=1):
        tmptxt=re.sub("(.*\[\d+\])\[\d+\]",r"\1",i)
    else:
        tmptxt=re.sub("\[\d+\]","",i)
    return tmptxt.strip()




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


def del_dir_files(parentdir):
    stack = [parentdir]
    dir=[]
    while stack:
        currentdir = stack.pop()
        for i in os.listdir(currentdir):
            if os.path.isfile(os.path.join(currentdir, i)):
                # print(os.path.join(os.path.abspath(currentdir),i))
                os.remove(os.path.join(os.path.abspath(currentdir),i))
            elif os.path.isdir(os.path.join(currentdir, i)):
                stack.append(os.path.join(currentdir, i))
                dir.append(os.path.join(currentdir, i))
    # print(dir)
    dir.reverse()
    if parentdir in dir:
        dir.remove(parentdir)
    for i in dir:
        os.removedirs(i)





def clean_dir(dir,clean_tmp=False):
    if(clean_tmp):
        files=[i for i in os.listdir(dir) if("tmp_" in i)]
    else:
        files=os.listdir(dir)

    for i in files:
        if(".svg" in i):
            continue
        path_i=os.path.join(os.path.abspath(dir),i)
        if(os.path.isfile(path_i)):
            os.remove(path_i)


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
            txt+=f"{mode} [{tmpi['endbit']}:{tmpi['startbit']}] {i};\n"

    if(return_bits):
        return txt,total_bits
    else:
        return txt
        

####################################################################################################################################
####################################################################################################################################

def det_logic(logic_gate,gate_mapping):
  for gate, gate_list in gate_mapping.items():
    if logic_gate in gate_list:
        return gate

####################################################################################################################################
####################################################################################################################################

def det_FF_node(mIO):
  if("clock" in mIO.lower() or "clk" in mIO.lower()):
    return "clock"
  elif(mIO=="R" or mIO.lower()=="rn" or mIO.lower()=="rst" or mIO.lower()=="clr" or mIO.lower()=="clear" or mIO.lower()=="reset"):
    return "reset"
  elif(mIO=="S" or mIO.lower()=="sn" or mIO.lower()=="pr" or mIO.lower()=="prn" or mIO.lower()=="preset" or mIO.lower()=="set"):
    return "preset"
  elif(mIO=="D"):
    return "inputs"
  elif(mIO=="Q"):
    return "outputs"


####################################################################################################################################
####################################################################################################################################

def FF_to_txt(FF_tech,FF):
  txt=""
  for FF_tech_i in FF_tech:
    port=FF[FF_tech_i]['port']
    for init_name in FF_tech[FF_tech_i]:
      tmp={}
      for mIO in FF[FF_tech_i]["port_list"]:
        tmp[mIO]=FF_tech[FF_tech_i][init_name][det_FF_node(mIO)]
      txt+= f"{FF_tech_i} {init_name} {port.format(**tmp)}\n"
  return txt

####################################################################################################################################
####################################################################################################################################
def gates_to_txt(gate_tech,gates_vlib):
    txt=""
    for logic in gate_tech:
        for logic_gate in gate_tech[logic]:
            NodeIO_def=gates_vlib[logic_gate]
            port=NodeIO_def['port']
            for init_name in gate_tech[logic][logic_gate]:
                I=gate_tech[logic][logic_gate][init_name]["inputs"]
                tmp={}
                tmp[NodeIO_def["outputs"][0]]=gate_tech[logic][logic_gate][init_name]["outputs"]
                for NodeI,mI in zip(NodeIO_def["inputs"],I):
                    tmp[NodeI]=mI
                txt+= f"{logic_gate} {init_name} {port.format(**tmp)}\n"
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
def save_graph(G,svg=False,dir_path="./tmp/",file_name="tmp"):
    dot_file_path=os.path.join(dir_path,file_name+".dot")
    import networkx as nx
    nx.drawing.nx_agraph.write_dot(G, dot_file_path)
    import subprocess
    if(svg):
        svg_file_name=os.path.join(dir_path,file_name+".svg")
        subprocess.run(f"dot -Tsvg {dot_file_path} > {svg_file_name}", shell=True)

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









####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################





