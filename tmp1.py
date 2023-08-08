from src.Locking.LL import LogicLocking
import src.utils as utils
from src.Netlist.AST import AST
import time 
# start_time = time.time()
# elapsed_time = time.time() - start_time

# """
# ~/FYP/linux/yosys/build/yosys -p'
# read_verilog input_files/ASSURE_LOCKED/design4/design4_netlist.v input_files/ASSURE_LOCKED/modulefiles.v
# hierarchy -check -top tate_pairing_0_obf
# proc; opt; fsm; opt; memory; opt;
# techmap; opt
# write_verilog -noattr tmp/tmpvbefore.v
# flatten;
# dfflibmap -liberty ./vlib/mycells.lib
# abc -liberty ./vlib/mycells.lib 
# opt_clean -purge
# write_verilog -noattr tmp/tmpv1.v
# '
# """





# top="fsm_0_obf"
# pathin="input_files/ASSURE_LOCKED/design1/design1_netlist.v"

# top="fsm"
# pathin="input_files/ASSURE_LOCKED/design1/oracle1_netlist.v"

utils.clean_dir("./tmp")

# path="/home/alira/FYP_FINAL/tmptest.v"
# top="test_adder"

# obj=AST(file_path=path,rw="w",flag="v",top=top,filename=f"{top}org",synth=False)#Run to Read in Verilog Design

import re
import os
files=[([f"input_files/ASSURE_LOCKED/{i}/{k}" for k in os.listdir("input_files/ASSURE_LOCKED/"+i) if(".v" in k and "design" in k)][0],[f"input_files/ASSURE_LOCKED/{i}/{j}" for j in os.listdir("input_files/ASSURE_LOCKED/"+i) if(".v" in j and "oracle" in j)][0]) for i in os.listdir("input_files/ASSURE_LOCKED") if("design" in i)]
files.sort()
notdone=[]


for i in files:
  design=i[0]
  oracle=i[1]
  

  tmp=open(design).read()
  top_design = re.findall(r'(module\s+(\w+)\s*\(.*?\)\s*;.*?endmodule)', utils.format_verilog_org(tmp), re.DOTALL)[0][1]
  tmp=open(oracle).read()
  top_oracle = re.findall(r'(module\s+(\w+)\s*\(.*?\)\s*;.*?endmodule)', utils.format_verilog_org(tmp), re.DOTALL)[0][1]
  print(top_oracle,top_design)
  # try:
  print("DOING ",top_oracle)
  obj=AST(file_path=oracle,rw="w",flag="v",top=top_oracle,filename=f"{top_oracle}org",vlibpath="input_files/ASSURE_LOCKED/modulefiles.v",synth=False)#Run to Read in Verilog Design
  # except:
  #   print("FAILED ",top_oracle)
  #   notdone.append(oracle)
  # try:
  print("DOING ",top_design)
  obj=AST(file_path=design,rw="w",flag="v",top=top_design,filename=f"{top_design}org",vlibpath="input_files/ASSURE_LOCKED/modulefiles.v",synth=False,locked=True)#Run to Read in Verilog Design
  # except:
  #   print("FAILED ",top_design)
  #   notdone.append(design)
  # break


# locked_filename="input_files/benchmark_bench/rnd/apex2_enc05.bench"
# unlocked_filename="input_files/benchmark_bench/original/apex2.bench"

# top="apex2_enc05"
# obj=AST(file_path=locked_filename,rw="w",flag="b",top=top,filename=f"{top}org",vlibpath="input_files/ASSURE_LOCKED/modulefiles.v",synth=False,locked=True)#Run to Read in Verilog Design
# top="apex2"
# obj=AST(file_path=unlocked_filename,rw="w",flag="b",top=top,filename=f"{top}org",vlibpath="input_files/ASSURE_LOCKED/modulefiles.v",synth=False)#Run to Read in Verilog Design

# top="fsm_0_obf"
# obj=AST(file_path="input_files/ASSURE_LOCKED/design1/design1_netlist.v",rw="w",flag="v",top=top,filename=f"{top}org",vlibpath="input_files/ASSURE_LOCKED/modulefiles.v",synth=False)#Run to Read in Verilog Design

# top="fsm_0_obf"
# locked = AST(file_path=f"./output_files/{top}org.json",rw='r',filename=f"{top}locked_test") #Run to read in AST Format
# top="fsm"
# unlocked = AST(file_path=f"./output_files/{top}org.json",rw='r',filename=f"{top}locked_test") #Run to read in AST Format


# outn=locked.top_module.io["outputs"]

# import sys

# #1000
# print(sys.getrecursionlimit())

# # set recursion limit to 2000
# sys.setrecursionlimit(200000)


# done=[]
# keys=[]
# def return_pred(circuitgraph,node):
#   global done
#   global keys
#   if("module#" in node):
#     return
  
#   if(node in done):
#       return
#   else:
#       done.append(node)
#   pred=list(circuitgraph.predecessors(node))
#   if(pred==[]):
#     return

#   # print(pred)
#   for i in pred:
#     if("locking" in i):
#        keys.append(i)
#     return_pred(circuitgraph,i)
    

# locked.top_module.gen_org_verilog()
# print(locked.top_module.gate_level_verilog)


# for i in outn:
#   return_pred(locked.top_module.circuitgraph,i)
#   print(len(keys))
#   # break


# diff=utils.get_diference(locked.top_module.io["outputs"],unlocked.top_module.io["outputs"])
# com=utils.find_common_elements(locked.top_module.io["outputs"],unlocked.top_module.io["outputs"])

# keys=[]
# inpb=[]
# inpa=list(unlocked.top_module.io["inputs"].keys())

# for i in locked.top_module.io["inputs"]:
#   if("locking" not in i):
#     inpb.append(i)
#   else:
#     keys.append(i)


# print(inpa)
# print()
# print(inpb)
# print()
# print()


# print(list(unlocked.top_module.io["outputs"].keys()))
# print(list(locked.top_module.io["outputs"].keys()))
