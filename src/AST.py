from src.utils import *
from src.conv import *
import networkx as nx
import pickle
import base64
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
        self.module_LLverilog=None
        self.module_LLcircuitgraph=None
    
    def gen_graph(self):
        self.circuitgraph = nx.DiGraph()
        for logic_gate in self.gates:
            for node in self.gates[logic_gate]:
                tmpi=self.gates[logic_gate]
                init_name=node["init_name"]
                node_input=node["inputs"]
                node_output=node["outputs"]
                node_name=logic_gate+"#"+init_name

                self.circuitgraph.add_node(node_name, type="gate",logic=logic_gate)

                if(re.sub("\[\d+\]","",node_output) in self.io["outputs"]):
                    self.circuitgraph.add_node("output#"+node_output, type="output")
                    self.circuitgraph.add_edge(node_name, "output#"+node_output)
                elif(re.sub("\[\d+\]","",node_output) in self.io["wires"]):
                    self.circuitgraph.add_node("wire#"+node_output, type="wire")
                    self.circuitgraph.add_edge(node_name, "wire#"+node_output)
                else:
                    print(re.sub("\[\d+\]","",node_output),node_output)
                    raise Exception("NODE NOT FOUND")

                for i in node_input:
                    if(re.sub("\[\d+\]","",i) in self.io["inputs"]):
                        self.circuitgraph.add_node("input#"+i, type="input")
                        self.circuitgraph.add_edge("input#"+i,node_name)
                    elif(re.sub("\[\d+\]","",i) in self.io["wires"]):
                        self.circuitgraph.add_node("wire#"+i, type="wire")
                        self.circuitgraph.add_edge("wire#"+i,node_name)
                    else:
                        print(re.sub("\[\d+\]","",i),i)
                        raise Exception("NODE NOT FOUND")

        self.circuitgraph.add_node("module#"+self.module_name, type="module")
        for i in self.io["outputs"]:
            tmpi=self.io["outputs"][i]
            if(tmpi['bits']==1):
                self.circuitgraph.add_edge("output#"+i,"module#"+self.module_name)
            else:
                for k in range(tmpi['startbit'],tmpi["endbit"]+1):
                    # print("output#"+i+f"[{k}]")
                    self.circuitgraph.add_edge("output#"+i+f"[{k}]","module#"+self.module_name)

        for i in self.io["inputs"]:
            tmpi=self.io["inputs"][i]
            if(tmpi['bits']==1):
                self.circuitgraph.add_edge("module#"+self.module_name,"input#"+i)
            else:
                for k in range(tmpi['startbit'],tmpi["endbit"]+1):
                    self.circuitgraph.add_edge("module#"+self.module_name,"input#"+i+f"[{k}]")

    
        # Encode the graph object to a binary string using pickle and encode the binary string to a base64 string
        self.base64_data = base64.b64encode(pickle.dumps(self.circuitgraph)).decode('utf-8')

    def save_graph(self):
        nx.drawing.nx_agraph.write_dot(self.circuitgraph, "./tmp/tmp.dot")
        import subprocess
        subprocess.run("dot -Tsvg ./tmp/tmp.dot > ./tmp/tmp.svg", shell=True)



