from src.utils import *
from src.conv import *
import json


class top_module:
    def __init__ (self, verilog, synthesized_verilog, top_module_name) -> None:
        self.top_module_name = top_module_name

        self.submodules_techmap = module_extraction(synthesized_verilog) # dictionary {module name : module code}
        
        self.top_module_verilog_techmap = self.submodules_techmap[top_module_name]
        del self.submodules_techmap[top_module_name]
        self.submodules_techmap_info = submodules_info(self.submodules_techmap)

        self.submodules = module_extraction(verilog)
        self.top_module_verilog = self.submodules[top_module_name]
        del self.submodules[top_module_name]
        self.submodules_info = submodules_info(self.submodules)

        inputs, input_ports = extract_io_v(self.top_module_verilog)
        outputs, output_ports = extract_io_v(self.top_module_verilog, "output")

        self.io = dict({'inputs':inputs,'outputs':outputs,'input_ports':input_ports,'output_ports':output_ports})
        self.gates = gates_extraction(self.top_module_verilog_techmap)
        self.submodule_linkages = submodule_links_extraction(self.top_module_verilog)


class AST(top_module):
    def __init__ (self,file_path,flag='v') -> None:
        if flag == 'v':
            self.org_code_verilog = open(file_path).read()
            self.org_code_bench = verilog_to_bench(self.org_code_verilog)
        elif flag == 'b':
            self.org_code_bench = open(file_path).read()
            self.org_code_verilog = verilog_to_bench(self.org_code_bench)

        self.gate_level_flattened = synthesize_verilog(self.org_code_verilog)
        self.gate_level_not_flattened = synthesize_verilog(self.org_code_verilog, "don't flatten")
        self.module_name = extract_module_name(self.gate_level_flattened)
        self.report = "report"
        super().__init__(self.org_code_verilog, self.gate_level_not_flattened, self.module_name)



obj = AST("input_files/tmporg.v",'v')
# print(obj.top_module_verilog)
ast_dict = dict({"orginal_code" : obj.org_code_verilog, "gate_level_flattened" : obj.gate_level_flattened, "gate_level_not_flattened" : obj.gate_level_not_flattened, "top_module_name" : obj.module_name})
top_dict = dict({"io":obj.io, "gates": obj.gates, "Linkages" : obj.submodule_linkages})
sub_dict = obj.submodules_techmap_info
ast = dict({"AST":ast_dict, "top_module": top_dict, "submodules": sub_dict})


# print(obj.submodule_linkages)

json_file = json.dumps(ast, indent = 4)

with open("output_files/ast.ll","w") as f:
    f.write(json_file)

# verilog_ast = open("output_files/ast.ll").read()

# print(verilog_ast)




# json.loads


# tmp=open("tmp/tmp_syn2.v").read()

# tmp=format_verilog(tmp,remove_wire=True)

# with open("tmp/tmp_syn2.v","w") as f:
#     f.write(tmp)