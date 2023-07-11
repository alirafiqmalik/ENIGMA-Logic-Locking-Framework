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

# pathin="input_files/ASSURE_LOCKED/design1/design1_netlist.v"
# pathin="input_files/ASSURE_LOCKED/design1/oracle1_netlist.v"

# utils.clean_dir("./tmp")

# obj=AST(file_path=pathin,rw="w",flag="v",top=top,filename=f"{top}org",sub_modules="input_files/ASSURE_LOCKED/modulefiles.v")#Run to Read in Verilog Design



top="fsm_0_obf"
locked = AST(file_path=f"./output_files/{top}org.json",rw='r',filename=f"{top}locked_test") #Run to read in AST Format
top="fsm"
unlocked = AST(file_path=f"./output_files/{top}org.json",rw='r',filename=f"{top}locked_test") #Run to read in AST Format


diff=utils.get_diference(locked.top_module.io["outputs"],unlocked.top_module.io["outputs"])
com=utils.find_common_elements(locked.top_module.io["outputs"],unlocked.top_module.io["outputs"])

keys=[]
inpb=[]
inpa=list(unlocked.top_module.io["inputs"].keys())

for i in locked.top_module.io["inputs"]:
  if("locking" not in i):
    inpb.append(i)
  else:
    keys.append(i)


print(inpa)
print()
print(inpb)
print()
print()


print(list(unlocked.top_module.io["outputs"].keys()))
print(list(locked.top_module.io["outputs"].keys()))
