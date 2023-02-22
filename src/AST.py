from src.utils import *
from src.conv import *
from src.verification import *
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
        self.gates = None
        self.io = None
        self.linkages = None
        self.circuitgraph=None
        self.module_LLverilog=""
        self.lockingdata={"wires":[],"gates":[],"inputs":[]}
        self.bitkey=""
        # self.module_LLverilog=None
        # self.module_LLcircuitgraph=None
    
    def gen_graph(self):
        self.circuitgraph = nx.DiGraph()
        for logic_gate in self.gates:
            for init_name in self.gates[logic_gate]:
                node=self.gates[logic_gate][init_name]
                tmpi=self.gates[logic_gate]
                # init_name=node["init_name"]
                node_input=node["inputs"]
                node_output=node["outputs"]
                node_name=init_name

                self.circuitgraph.add_node(node_name, type="gate",logic=logic_gate)
                

                if(re.sub("\[\d+\]","",node_output) in self.io["outputs"]):
                    self.circuitgraph.add_node(node_output, type="output")
                    self.circuitgraph.add_edge(node_name, node_output)
                elif(re.sub("\[\d+\]","",node_output) in self.io["wires"]):
                    self.circuitgraph.add_node(node_output, type="wire")
                    self.circuitgraph.add_edge(node_name, node_output)
                else:
                    print(self.module_name)
                    print(re.sub("\[\d+\]","",node_output),node_output)
                    raise Exception("NODE NOT FOUND")

                for i in node_input:
                    tmptxt=re.sub("\[\d+\]","",i)
                    if(tmptxt in self.io["inputs"]):
                        self.circuitgraph.add_node(i, type="input",port=tmptxt)
                        self.circuitgraph.add_edge(i,node_name)
                    elif(tmptxt in self.io["outputs"]):
                        self.circuitgraph.add_node(i, type="output",port=tmptxt)
                        self.circuitgraph.add_edge(node_name,i)
                    elif(tmptxt in self.io["wires"]):
                        self.circuitgraph.add_node(i, type="wire",port=tmptxt)
                        self.circuitgraph.add_edge(i,node_name)
                    else:
                        print(self.module_name)
                        print(tmptxt,i)
                        raise Exception("NODE NOT FOUND")

        self.circuitgraph.add_node("module#"+self.module_name, type="module")
        for i in self.io["outputs"]:
            tmpi=self.io["outputs"][i]
            if(tmpi['bits']==1):
                self.circuitgraph.add_edge(i,"module#"+self.module_name)
            else:
                for k in range(tmpi['startbit'],tmpi["endbit"]+1):
                    self.circuitgraph.add_edge(i+f"[{k}]","module#"+self.module_name)

        for i in self.io["inputs"]:
            tmpi=self.io["inputs"][i]
            if(tmpi['bits']==1):
                self.circuitgraph.add_edge("module#"+self.module_name,i)
            else:
                for k in range(tmpi['startbit'],tmpi["endbit"]+1):
                    self.circuitgraph.add_edge("module#"+self.module_name,i+f"[{k}]")

    
    def bin_graph(self):
        # Encode the graph object to a binary string using pickle and encode the binary string to a base64 string
        self.base64_data = base64.b64encode(pickle.dumps(self.circuitgraph)).decode('utf-8')

    def save_graph(self):
        save_graph(self.circuitgraph)
    
    
    def node_to_txt(self,mode="input"):
        txt=""
        iodict=self.io[mode+"s"]
        for i in iodict:
            tmpi=iodict[i]
            if(tmpi["bits"]==1):
                txt+=f"{mode} {i};\n"
            else:
                txt+=f"{mode} [{tmpi['endbit']}:{tmpi['startbit']}] {i};\n"
        return txt

    def gates_to_txt(self):
        txt=""
        for i in self.gates:
            # print(i)
            if(i=="NOT" or i=="BUF"):
                fn =lambda inputs,outputs,initname: f"{i}_g {initname}(.A({inputs[0]}), .Y({outputs}));"
            else:
                fn=lambda inputs,outputs,initname: f"{i}_g {initname}(.A({inputs[0]}), .B({inputs[1]}), .Y({outputs}));"
            
            # print(self.gates[i])
            for jj in self.gates[i]:
                j=self.gates[i][jj]
                # print(jj,j)
                # print(j,self.gates[i][j])
                txt+=fn(j['inputs'],j['outputs'],jj)+"\n";
            # print(fn(j['inputs'],j['outputs']))
        return txt


    def module_to_txt(self):
        txt=""
        for i in self.linkages:
            tmpi=self.linkages[i]
            # print(i,tmpi)
            port=""
            for L,R in zip(tmpi["L"],tmpi["R"]):
                port+=f".{L}({R}), "
            txt+=f"{tmpi['module_name']} {i}({port[:-2]});\n"
                # print(f"{tmpi['module_name']} {i}({port[:-2]});")
        return txt

    
    
    def gen_LL_verilog(self):
        self.module_LLverilog=f"module {self.module_name}({self.io['input_ports']}{self.io['output_ports'][:-1]});\n"
        self.module_LLverilog+=self.node_to_txt(mode="input")
        self.module_LLverilog+=self.node_to_txt(mode="output")
        self.module_LLverilog+=self.node_to_txt(mode="wire")
        self.module_LLverilog+=self.gates_to_txt()
        self.module_LLverilog+=self.module_to_txt()
        self.module_LLverilog+="endmodule\n"



