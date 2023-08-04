import src.Attacks.SATAttack.SATAttack as satattack
from src.Parser.bench_parser import extract_io_b,extract_gates_b
import src.utils as utils
from src.Netlist.AST import AST

locked_filename="input_files/benchmark_bench/rnd/apex2_enc05.bench"
unlocked_filename="input_files/benchmark_bench/original/apex2.bench"



# top="fsm_0_obf"
# locked = AST(file_path=f"./output_files/{top}org.json",rw='r',filename=f"{top}locked_test") #Run to read in AST Format
# top="fsm"
# unlocked = AST(file_path=f"./output_files/{top}org.json",rw='r',filename=f"{top}locked_test") #Run to read in AST Format

# utils.clean_dir("./tmp")


top="apex2_enc05"
locked = AST(file_path=f"./output_files/{top}org.json",rw='r',filename=f"{top}locked_test") #Run to read in AST Format
top="apex2"
unlocked = AST(file_path=f"./output_files/{top}org.json",rw='r',filename=f"{top}locked_test") #Run to read in AST Format

# unlocked.write_Verilog_File(file="org")
# utils.clean_dir("./tmp",clean_tmp=True)
# locked.write_Verilog_File(file="org")

# print(locked.top_module.gates.keys())


print("START SAT ATTACK")
satobj=satattack.SatAttack(file_type="obj",locked_obj=locked.top_module,unlocked_obj=unlocked.top_module)
# satobj=satattack.SatAttack(file_type="b",locked_filename=locked_filename, unlocked_filename=unlocked_filename)
print(satobj.run())
print(satobj.iterations)


# netlist1=open(locked_filename).read()
# netlist2=open(unlocked_filename).read()
# tmp1=extract_gates_b(netlist1)
# # tmp2=extract_gates_b(netlist2)

# # t=utils.get_difference_abs(tmp1,tmp2)
# # t.sort(key=lambda x:int(x.split("keyinput")[-1]))
# # print(t)

# print(tmp1,tmp2)



# for logic,logic_gates in gates.items():
#   for logic_gate in logic_gates:
#     print(logic,logic_gate)

