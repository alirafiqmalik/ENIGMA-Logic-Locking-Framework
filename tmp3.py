import re


with open("input_files/ASSURE_LOCKED/modulefiles.v","r") as f:
  module_txt=f.read()

module_txt=re.sub(r"\n","",module_txt)
module_txt=re.sub(r"endmodule",r"endmodule\n",module_txt)

with open("tmp/tmpmod.v","w") as f:
  f.write(module_txt)

modules=re.findall("module.*endmodule",module_txt)

for i in modules:
  print(re.findall(r"module (.*)\(.",i))