class AST:
    def __init__(self,file_path,top=None, rw = 'w', flag = 'v',filename=None,vlibpath="vlib/mycells.v"):
        self.LLverilog = ""
        if(filename==None):
            self.filename=top
            self.filepath="./output_files/{}.json".format(top)
        else:
            self.filename=filename
            self.filepath="./output_files/{}.json".format(self.filename)
        if rw == 'r':
            self.read_LLFile(file_path)
        elif rw == 'w':
            if flag == 'v':
                self.verilog = open(file_path).read()
                # self.verilog=re.sub(r"//.*\n","",self.verilog)
                # self.verilog=re.sub(r"/\*.*?\*/", "", self.verilog, flags=re.DOTALL)
                self.verilog=format_verilog_org(self.verilog)
            elif flag == 'b':
                self.bench = open(file_path).read()
                self.verilog = bench_to_verilog(self.bench)
            else:
                Exception("Enter either 'v' (for verilog) or 'b' (for bench)")
            
            self.synthesized_verilog = None
            self.extracted_modules = None
            self.top_module = module()
            self.modules = {}
            self.top_module_name=top
            self.gate_lib=open(vlibpath).read()
            
            self.gen_LLFile()
            self.writeLLFile() 
        else:
            Exception("Enter either 'r' (for read) or 'w' (for write)")
        

        

    def gen_LLFile(self):
        self.synthesized_verilog = synthesize_verilog(self.verilog,top=self.top_module_name)#,flag="dont_flatten"
        self.gate_level_flattened = synthesize_verilog(self.verilog,top=self.top_module_name)
        self.flatten_bench = verilog_to_bench(self.gate_level_flattened)

        self.modules_techmap = module_extraction(self.synthesized_verilog)
        self.extracted_modules = module_extraction(self.synthesized_verilog)
        self.no_of_modules = len(self.extracted_modules)

        self.sub_modules_data()
        for i in self.modules:
            self.gen_graph_links(self.modules[i])
            # self.modules[i].bin_graph()
        
        self.gen_module_connections()
            
        
    def sub_modules_data(self):
        for key in self.extracted_modules:
            self.modules[key]=module()
            self.modules[key].module_name = key
            self.modules[key].org_code_verilog = self.extracted_modules[key]
            self.modules[key].gate_level_verilog = self.modules_techmap[key]
            self.modules[key].gates,self.modules[key].linkages = gates_module_extraction(self.modules[key].gate_level_verilog)
            inputs, input_ports = extract_io_v(self.modules[key].org_code_verilog)
            outputs, output_ports = extract_io_v(self.modules[key].org_code_verilog, "output")
            wire, _ = extract_io_v(self.modules[key].gate_level_verilog, "wire")
            wire={key:wire[key]  for key in get_difference_abs(wire.keys(),inputs.keys(),outputs.keys())}
            # print("N4944" in  wire.keys())
            # print(get_diference(wire.keys(),outputs.keys()))
            
            # print("N1947" in outputs.keys())
            # print(self.modules[key].gates)
            self.modules[key].io = dict({'wires':wire,'inputs':inputs,'outputs':outputs,'input_ports':input_ports,'output_ports':output_ports})
            self.modules[key].gen_graph()
        self.top_module=self.modules[self.top_module_name]
            

    def writeLLFile(self):
        self.update_LLverilog()
        ast_dict = dict({"orginal_code" : self.verilog, "gate_lib":self.gate_lib,"gate_level_flattened" : self.gate_level_flattened,"Bench_format_flattened" : self.flatten_bench, "gate_level_not_flattened" : self.synthesized_verilog, "top_module_name" : self.top_module_name,"Total_number_of_modules":self.no_of_modules,"LL_gatelevel_verilog":self.LLverilog,"bitkey":self.top_module.bitkey})
        # top_dict = dict({"Verilog": self.top_module.org_code_verilog, "Synthesized_verilog" : self.top_module.gate_level_verilog, "Total_number_of_modules":self.no_of_modules, "io":self.top_module.io, "gates": self.top_module.gates, "links" : self.top_module.linkages, "DiGraph":self.top_module.base64_data})
        # top_dict = dict({"Total_number_of_modules":self.no_of_modules, "io":self.top_module.io, "gates": self.top_module.gates, "links" : self.top_module.linkages, "DiGraph":self.top_module.base64_data})

        sub_dict = {}
        for key in list(self.modules.keys()):
            self.modules[key].bin_graph()
            sub_dict[key] = dict({"Verilog": self.modules[key].org_code_verilog, "Synthesized_verilog" : self.modules[key].gate_level_verilog,"lockingdata":self.modules[key].lockingdata,"DiGraph":self.modules[key].base64_data, "io":self.modules[key].io, "gates": self.modules[key].gates, "links" : self.modules[key].linkages})


        ast = dict({"AST":ast_dict, "modules": sub_dict})

        json_file = json.dumps(ast, indent = 4)
        with open(self.filepath, "w") as verilog_ast:
            verilog_ast.write(json_file)


    def gen_graph_links(self,module):
        def process_node(R):
            if(":" in R):
                node,endbit,startbit=re.findall("(.*)\[(\d+):?(\d*)\]",R)[0]
                endbit,startbit=int(endbit),int(startbit)
            elif("[" in R):
                node,bit=re.findall("(.*)\[(\d+)\]",R)[0]
                # print(node)
                endbit,startbit=int(bit),int(bit)
            else:
                node=R
                endbit,startbit=None,None

            if(node in module.io['inputs']):
                Node=module.io['inputs'][node]
                type='input'
            elif(node in module.io['outputs']):
                Node=module.io['outputs'][node]
                type='output'
            elif(node in module.io['wires']):
                Node=module.io['wires'][node]
                type='wire'
            else:
                # print(module.module_name,R)
                raise Exception("NODE NOT FOUND")

            if(endbit==None):
                endbit=Node['endbit']
                startbit=Node['startbit']

            return node,type,endbit,startbit

        for ii in module.linkages:
            i=module.linkages[ii]
            module_node_name="module#"+ii
            module.circuitgraph.add_node(module_node_name, type="module",module_name=i['module_name'],init_name=ii)

            for L,R in zip(i['L'],i['R']):
                # L,R=j
                # print(L,R)
                node,type,endbit,startbit=process_node(R)
                # node="wire#"+node if type=="wire" else node
                if(L in self.modules[i['module_name']].io['inputs']):
                    for k in range(startbit,endbit+1):
                        module.circuitgraph.add_node(node+f"[{k}]",type=type,port=node)
                        module.circuitgraph.add_edge(node+f"[{k}]",module_node_name)
                elif(L in self.modules[i['module_name']].io['outputs']):
                    for k in range(startbit,endbit+1):
                        module.circuitgraph.add_node(node+f"[{k}]",type=type,port=node)
                        module.circuitgraph.add_edge(module_node_name,node+f"[{k}]")
                else:
                    raise Exception("NODE NOT FOUND")
            
    
    def read_LLFile(self, file_path):
        with open(file_path) as json_file:
            verilog_ast = json.load(json_file)

        self.top_module = module()
        self.modules = {}
        self.verilog =  verilog_ast["AST"]["orginal_code"]
        self.gate_level_flattened = verilog_ast["AST"]["gate_level_flattened"]
        self.synthesized_verilog = verilog_ast["AST"]["gate_level_not_flattened"]
        self.top_module_name  = verilog_ast["AST"]["top_module_name"]
        self.no_of_modules = verilog_ast["AST"]["Total_number_of_modules"]
        self.flatten_bench=verilog_ast["AST"]["Bench_format_flattened"]
        self.gate_lib=verilog_ast["AST"]["gate_lib"]

        keys = list((verilog_ast["modules"]).keys())
        for i in keys:
            self.modules[i]=module()
            self.modules[i].module_name = i
            self.modules[i].org_code_verilog = verilog_ast["modules"][i]["Verilog"]
            self.modules[i].gate_level_verilog = verilog_ast["modules"][i]["Synthesized_verilog"]
            self.modules[i].io = verilog_ast["modules"][i]["io"]
            self.modules[i].gates = verilog_ast["modules"][i]["gates"]
            self.modules[i].linkages = verilog_ast["modules"][i]["links"]
            self.modules[i].lockingdata=verilog_ast["modules"][i]["lockingdata"]
            #Decode the base64 string back to binary
            # Decode the binary string back to a graph object
            self.modules[i].base64_data = verilog_ast["modules"][i]["DiGraph"]
            self.modules[i].circuitgraph = pickle.loads(base64.b64decode(self.modules[i].base64_data.encode('utf-8')))
        self.top_module=self.modules[self.top_module_name]
        self.top_module.bitkey=verilog_ast["AST"]["bitkey"]
    
    
    def gen_module_connections(self):
        self.module_connections = nx.DiGraph()
        for i in self.modules:
            tmpi=self.modules[i]
            for jj in tmpi.linkages:
                j=tmpi.linkages[jj]
                module_name = j['module_name']
                init_name = jj  
                # Check if an edge already exists in the graph
                if self.module_connections.has_edge(i, module_name):
                    # If an edge already exists, update its attributes without overwriting
                    # existing ones
                    tmp=[self.module_connections[i][module_name]['init_name']]
                    tmp.append(init_name)
                    # print(tmp)
                    self.module_connections[i][module_name].update({'init_name': tmp})
                else:
                    # If no edge exists, add a new edge with the specified attributes
                    self.module_connections.add_edge(i, module_name, init_name=init_name) 

    
    def save_module_connections(self):
        save_graph(self.module_connections)
    
    def update_LLverilog(self):
        for i in self.modules:
            self.modules[i].gen_LL_verilog()
        self.LLverilog=""
        self.LLverilog+=self.top_module.module_LLverilog+"\n"
        for i in self.modules:
            if(i!=self.top_module_name):
                self.LLverilog+=self.modules[i].module_LLverilog+"\n"
        
        # self.LLverilog+=self.gate_lib

    def gen_verification_files(self):
        self.update_LLverilog()
        cir,testbench=gen_miterCircuit(self.gate_level_flattened,self.LLverilog)

        with open("./tmp/top.v","w") as f:
            f.write(cir)

        with open("./tmp/testbench.v","w") as f:
            f.write(testbench)


        path="./tmp/top.v"
        verify_verilog(path,'top')
        print("Verification Done Without Error")






















# // module locked(inputs, key, out);
# // input [7:0] inputs;
# // input [7:0] key;
# // output [1:0]out;
# // sarlock s(.inputs(inputs), .key(key), .lock_out(out[0]));
# // sarlock s1(.inputs(inputs), .key(key), .lock_out(out[1]));
# // endmodule

# // module ckt(a,b,c);
# // input [3:0] a,b;
# // output [4:0] c;
# // assign	c = a + b;
# // endmodule

# // module sarlock (inputs, key, lock_out);
# // input [7:0] inputs;
# // input [7:0] key;
# // output lock_out;
# // wire [4:0]ckt_out; 
# // reg keyx = 8'b01101101;
# // assign lock_out =ckt_out[0]^( (inputs == key) & (inputs != keyx));
# // ckt c(.a(inputs[3:0]), .b(inputs[7:4]), .c(ckt_out));
# // endmodule

