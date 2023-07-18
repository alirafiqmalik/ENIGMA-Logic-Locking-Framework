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

@utils.timer_func
def gates_module_extraction(verilog,gate_mapping,gates,FF):
  gate_tech={}
  FF_tech={}
  Clock_pins=[]
  Reset_pins=[]
  sub_module={}
  
  def process_chunk(chunk):
    type_block,init,extra=chunk

    if(type_block in gates):
      tmpx=re.findall(r'\.\S+\(([^\(\),]+)\)',extra)
      tmpx.reverse()
      
      logic=utils.det_logic(type_block,gate_mapping)
    
      if logic not in gate_tech:
          gate_tech[logic]={}
      
      if type_block not in gate_tech[logic]:
        gate_tech[logic][type_block]={}
      
      gate_tech[logic][type_block][logic+"_"+init]={"inputs": tmpx[1:] ,"outputs": tmpx[0]}
  
    elif(type_block in FF):

      tmpx=re.findall(r'\.\S+\(([^\(\),]+)\)',extra)

      if(type_block in FF):
        Presetpin=None
        Resetpin=None
        for mIO,NodeIO in zip(FF[type_block]["port_list"],tmpx):
          if("clock" in mIO.lower() or "clk" in mIO.lower()):
            Clockpin=NodeIO
          elif(mIO=="R" or mIO.lower()=="rn" or mIO.lower()=="rst" or mIO.lower()=="clr" or mIO.lower()=="clear" or mIO.lower()=="reset"):
            Resetpin=NodeIO
          elif(mIO=="S" or mIO.lower()=="sn" or mIO.lower()=="pr" or mIO.lower()=="prn" or mIO.lower()=="preset" or mIO.lower()=="set"):
            Presetpin=NodeIO
          elif(mIO=="D"):
            D_pin=NodeIO
          elif(mIO=="Q"):
            Q_pin=NodeIO

      
        if(Clockpin not in Clock_pins):
          Clock_pins.append(Clockpin)
        
        if(Resetpin not in Reset_pins):
          Reset_pins.append(Resetpin)
        
        if(Presetpin not in Reset_pins):
          Reset_pins.append(Presetpin)

        if type_block not in FF_tech:
            FF_tech[type_block]={}    
            
        FF_tech[type_block][init]={"inputs": D_pin ,"outputs": Q_pin,"clock":Clockpin,"reset":Resetpin,"preset":Presetpin}
  
    elif(type_block=="module"):
      return
    
    else:
      links=[]
      for i in extra.split(","):
          Li,Ri=re.findall("\.(.*)\((.*)\)",i)[0]
          links.append((Li,Ri,None))
      
      links=[re.findall("\.(.*)\((.*)\)",i)[0] for i in extra.split(",")]
    
      sub_module[init]={"module_name": type_block,"links":links,"port":extra} 
  
    # else:
    #   raise Exception(f"TypeBlock={type_block} NOT Defined")

  
  for i in re.findall(r"(\w+) (\w+) \((.*)\);",verilog):
    process_chunk(i)

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