class AST:
    def __init__(self,file_path,top, rw = 'w', flag = 'v'):
        self.LLverilog = ""
        
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
            self.submodule = {}
            self.top_module_name=top
            self.gen_LLFile()
            self.writeLLFile()
        else:
            Exception("Enter either 'r' (for read) or 'w' (for write)")

    def gen_LLFile(self):
        self.synthesized_verilog = synthesize_verilog(self.verilog,top=self.top_module_name,flag="dont_flatten")
        self.synthesized_verilog_flatten = synthesize_verilog(self.verilog,top=self.top_module_name)
        self.flatten_bench = verilog_to_bench(self.synthesized_verilog_flatten)

        # print(self.top_module_name)

        self.submodules_techmap = module_extraction(self.synthesized_verilog) # dictionary {module name : module code}
        # print(self.submodules_techmap)
        self.top_module_verilog_techmap = self.submodules_techmap[self.top_module_name]
        del self.submodules_techmap[self.top_module_name]

        self.extracted_submodules = module_extraction(self.verilog)
        self.top_module_verilog = self.extracted_submodules[self.top_module_name]
        del self.extracted_submodules[self.top_module_name]
        self.no_of_submodules = len(self.extracted_submodules)

        self.top_module_info()
        self.sub_modules_data()
        self.update_LLverilog()

    
    def top_module_info(self):
        self.top_module.module_name = self.top_module_name
        self.top_module.org_code_verilog = self.top_module_verilog
        # self.top_module.org_code_bench = verilog_to_bench(self.top_module_verilog_techmap)
        self.top_module.gate_level_verilog = format_verilog(self.top_module_verilog_techmap)
        self.top_module.gates,self.top_module.linkages = gates_module_extraction(self.top_module.gate_level_verilog)
        inputs, input_ports = extract_io_v(self.top_module_verilog)
        outputs, output_ports = extract_io_v(self.top_module_verilog, "output")
        wire, _ = extract_io_v(self.top_module_verilog, "wire")    
        wire={key:wire[key]  for key in get_difference_abs(wire.keys(),inputs.keys(),outputs.keys())}
        self.top_module.io = dict({'wires':wire,'inputs':inputs,'outputs':outputs,'input_ports':input_ports,'output_ports':output_ports})
        self.top_module.gen_graph()
        

    def sub_modules_data(self):
        for key in self.extracted_submodules:
            self.submodule[key]=module()
            self.submodule[key].module_name = key
            self.submodule[key].org_code_verilog = self.extracted_submodules[key]
            # self.submodule[key].org_code_bench = verilog_to_bench(self.submodules_techmap[key])
            self.submodule[key].gate_level_verilog = self.submodules_techmap[key]
            self.submodule[key].gates,self.submodule[key].linkages = gates_module_extraction(self.submodule[key].gate_level_verilog)
            inputs, input_ports = extract_io_v(self.submodule[key].org_code_verilog)
            outputs, output_ports = extract_io_v(self.submodule[key].org_code_verilog, "output")
            wire, _ = extract_io_v(self.submodule[key].gate_level_verilog, "wire")    
            wire={key:wire[key]  for key in get_difference_abs(wire.keys(),inputs.keys(),outputs.keys())}
            self.submodule[key].io = dict({'wires':wire,'inputs':inputs,'outputs':outputs,'input_ports':input_ports,'output_ports':output_ports})
            self.submodule[key].gen_graph()
            

    def writeLLFile(self):
        ast_dict = dict({"orginal_code" : self.verilog, "gate_level_flattened" : self.synthesized_verilog_flatten,"Bench_format_flattened" : self.flatten_bench, "gate_level_not_flattened" : self.synthesized_verilog, "top_module_name" : self.top_module_name})
        top_dict = dict({"Verilog": self.top_module.org_code_verilog, "Synthesized_verilog" : self.top_module.gate_level_verilog, "Total_number_of_submodules":self.no_of_submodules, "io":self.top_module.io, "gates": self.top_module.gates, "Linkages" : self.top_module.linkages, "DiGraph":self.top_module.base64_data})

        sub_dict = {}
        for key in self.extracted_submodules:
            sub_dict[key] = dict({"Verilog": self.submodule[key].org_code_verilog, "Synthesized_verilog" : self.submodule[key].gate_level_verilog, "io":self.submodule[key].io, "gates": self.submodule[key].gates, "Linkages" : self.submodule[key].linkages,"DiGraph":self.submodule[key].base64_data})


        ast = dict({"AST":ast_dict, "top_module": top_dict, "submodules": sub_dict})

        json_file = json.dumps(ast, indent = 4)
        with open("./output_files/{}.json".format(self.top_module_name), "w") as verilog_ast:
            verilog_ast.write(json_file)

    
    
    
    
    def read_LLFile(self, file_path):
        with open(file_path) as json_file:
            verilog_ast = json.load(json_file)

        self.top_module = module()
        self.submodule = {}
        self.verilog =  verilog_ast["AST"]["orginal_code"]
        self.synthesized_verilog_flatten = verilog_ast["AST"]["gate_level_flattened"]
        self.synthesized_verilog = verilog_ast["AST"]["gate_level_not_flattened"]
        self.top_module_name  = verilog_ast["AST"]["top_module_name"]

        self.top_module.module_name = self.top_module_name
        self.top_module.org_code_verilog = verilog_ast["top_module"]["Verilog"]
        self.top_module.gate_level_verilog = verilog_ast["top_module"]["Synthesized_verilog"]
        # self.top_module.org_code_bench = verilog_ast["top_module"]["Bench_format"]
        self.no_of_submodules = verilog_ast["top_module"]["Total_number_of_submodules"]
        self.top_module.io = verilog_ast["top_module"]["io"]
        self.top_module.gates = verilog_ast["top_module"]["gates"]
        self.top_module.linkages = verilog_ast["top_module"]["Linkages"]
        #Decode the base64 string back to binary
        # Decode the binary string back to a graph object
        self.top_module.circuitgraph = pickle.loads(base64.b64decode(verilog_ast["top_module"]["DiGraph"].encode('utf-8')))

        keys = list((verilog_ast["submodules"]).keys())
        for i in keys:
            self.submodule[i]=module()
            self.submodule[i].module_name = i
            self.submodule[i].org_code_verilog = verilog_ast["submodules"][i]["Verilog"]
            self.submodule[i].gate_level_verilog = verilog_ast["submodules"][i]["Synthesized_verilog"]
            # self.submodule[i].org_code_bench = verilog_ast["submodules"][i]["Bench_format"]
            self.submodule[i].io = verilog_ast["submodules"][i]["io"]
            self.submodule[i].gates = verilog_ast["submodules"][i]["gates"]
            self.submodule[i].linkages = verilog_ast["submodules"][i]["Linkages"]
            #Decode the base64 string back to binary
            # Decode the binary string back to a graph object
            self.submodule[i].circuitgraph = pickle.loads(base64.b64decode(verilog_ast["submodules"][i]["DiGraph"].encode('utf-8'))) 
        self.update_LLverilog()
    
    def update_LLverilog(self):
        self.LLverilog+=self.top_module.gate_level_verilog+"\n"
        # self.circuitgraph
        for i in self.submodule:
            self.LLverilog+=self.submodule[i].gate_level_verilog+"\n"
            # self.circuitgraph

