import src.utils as utils
import src.verification as ver
from src.AST import AST
from src.PreSAT import PreSAT
import networkx as nx



# obj=AST(file_path="./input_files/Benchmarks/ISCAS85/c3540/c3540.v",rw="w",flag="v",top="c3540",filename="c3540org")
obj = AST(file_path="./output_files/c3540org.json",rw='r',filename="c3540locked") # r for read from file
# obj.save_module_connections()


LL=PreSAT(obj.top_module)


LL.set_key(50) # for TRLL, keycount<=Total No of original gates
# LL.RLL()
# LL.SLL()
LL.TRLL_plus()


# obj.top_module.save_graph()
obj.writeLLFile()

obj.gen_verification_files()






# tmp=utils.synthesize_verilog(obj.LLverilog+obj.gate_lib, top=obj.top_module_name,flag = "flatten")

# cmd = """
#              ~/FYP/linux/yosys/build/yosys -q -p'
#             read_verilog /home/alira/FYP_FINAL/tmpll.v
#             hierarchy -check -top {}
#             proc; opt; fsm; opt; memory; opt;
#             techmap; opt;
#             flatten
#             # dfflibmap -liberty ./vlib/mycells.lib
#             # abc -liberty ./vlib/mycells.lib  
#             opt_clean -purge
#             # flatten
#             write_verilog -noattr /home/alira/FYP_FINAL/tmpll.v
#             '
#         """
# import subprocess    
# subprocess.run(cmd.format(obj.top_module_name), shell=True)


# tmp=open("/home/alira/FYP_FINAL/tmpll.v").read()

# with open("/home/alira/FYP_FINAL/tmpll.v","w") as f:
#   f.write(tmp)


# path="/home/alira/FYP_FINAL/tmpll.v"
# top="top"

# utils.verify_verilog(path,obj.top_module_name)



# ~/FYP/linux/yosys/build/yosys -q -p'
# read_verilog /home/alira/FYP_FINAL/tmpll.v
# hierarchy -check -top locked
# '


