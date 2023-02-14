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

def get_diference(a,b):
    tmpa=list(set(a) - set(b))
    tmpb=list(set(b) - set(a))
    tmplist=[tmpa,tmpb]#list(set(tmpa)|set(tmpb))
    return tmplist

####################################################################################################################################
####################################################################################################################################


# def get_diference_abs(a,b):
#     tmpa=list(set(a) - set(b))
#     tmpb=list(set(b) - set(a))
#     tmplist=list(set(tmpa)|set(tmpb))
#     return tmplist

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

def format_verilog_org(verilog):
    verilog=re.sub(r"//.*\n","",verilog)
    verilog=re.sub(r"[/][].[*][/]","",verilog)
    verilog=re.sub(r"[(][].[*][)]\n","",verilog)
    verilog=re.sub(r"/\*.*?\*/", "", verilog, flags=re.DOTALL)

    verilog=re.sub(r"\n+","",verilog)
    verilog=re.sub(r"\s+"," ",verilog)
    verilog=re.sub(r" ?; ?",";\n",verilog)
    verilog=re.sub(r"endmodule","endmodule\n",verilog)
    verilog=re.sub(r"end ","end\n",verilog)
    verilog=re.sub(r"begin","begin\n",verilog)
    return verilog



def format_verilog(verilog,remove_wire=False,remove_assign=False):
    verilog=re.sub(r"//.*\n","",verilog)
    verilog=re.sub(r"[/][].[*][/]","",verilog)
    verilog=re.sub(r"[(][].[*][)]\n","",verilog)
    verilog=re.sub(r"/\*.*?\*/", "", verilog, flags=re.DOTALL)

    verilog=re.sub(r"\n+","",verilog)
    verilog=re.sub(r"\s+"," ",verilog)
    verilog=re.sub(r" ?; ?",";\n",verilog)
    verilog=re.sub(r"endmodule","endmodule\n",verilog)
    verilog=re.sub(r"end ","end\n",verilog)
    verilog=re.sub(r"begin","begin\n",verilog)

    assign_nodes=re.findall(r"assign (\\?.*) = (\\?.*) ?;\n",verilog)

    verilog=re.sub(r"assign (\\?.*) = (\\?.*) ?;\n","",verilog) #BUF_g node\1_ ( .A(\2), .Y(\1) );\n

    verilog_withoutwire=re.sub(r"wire .*;\n","",verilog)
    if(remove_wire):
        verilog=re.sub(r"wire .*;\n","",verilog)
    
    tmpstr=""
    if(remove_assign):
        count=0
        for i in assign_nodes:
            if(re.findall(i[0],verilog_withoutwire)!=[]):
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
def connector(bits,startbit,endbit) -> None:
    if bits==1:
        return {"bits":bits}
    else:
        return {"bits":bits,"startbit":startbit,"endbit":endbit}


def extract_io_v(verilog,mode="input"):
  nodes={}
  port=""
  tmp=re.findall(mode.lower()+r"[\s\[](.*);",verilog)
  for i in tmp:
    if("[" in i):
        # print(i)
        ei,si,tmpi=re.findall(r"\[(\d+):(\d+)\] ?(.*)",i)[0]
        ei,si=int(ei),int(si)
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
##AST help functions

def extract_module_name(verilog):
    # Regular expression to match the module name
    module_pattern = re.compile(r"module\s+(\w+)")

    # Search for the module name in the Verilog code
    module_match = module_pattern.search(verilog)

    if module_match:
        module_name = module_match.group(1)
    return module_name

