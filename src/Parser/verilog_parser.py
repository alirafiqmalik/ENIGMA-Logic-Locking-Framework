import re
import os
import src.utils as utils


#gates=['INVX1', 'AND2X1', 'OR2X1', 'NAND2X1', 'NOR2X1']
#gates=['not_g', 'and_g', 'or_g', 'nand_g', 'nor_g']
#gates=['NOT', 'AND', 'OR', 'NAND', 'NOR']
v_gates_ps="_g"
verilog_gates=['BUF_g','NOT_g', 'AND_g', 'OR_g', 'NAND_g', 'NOR_g','XOR_g','XNOR_g']




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
                nodes[k]=utils.connector(ei-si+1,si,ei)
                port+=k+","
        else:
            nodes[tmpi]=utils.connector(ei-si+1,si,ei)
            port+=tmpi+","
    elif("," in i):
        tmpi=i.split(",")
        for k in tmpi:
            nodes[k]=utils.connector(1,0,0)
            port+=k+","
    else:
      nodes[i]=utils.connector(1,0,0)
      port+=i+","

  return nodes,port

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



##AST help functions

def extract_module_name(verilog):
    # Regular expression to match the module name
    module_pattern = re.compile(r"module\s+(\w+)")

    # Search for the module name in the Verilog code
    module_match = module_pattern.search(verilog)

    if module_match:
        module_name = module_match.group(1)
    return module_name

def module_extraction (verilog):
        modules = re.findall(r'(module\s+(\w+)\s*\(.*?\)\s*;.*?endmodule)', utils.format_verilog_org(verilog), re.DOTALL)
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




# @utils.timer_func
def find_verilog_files_iter(parentdir,code="read_verilog {path}\n",checks=["tb",'backup','vrf']):
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

# @utils.timer_func
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


