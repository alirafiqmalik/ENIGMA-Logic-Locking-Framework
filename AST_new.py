from src.utils import *
from src.conv import *
import json

class module:
    def __init__(self):
        self.org_code_verilog = None
        self.org_code_bench = None
        self.gate_level_verilog = None
        self.module_name = None
        self.code_locked = None
        self.gates = None
        self.io = None #dict({'inputs':None,'outputs':None,'input_ports':None,'output_ports':None})
        self.linkages = None #[ {"instant_name":None,"module_name":None,"links":{"out":"lock_out"}}]


class AST:
    def __init__(self, file_path, rw = 'w', flag = 'v'):
        if rw == 'r':
            self.read_LLFile(file_path)
        elif rw == 'w':
            if flag == 'v':
                self.verilog = open(file_path).read()
            elif flag == 'b':
                self.bench = open(file_path).read()
                self.verilog = verilog_to_bench(self.bench)
            else:
                Exception("Enter either 'v' (for verilog) or 'b' (for bench)")
            self.synthesized_verilog = None
            self.extracted_submodules = None
            self.top_module = module()
            self.submodule = []
            self.gen_LLFile()
            self.writeLLFile()
        else:
            Exception("Enter either 'r' (for read) or 'w' (for write)")

    def gen_LLFile(self):
        self.synthesized_verilog = synthesize_verilog(self.verilog,"don't flatten")
        self.synthesized_verilog_flatten = synthesize_verilog(self.verilog)
        self.top_module_name  = extract_module_name(self.synthesized_verilog_flatten)
        print(self.top_module_name)

        self.submodules_techmap = module_extraction(self.synthesized_verilog) # dictionary {module name : module code}
        self.top_module_verilog_techmap = self.submodules_techmap[self.top_module_name]
        del self.submodules_techmap[self.top_module_name]

        self.extracted_submodules = module_extraction(self.verilog)
        self.top_module_verilog = self.extracted_submodules[self.top_module_name]
        del self.extracted_submodules[self.top_module_name]
        self.no_of_submodules = len(self.extracted_submodules)

        self.top_module_info()
        self.sub_modules_data()

    def top_module_info(self):

        self.top_module.module_name = self.top_module_name
        self.top_module.org_code_verilog = self.top_module_verilog
        self.top_module.org_code_bench = verilog_to_bench(self.top_module.org_code_verilog)
        self.top_module.gate_level_verilog = self.top_module_verilog_techmap
        self.top_module.gates = gates_extraction(self.top_module.gate_level_verilog)
        self.top_module.linkages = submodule_links_extraction(self.top_module.org_code_verilog)

        inputs, input_ports = extract_io_v(self.top_module_verilog)
        outputs, output_ports = extract_io_v(self.top_module_verilog, "output")

        self.top_module.io = dict({'inputs':inputs,'outputs':outputs,'input_ports':input_ports,'output_ports':output_ports})

    def sub_modules_data(self):
        for i,key in enumerate(self.extracted_submodules):
            self.submodule.append(module())
            self.submodule[i].module_name = key
            self.submodule[i].org_code_verilog = self.extracted_submodules[key]
            self.submodule[i].org_code_bench = verilog_to_bench(self.submodule[i].org_code_verilog)
            self.submodule[i].gate_level_verilog = self.submodules_techmap[key]
            self.submodule[i].gates = gates_extraction(self.submodule[i].gate_level_verilog)
            self.submodule[i].linkages = submodule_links_extraction(self.submodule[i].org_code_verilog)

            inputs, input_ports = extract_io_v(self.submodule[i].org_code_verilog)
            outputs, output_ports = extract_io_v(self.submodule[i].org_code_verilog, "output")

            self.submodule[i].io = dict({'inputs':inputs,'outputs':outputs,'input_ports':input_ports,'output_ports':output_ports})
            

    def writeLLFile(self):
        ast_dict = dict({"orginal_code" : self.verilog, "gate_level_flattened" : self.synthesized_verilog_flatten, "gate_level_not_flattened" : self.synthesized_verilog, "top_module_name" : self.top_module_name})
        top_dict = dict({"Verilog": self.top_module.org_code_verilog, "Synthesized_verilog" : self.top_module.gate_level_verilog, "Bench_format" : self.top_module.org_code_bench, "Total_number_of_submodules":self.no_of_submodules, "io":self.top_module.io, "gates": self.top_module.gates, "Linkages" : self.top_module.linkages})

        sub_dict = {}
        for i,key in enumerate(self.extracted_submodules):
            sub_dict[key] = dict({"Verilog": self.submodule[i].org_code_verilog, "Synthesized_verilog" : self.submodule[i].gate_level_verilog, "Bench_format" : self.submodule[i].org_code_bench, "io":self.submodule[i].io, "gates": self.submodule[i].gates, "Linkages" : self.submodule[i].linkages})


        ast = dict({"AST":ast_dict, "top_module": top_dict, "submodules": sub_dict})

        json_file = json.dumps(ast, indent = 4)
        verilog_ast = open("./output_files/{}.json".format(self.top_module_name), "w")
        verilog_ast.write(json_file)
        verilog_ast.close()
        pass

    def read_LLFile(self, file_path):
        with open(file_path) as json_file:
            verilog_ast = json.load(json_file)

        self.top_module = module()
        self.submodule = []
        self.verilog =  verilog_ast["AST"]["orginal_code"]
        self.synthesized_verilog_flatten = verilog_ast["AST"]["gate_level_flattened"]
        self.synthesized_verilog = verilog_ast["AST"]["gate_level_not_flattened"]
        self.top_module_name  = verilog_ast["AST"]["top_module_name"]

        self.top_module.module_name = self.top_module_name
        self.top_module.org_code_verilog = verilog_ast["top_module"]["Verilog"]
        self.top_module.gate_level_verilog = verilog_ast["top_module"]["Synthesized_verilog"]
        self.top_module.org_code_bench = verilog_ast["top_module"]["Bench_format"]
        self.no_of_submodules = verilog_ast["top_module"]["Total_number_of_submodules"]
        self.top_module.io = verilog_ast["top_module"]["io"]
        self.top_module.gates = verilog_ast["top_module"]["gates"]
        self.top_module.linkages = verilog_ast["top_module"]["Linkages"]

        keys = list((verilog_ast["submodules"]).keys())
        for i in range(self.no_of_submodules):
            self.submodule.append(module())
            self.submodule[i].module_name = keys[i]
            self.submodule[i].org_code_verilog = verilog_ast["submodules"][keys[i]]["Verilog"]
            self.submodule[i].gate_level_verilog = verilog_ast["submodules"][keys[i]]["Synthesized_verilog"]
            self.submodule[i].org_code_bench = verilog_ast["submodules"][keys[i]]["Bench_format"]
            self.submodule[i].io = verilog_ast["submodules"][keys[i]]["io"]
            self.submodule[i].gates = verilog_ast["submodules"][keys[i]]["gates"]
            self.submodule[i].linkages = verilog_ast["submodules"][keys[i]]["Linkages"]





# obj=AST("./input_files/tmporg.v",rw="w",flag="v")

obj = AST("./output_files/locked.json",'r') # r for read from file

print(obj.top_module.module_name)
print(list(obj.top_module.linkages.keys())[0])
print(obj.top_module.io["inputs"])
print()
for i in obj.submodule:
    print(i.module_name,end=" ==>  ")
    # print(i.)
    print(i.linkages)