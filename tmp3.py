import re
import src.utils as utils
import src.Parser.verilog_parser as verilog_parser



with open("input_files/ASSURE_LOCKED/modulefiles.v","r") as f:
  module_txt=f.read()


with open("tmp/tmpmod.v","w") as f:
  f.write(module_txt)


# with open("tmp.v","w") as f:
#   f.write(t)

gate_mapping,gates,FF=verilog_parser.extract_modules_def(module_txt)

path="input_files/ASSURE_LOCKED/design4/design4_netlist.v"
# "input_files/test.v"
# "input_files/ASSURE_LOCKED/design4/design4_netlist.v"


@utils.timer_func
def tmp1():
  file=open(path)
  verilog=file.read()
  return utils.format_verilog(verilog)


import mmap
@utils.timer_func
def tmp2():
  # Open the file in binary mode
  with open(path, "rb") as file:
      # Memory-map the file
      with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mapped_file:
          # Read the entire file
          verilog = mapped_file.read().decode()
  return utils.format_verilog(verilog)


# verilog=tmp1()
verilog=tmp2()
# with open("tmp/tmp.v","w") as f:
#   f.write(verilog)
# print(verilog)

print("HERE")



gate_tech,sub_module,(FF_tech,Clock_pins,Reset_pins)=verilog_parser.gates_module_extraction(verilog,gate_mapping,gates,FF)


print(gate_tech)