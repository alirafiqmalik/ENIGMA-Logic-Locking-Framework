import re
import src.utils as utils

@utils.timer_func
def extract_modules_def(gate_module_lib):
  Operations={
   "OR"  :{},
   "BUF" :{},
   "NOT" :{},
   "AND" :{},
   "XOR" :{},
   "NOR" :{},
   "NAND":{},
   "XNOR":{}
   }
  modules = re.findall(r"module\s+(\w+) ?\((.*?)\);(.*?)endmodule", gate_module_lib, re.DOTALL)
  
  
  for module in modules:
      module_name = module[0]
      port_list = [i.strip() for i in module[1].split(",")]
      tmp=re.sub(";",r"\n",module[2])
      module_inputs = []
      for i in re.findall(r"input\s+(.*)", tmp):
        for j in i.split(","):
          module_inputs.append(j.strip())
      module_outputs = re.findall(r"output(?:\s+reg)?\s+(.*)", tmp)
      assign_line = re.search(r"assign\s+(.*?)\;", module[2], re.DOTALL)
      always_block = re.search(r"always\s*@\s*\((.*?)\)\s*begin\s*(.*?)\s*end", module[2], re.DOTALL)

      port_io_map=""

      for i in port_list:
        if(i in module_inputs):
          port_io_map+="I"
        if(i in module_outputs):
          port_io_map+="O"

      # print("PORT MAP",port_io_map)

      if(2<len(port_list)>4):
        raise Exception("INVALID PORT Length")

      if(port_io_map!="IIIO" and len(port_list)==4):
        raise Exception("INVALID PORT LISTING")

      if(port_io_map!="IIO" and len(port_list)==3):
        raise Exception("INVALID PORT LISTING")
      
      if(port_io_map!="IO" and len(port_list)==2):
        raise Exception("INVALID PORT LISTING")    
        


      if(always_block==None and assign_line!=None):
        port="\("
        for i in port_list[:-1]:
          port+=f".{i}\((.*)\), "
        port+=f".{port_list[-1]}\((.*)\)"+" ?;"
      elif(always_block!=None and assign_line==None):
        pass
      else:
        raise Exception("Gate Definition Not Supported")
      # elif(always_block!=None and assign_line!=None):
      #   pass
      # elif(always_block==None and assign_line==None):
      #   pass
      


      tmp=dict({
          "port_list":port_list,
          "port":port,
          "inputs": [input_.strip() for input_ in module_inputs],
          "outputs": module_outputs,
          "assign_line": assign_line.group(1).strip() if assign_line else None,
          "always_block":{
                          "sensitivity_list": always_block.group(1).strip() if always_block else None,
                          "lines": always_block.group(2).strip() if always_block else None
                          } if always_block else None
      })

      if("BUF" in module_name):
        Operations["BUF"][module_name]=tmp
      elif("NOT" in module_name or "INV" in module_name):
        Operations["NOT"][module_name]=tmp
      elif("NAND" in module_name):
        Operations["NAND"][module_name]=tmp
      elif("XNOR" in module_name):
        Operations["XNOR"][module_name]=tmp
      elif("NOR" in module_name):
        Operations["NOR"][module_name]=tmp
      elif("AND" in module_name):
        Operations["AND"][module_name]=tmp
      elif("XOR" in module_name):
        Operations["XOR"][module_name]=tmp
      elif("OR" in module_name):
        Operations["OR"][module_name]=tmp    
      elif("FF" in module_name):
        pass
      else:
        raise Exception(f"LOGIC NOT IDENTIFIED = {module_name}")
  
  return Operations


with open("input_files/ASSURE_LOCKED/modulefiles.v","r") as f:
  module_txt=f.read()

module_txt=re.sub(r"\n","",module_txt)
module_txt=re.sub(r"endmodule",r"endmodule\n",module_txt)

with open("tmp/tmpmod.v","w") as f:
  f.write(module_txt)


verilog=utils.format_verilog(open("input_files/ASSURE_LOCKED/design1/design1_netlist.v").read())

# with open("tmp.v","w") as f:
#   f.write(t)

Operations=extract_modules_def(module_txt)



# for i in Operations:
#   print(i,list(Operations[i].keys()))

tmp={}
gate_count = {}
for i in Operations:
    if(i=="NOT" or i=="BUF"):
      for j in Operations[i]:
        tmpx=re.findall(r"\n ?"+j + r" .* "+Operations[i][j]["port"],verilog)
    else:
      for j in Operations[i]:
        tmpx=re.findall(r"\n ?"+j + r" .* "+Operations[i][j]["port"],verilog)

    tmp[i]=tmpx
    gate_count[i] = len(tmp[i])

# print(tmp["NAND"])