def synthesize_verilog(verilog, top,flag = "flatten"):
    with open("./tmp/tmp_syn1.v", "w") as f:
        f.write(verilog)

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
            opt_clean -purge
            write_verilog -noattr ./tmp/tmp_syn2flatten.v
            '
        """

        
    elif flag == "dont_flatten":
        cmd = """
             ~/FYP/linux/yosys/build/yosys -q -p'
            read_verilog ./tmp/tmp_syn1.v
            hierarchy -check -top {}
            proc; opt; fsm; opt; memory; opt;
            techmap; opt
            dfflibmap -liberty ./vlib/mycells.lib
            abc -liberty ./vlib/mycells.lib 
            opt_clean -purge
            write_verilog -noattr ./tmp/tmp_syn2dont_flatten.v
            '
        """
    else:
        Exception("Enter either 'flatten' or 'don't flatten' ")
    # Run the command and capture the output
    module_name = top
    subprocess.run(cmd.format(module_name), shell=True)
    synthesized_verilog = open(f"./tmp/tmp_syn2{flag}.v", "r").read()
    synthesized_verilog = format_verilog(synthesized_verilog,remove_wire=False,remove_assign=True)
    with open(f"./tmp/tmp_syn2{flag}.v","w") as f:
        f.write(synthesized_verilog)    
    #os.remove("./tmp/tmp_syn1.v")
    #os.remove("./tmp/tmp_syn2.v")

    return synthesized_verilog

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
#     synthesized_verilog = format_verilog(synthesized_verilog,remove_wire=False)
#     with open(f"./tmp/tmp_syn2.v","w") as f:
#         f.write(synthesized_verilog)
#     #os.remove("./tmp/tmp_syn1.v")
#     #os.remove("./tmp/tmp_syn2.v")
#     return synthesized_verilog

def module_extraction (verilog):
        modules = re.findall(r'(module\s+(\w+)\s*\(.*?\)\s*;.*?endmodule)', verilog, re.DOTALL)
        module_dict = dict((module[1], format_verilog_org(module[0])) for module in modules)
        return module_dict      #module_dict = {'modulename' : "module code"}

# def gates_extraction(verilog):
#     pattern = r"(\w+)_g\s+(\w+)\s+\(\s*.*\((.*)\),\s*\.B\((.*)\),\s*\.Y\((.*)\)\s*\);"
#     regex = re.compile(pattern)
#     matches = regex.finditer(verilog)
#     # Initialize an empty dictionary to store the gate information
#     gates = {}

#     # Iterate over the matches
#     for match in matches:
#         # Extract the gate type, input A, input B, and output from the match
#         gate_type, gate_name, input_a, input_b, output = match.groups()
        
#         # Add the gate information to the dictionary
#         gates[gate_name] = {
#             "type": gate_type,
#             "inputs": [input_a, input_b],
#             "outputs": output
#         }

#     return gates

# def submodule_links_extraction(verilog):
#     linkages = []
#     # (?!module)
#     for match in re.finditer(r"(\w+)\s+(\w+)\s*\((.*?)\);", verilog):
#         module_name = match.group(1)
#         instance_name = match.group(2)
#         inputs_str = match.group(3)
#         input_list = re.findall(r"\.(\w+)\((.*?)\)", inputs_str)
#         if(module_name=='module'):
#             pass
#         else:
#             print("THIS ",input_list)
#             linkages.append({"module_name": module_name, "init_name":instance_name,"links": input_list})
    
#     # print(linkages)
#     # first_key = next(iter(linkages))
#     # print(first_key)
#     # linkages.pop(first_key)

#     # print(linkages)
    
#     return linkages

def gates_module_extraction(verilog):
  gate_tech={}
#   {'BUF':[],'NOT':[], 'AND':[], 'OR':[],'XOR':[],'NAND':[], 'NOR':[],'XNOR':[]}
  sub_module=[]
  def process_chunk(chunk):
    type,init,extra=chunk
    if(type in ['BUF_g','NOT_g', 'AND_g', 'OR_g', 'NAND_g', 'NOR_g','XOR_g','XNOR_g']):
      tmpx=re.findall(r'\.\S+\(([^\(\),]+)\)',extra)
      tmpx.reverse()
      if re.sub("_g","",type) not in gate_tech:
        gate_tech[re.sub("_g","",type)]=[{"init_name": init,"inputs": tmpx[1:] ,"outputs": tmpx[0]}]
      else:
        gate_tech[re.sub("_g","",type)].append({"init_name": init,"inputs": tmpx[1:] ,"outputs": tmpx[0]})
    else:
      links=[re.findall("\.(.*)\((.*)\)",i)[0] for i in extra.split(",")]
    #   for i in extra.split(","):
    #     Lnode,Rnode=re.findall("\.(.*)\((.*)\)",i)[0]
    #     print(Lnode,Rnode)
        # nodel={}
        # noder={}

        # if(":" in Rnode):
        #   nodename,startbit,endbit=re.findall(r"(.*)\[(\d+):(\d+)\]",Rnode)[0]
        #   startbit=int(startbit)
        #   endbit=int(endbit)
        #   noder=connector(startbit-endbit+1,startbit,endbit)
        #   noder["node_name"]=nodename
        # else:
        #   noder=Rnode

        # if(":" in Lnode):
        #   nodename,startbit,endbit=re.findall(r"(.*)\[(\d+):(\d+)\]",Lnode)[0]
        #   startbit=int(startbit)
        #   endbit=int(endbit)
        #   nodel=connector(startbit-endbit+1,startbit,endbit)
        #   noder["node_name"]=nodename
        # else:
        #   nodel=Lnode
        # links.append((nodel,noder))
      sub_module.append({"module_name": type, "init_name": init, "links":links})

  for i in re.findall(r"(\w+) (\w+) \((.*)\);",verilog):
    process_chunk(i)

  return gate_tech,sub_module


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
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################
####################################################################################################################################

