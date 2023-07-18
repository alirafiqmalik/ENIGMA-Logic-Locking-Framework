import os
import json
import base64
import pickle
import networkx as nx


# from src.utils import *
import src.utils as utils
import src.yosys as yosys
import src.Parser.conv as conv
import src.Parser.verilog_parser as verilog_parser
from src.Verification.verification import *





class module:
    def __init__(self):
        """
        Initialize the module object.
        """
        self.change_flag=1
        self.org_code_verilog = None
        self.org_code_bench = None
        self.gate_level_verilog = None
        self.module_name = None
        self.gates = None
        self.FF_tech=None
        self.io = None
        self.circuitgraph=None
        self.module_LLverilog=""
        self.lockingdata={"wires":[],"gates":[],"inputs":[]}
        self.bitkey=""
        # self.module_LLverilog=None
        # self.module_LLcircuitgraph=None
    
    def gen_graph(self):
        """
        Generate the circuit graph.
        """
        self.circuitgraph = nx.DiGraph()
        for logic_gate in self.gates:
            for init_name in self.gates[logic_gate]:
                node=self.gates[logic_gate][init_name]
                tmpi=self.gates[logic_gate]
                node_input=node["inputs"]
                node_output=node["outputs"]
                node_name=init_name
                port=utils.check_port(node_output)
                self.circuitgraph.add_node(node_name, type="gate",logic=logic_gate)

                if(port in self.io["outputs"]):
                    self.circuitgraph.add_node(node_output, type="output")
                    self.circuitgraph.add_edge(node_name, node_output)
                elif(port in self.io["wires"]):
                    self.circuitgraph.add_node(node_output, type="wire")
                    self.circuitgraph.add_edge(node_name, node_output)
                else:
                    print(self.module_name)
                    print(port,node_output)
                    raise Exception("NODE NOT FOUND")


                for i in node_input:
                    def tmp():
                        if("XNOR_117153_" in init_name):
                            print("HERE212 ",i,node_input,node_name)
                    tmptxt=utils.check_port(i)

                    if(tmptxt in self.io["inputs"]):
                        self.circuitgraph.add_node(i, type="input",port=tmptxt)
                        self.circuitgraph.add_edge(i,node_name)
                    elif(tmptxt in self.io["outputs"]):
                        self.circuitgraph.add_node(i, type="output",port=tmptxt)
                        self.circuitgraph.add_edge(i,node_name)
                        # tmp()
                        # print(i)
                    elif(tmptxt in self.io["wires"]):
                        self.circuitgraph.add_node(i, type="wire",port=tmptxt)
                        self.circuitgraph.add_edge(i,node_name)
                    elif(i in self.io["wires"]):
                        self.circuitgraph.add_node(i, type="wire",port=tmptxt)
                        self.circuitgraph.add_edge(i,node_name)
                    elif("1'" in i):
                        self.circuitgraph.add_node(i, type="bit",value=i)
                        self.circuitgraph.add_edge(i,node_name)
                    else:
                        print("HERE")
                        print(self.module_name," ==>> ",tmptxt,i)
                        raise Exception("NODE NOT FOUND")

        # print("HERE",self.FF_tech)
        for FF in self.FF_tech:
            for init_name in self.FF_tech[FF]:
                tmpi=self.FF_tech[FF]
                node=tmpi[init_name]
                node_input=node["inputs"]
                node_output=node["outputs"]
                node_name=init_name
                
                rst=node.get("reset")
                clk=node.get("clock")
                self.circuitgraph.add_node(node_name, type=FF,clock=clk,reset=rst)
                # print(init_name)
                



                self.circuitgraph.add_node(clk, type="input")
                self.circuitgraph.add_edge(clk, node_name)

                if(rst!=None):
                    self.circuitgraph.add_node(rst, type="input")
                    self.circuitgraph.add_edge(rst, node_name)

                port=utils.check_port(node_output)
                if(port in self.io["outputs"]):
                    self.circuitgraph.add_node(node_output, type="output",port=port)
                    self.circuitgraph.add_edge(node_name, node_output)
                elif(port in self.io["wires"]):
                    self.circuitgraph.add_node(node_output, type="wire",port=port)
                    self.circuitgraph.add_edge(node_name, node_output)
                else:
                    print(self.module_name)
                    print(port,node_output)
                    raise Exception("NODE NOT FOUND")
                

                tmptxt=utils.check_port(node_input)
                if(tmptxt in self.io["inputs"]):
                    self.circuitgraph.add_node(node_input, type="input",port=tmptxt)
                    self.circuitgraph.add_edge(node_input,node_name)
                elif(tmptxt in self.io["outputs"]):
                    self.circuitgraph.add_node(node_input, type="output",port=tmptxt)
                    self.circuitgraph.add_edge(node_name,node_input)
                elif(tmptxt in self.io["wires"]):
                    self.circuitgraph.add_node(node_input, type="wire",port=tmptxt)
                    self.circuitgraph.add_edge(node_input,node_name)
                elif(node_input in self.io["wires"]):
                    self.circuitgraph.add_node(node_input, type="wire",port=node_input)
                    self.circuitgraph.add_edge(node_input,node_name)
                elif("1'h" in node_input):
                    self.circuitgraph.add_node(node_input, type="bit",value=int(node_input[-1]))
                    self.circuitgraph.add_edge(node_input,node_name)
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
        self.change_flag=0
  
    def bin_graph(self):
        """
        Encode the circuit graph to a binary string using pickle and encode the binary string to a base64 string.
        """
        self.base64_data = base64.b64encode(pickle.dumps(self.circuitgraph)).decode('utf-8')

    def nodeio(self,Node)->None:
        """
        Print the outputs and inputs of a node in the circuit graph.
        
        Args:
            Node (str): The name of the node.
        """
        print("Node outputs = ",list(self.circuitgraph.successors(Node))) 
        print("Node inputs = ",list(self.circuitgraph.predecessors(Node)))    
    
    def save_graph(self,svg=False):
        """
        Save the circuit graph as an SVG image.
        
        Args:
            svg (bool): Whether to save the graph as an SVG image (default: False).
        """
        utils.save_graph(self.circuitgraph,svg)



    def gen_org_verilog(self):
        """
        Generate the orginal verilog code for the module.
        """
        self.gate_level_verilog=f"module {self.module_name}({self.io['input_ports']}{self.io['output_ports'][:-1]});\n"
        self.gate_level_verilog+=utils.node_to_txt(self.io['inputs'],mode="input")
        self.gate_level_verilog+=utils.node_to_txt(self.io['outputs'],mode="output")
        self.gate_level_verilog+=utils.node_to_txt(self.io['wires'],mode="wire")
        # print(self.gates)
        self.gate_level_verilog+=utils.gates_to_txt(self.gates)
        self.gate_level_verilog+=utils.FF_to_txt(self.FF_tech)
        # self.module_LLverilog+=module_to_txt(self.linkages)
        for j in self.linkages:
            tmpj=self.linkages[j]
            self.gate_level_verilog+=f"{tmpj['module_name']} {j}({tmpj['port']}); \n"
        self.gate_level_verilog+="endmodule\n"


    def gen_LL_verilog(self):
        """
        Generate the LL verilog code for the module.
        """
        self.module_LLverilog=f"module {self.module_name}({self.io['input_ports']}{self.io['output_ports'][:-1]});\n"
        self.module_LLverilog+=utils.node_to_txt(self.io['inputs'],mode="input")
        self.module_LLverilog+=utils.node_to_txt(self.io['outputs'],mode="output")
        self.module_LLverilog+=utils.node_to_txt(self.io['wires'],mode="wire")
        self.module_LLverilog+=utils.gates_to_txt(self.gates)
        self.module_LLverilog+=utils.FF_to_txt(self.FF_tech)
        # self.module_LLverilog+=module_to_txt(self.linkages)
        for j in self.linkages:
            tmpj=self.linkages[j]
            self.module_LLverilog+=f"{tmpj['module_name']} {j}({tmpj['port']}); \n"
        self.module_LLverilog+="endmodule\n"
        # if(self.postSAT_modules!={}):
        #     self.module_LLverilog+=module_to_txt(self.postSAT_modules)


class AST:
    """

    
    """
    def __init__(self,
                 file_path,
                 top=None,
                 rw = 'w',
                 flag = 'v',
                 filename=None,
                 vlibpath="vlib/mycells.v",
                 sub_modules=None
                 ):
        self.LLverilog = ""
        self.postsat_lib=""
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
                
                if(sub_modules!=None):
                    if(type(sub_modules)==list):
                        for files in sub_modules:
                            self.verilog+=open(files).read()
                    else:
                        self.verilog+=open(sub_modules).read()
                
                tmp_file_path=f"./tmp/tmp_verilog_{top}.v"
                with open(tmp_file_path,"w") as f:
                    f.write(self.verilog)
                # self.verilog=format_verilog_org(self.verilog)
                print("Verifiying Input Verilog File")
                yosys.verify_verilog(tmp_file_path,top)
                print("Input Verilog File Verified Without Issue")
                os.remove(tmp_file_path)
                
            elif flag == 'b':
                self.bench = open(file_path).read()
                self.verilog = conv.bench_to_verilog(self.bench)
            else:
                Exception("Enter either 'v' (for verilog) or 'b' (for bench)")
            
            self.synthesized_verilog = None
            self.extracted_modules = None
            self.top_module = module()
            self.modules = {}
            # self.linkages={}
            self.top_module_name=top
            self.gate_lib=open(vlibpath).read()
            self.gate_mapping_vlib,self.gates_vlib,self.FF_vlib=verilog_parser.extract_modules_def(self.gate_lib)
            self.gen_LLFile()
            self.writeLLFile() 
        else:
            Exception("Enter either 'r' (for read) or 'w' (for write)")
        
    def gen_LLFile(self):
        print("Generating Logic Locking AST File")
        self.synthesized_verilog = yosys.synthesize_verilog(self.verilog,top=self.top_module_name)#,flag="dont_flatten"
        self.gate_level_flattened=self.synthesized_verilog
        # self.gate_level_flattened = synthesize_verilog(self.verilog,top=self.top_module_name)
        self.flatten_bench = conv.verilog_to_bench(self.gate_level_flattened,self.gate_mapping_vlib)

        self.modules_techmap = utils.module_extraction(self.synthesized_verilog)
        self.extracted_modules = utils.module_extraction(self.synthesized_verilog)
        self.no_of_modules = len(self.extracted_modules)

        self.sub_modules_data()
        self.gen_graph_links()

        print("Done Generating Logic Locking AST File")
            # self.modules[i].bin_graph()
        
        # self.gen_module_connections()        
        
    def sub_modules_data(self):
        for key in self.extracted_modules:
            self.modules[key]=module()
            self.modules[key].module_name = key
            self.modules[key].org_code_verilog = self.extracted_modules[key]
            self.modules[key].gate_level_verilog = self.modules_techmap[key]
            self.modules[key].gates,self.modules[key].linkages,tmp = utils.gates_module_extraction(self.modules[key].gate_level_verilog,self.gate_mapping_vlib,self.gates_vlib,self.FF_vlib)
            self.modules[key].FF_tech,self.modules[key].Clock_pins,self.modules[key].Reset_pins=tmp


            # print(self.modules[key].linkages.keys())

            inputs, input_ports = extract_io_v(self.modules[key].org_code_verilog)
            outputs, output_ports = extract_io_v(self.modules[key].org_code_verilog, "output")
            wire, _ = extract_io_v(self.modules[key].gate_level_verilog, "wire")
            wire={key:wire[key]  for key in get_difference_abs(wire.keys(),inputs.keys(),outputs.keys())}


            for i in self.modules[key].Clock_pins:
                if(("1'" in i) or (i not in inputs.keys())):
                    self.modules[key].Clock_pins.remove(i)
            # print("N4944" in  wire.keys())
            # print(get_diference(wire.keys(),outputs.keys()))
            # print("HERE",wire["cpuregs[5]"])
            
            # print("N1947" in outputs.keys())
            # print(self.modules[key].gates)
            self.modules[key].io = dict({"Clock_pins":self.modules[key].Clock_pins,"Reset_pins":self.modules[key].Reset_pins,'wires':wire,'inputs':inputs,'outputs':outputs,'input_ports':input_ports,'output_ports':output_ports})
            self.modules[key].gen_graph()
        self.top_module=self.modules[self.top_module_name]
            
    def writeLLFile(self):
        print("Writing LL file")
        self.update_LLverilog()
        ast_dict = dict({"top_module_name" : self.top_module_name,"Total_number_of_modules":self.no_of_modules,"LL_gatelevel_verilog":self.LLverilog,"bitkey":self.top_module.bitkey})
        # top_dict = dict({"Verilog": self.top_module.org_code_verilog, "Synthesized_verilog" : self.top_module.gate_level_verilog, "Total_number_of_modules":self.no_of_modules, "io":self.top_module.io, "gates": self.top_module.gates, "links" : self.top_module.linkages, "DiGraph":self.top_module.base64_data})
        # top_dict = dict({"Total_number_of_modules":self.no_of_modules, "io":self.top_module.io, "gates": self.top_module.gates, "links" : self.top_module.linkages, "DiGraph":self.top_module.base64_data})

        sub_dict = {}
        for key in list(self.modules.keys()):
            self.modules[key].bin_graph()
            sub_dict[key] = dict({"Verilog": self.modules[key].org_code_verilog, "Synthesized_verilog" : self.modules[key].gate_level_verilog,"lockingdata":self.modules[key].lockingdata,"DiGraph":self.modules[key].base64_data, "io":self.modules[key].io, "gates": self.modules[key].gates,"FF":self.modules[key].FF_tech,"links" : self.modules[key].linkages})#"postSAT_modules" : self.modules[key].postSAT_modules, "links" : self.modules[key].linkages


        ast = dict({"AST":ast_dict,"modules": sub_dict})

        json_file = json.dumps(ast, indent = 4)
        with open(self.filepath, "w") as verilog_ast:
            verilog_ast.write(json_file)
        print("Done Writing LL file")

    def gen_graph_links(self):
        def process_node(R,module):
            if(":" in R):
                node,startbit,endbit=re.findall("(.*)\[(\d+):?(\d*)\]",R)[0]
                endbit,startbit=int(endbit),int(startbit)
            elif("[" in R):
                node,bit=re.findall("(.*)\[(\d+)\]",R)[0]
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
                print(module.module_name,R)
                raise Exception("NODE NOT FOUND")

            if(endbit==None):
                # print(Node)
                if(Node['bits']==1):
                    endbit=0
                    startbit=0
                else:
                    endbit=Node['endbit']
                    startbit=Node['startbit']
                    
            return node,type,endbit,startbit

        def process_links(module):
            links=module.linkages
            for ii in links:
                i=links[ii]
                module_node_name="module#"+ii
                module.circuitgraph.add_node(module_node_name, type="module",module_name=i['module_name'],init_name=ii)

                for x in i['links']:
                    L,R,T=x
                    node,type,endbit,startbit=process_node(R,module)
                    if(T=="I"):
                        if(endbit==0):
                            module.circuitgraph.add_node(node,type=type,port=node)
                            module.circuitgraph.add_edge(node,module_node_name)
                        else:
                            # print(R,node,module_node_name)
                            for k in range(startbit,endbit+1):
                                module.circuitgraph.add_node(node+f"[{k}]",type=type,port=node)
                                module.circuitgraph.add_edge(node+f"[{k}]",module_node_name)
                    elif(T=="O"):
                        if(endbit==0):
                            module.circuitgraph.add_node(node,type=type,port=node)
                            module.circuitgraph.add_edge(module_node_name,node)
                        else:
                            for k in range(startbit,endbit+1):
                                module.circuitgraph.add_node(node+f"[{k}]",type=type,port=node)
                                module.circuitgraph.add_edge(module_node_name,node+f"[{k}]")
                    else:
                        raise Exception("NODE NOT FOUND")
   
                # if(L in self.modules[i['module_name']].io['inputs']):
                #     for k in range(startbit,endbit+1):
                #         module.circuitgraph.add_node(node+f"[{k}]",type=type,port=node)
                #         module.circuitgraph.add_edge(node+f"[{k}]",module_node_name)
                # elif(L in self.modules[i['module_name']].io['outputs']):
                #     for k in range(startbit,endbit+1):
                #         module.circuitgraph.add_node(node+f"[{k}]",type=type,port=node)
                #         module.circuitgraph.add_edge(module_node_name,node+f"[{k}]")
                # else:
                #     raise Exception("NODE NOT FOUND")
        
        for i in self.modules:
            process_links(self.modules[i])

    def read_LLFile(self, file_path):
        print("Reading LL file")
        print("\t Loading json file")
        with open(file_path) as json_file:
            verilog_ast = json.load(json_file)
        
        print("\t Done Loading json file")

        print("\t Loading Top module in AST")
        self.top_module = module()
        self.modules = {}
        self.verilog =  verilog_ast["AST"]["orginal_code"]
        self.gate_level_flattened = verilog_ast["AST"]["gate_level_flattened"]
        self.synthesized_verilog = verilog_ast["AST"]["gate_level_not_flattened"]
        self.top_module_name  = verilog_ast["AST"]["top_module_name"]
        self.no_of_modules = verilog_ast["AST"]["Total_number_of_modules"]
        self.flatten_bench=verilog_ast["AST"]["Bench_format_flattened"]
        self.gate_lib=verilog_ast["AST"]["gate_lib"]
        # self.linkages=verilog_ast["linkages"]
        print(f"\t Done Loading Top module {self.top_module_name} in AST")

        keys = list((verilog_ast["modules"]).keys())
        print("\t Loading module data in AST")
        for i in keys:
            print(f"\t\t Loading module {i} in AST")
            self.modules[i]=module()
            self.modules[i].module_name = i
            self.modules[i].org_code_verilog = verilog_ast["modules"][i]["Verilog"]
            self.modules[i].gate_level_verilog = verilog_ast["modules"][i]["Synthesized_verilog"]
            self.modules[i].io = verilog_ast["modules"][i]["io"]
            self.modules[i].gates = verilog_ast["modules"][i]["gates"]
            self.modules[i].linkages = verilog_ast["modules"][i]["links"]
            self.modules[i].FF_tech=verilog_ast["modules"][i]["FF"]
            # self.modules[i].postSAT_modules = verilog_ast["modules"][i]["postSAT_modules"]
            self.modules[i].lockingdata=verilog_ast["modules"][i]["lockingdata"]
            #Decode the base64 string back to binary
            # Decode the binary string back to a graph object
            self.modules[i].base64_data = verilog_ast["modules"][i]["DiGraph"]
            self.modules[i].circuitgraph = pickle.loads(base64.b64decode(self.modules[i].base64_data.encode('utf-8')))
            print(f"\t\t Done Loading module {i} in AST")
        print("\t Done Loading module data in AST")
        self.top_module=self.modules[self.top_module_name]
        self.top_module.bitkey=verilog_ast["AST"]["bitkey"]
        print("Done Reading LL file")
    
    # def gen_module_connections(self):
    #     self.module_connections = nx.DiGraph()
    #     for i in self.modules:
    #         tmpi=self.modules[i]
    #         for jj in tmpi.linkages:
    #             j=tmpi.linkages[jj]
    #             module_name = j['module_name']
    #             init_name = jj  
    #             # Check if an edge already exists in the graph
    #             if self.module_connections.has_edge(i, module_name):
    #                 # If an edge already exists, update its attributes without overwriting
    #                 # existing ones
    #                 tmp=[self.module_connections[i][module_name]['init_name']]
    #                 tmp.append(init_name)
    #                 # print(tmp)
    #                 self.module_connections[i][module_name].update({'init_name': tmp})
    #             else:
    #                 # If no edge exists, add a new edge with the specified attributes
    #                 self.module_connections.add_edge(i, module_name, init_name=init_name) 

    
    # def save_module_connections(self):
    #     save_graph(self.module_connections)
    

    # def update_org_verilog(self):
    #     self.gate_level_flattened=""
    #     for i in self.modules:
    #         self.modules[i].gen_org_verilog()
    #         self.LLverilog=""
    #         self.gate_level_flattened+=self.top_module.gate_level_verilog+"\n"
    #         for i in self.modules:
    #             if(i!=self.top_module_name):
    #                 self.gate_level_flattened+=self.modules[i].gate_level_verilog+"\n"


    def update_LLverilog(self):
        for i in self.modules:
            if(self.modules[i].change_flag==1):
                self.modules[i].gen_graph()
        self.gen_graph_links()
        
        
        
        if("lockingkeyinput" in self.top_module.io["inputs"]):
            print("\t Updating Logic Locked Verilog Code")
            for i in self.modules:
                self.modules[i].gen_LL_verilog()
            self.LLverilog=""
            self.LLverilog+=self.top_module.module_LLverilog+"\n"
            for i in self.modules:
                if(i!=self.top_module_name):
                    self.LLverilog+=self.modules[i].module_LLverilog+"\n"
            
            self.postsat_lib=""
            for i in self.modules:
                tmpi=self.modules[i]
                for j in tmpi.linkages:
                    self.postsat_lib+="\n"+tmpi.linkages[j]['code']+"\n"
            print("\t Done Updating Logic Locked Verilog Code")
        else:
            print("\t Netlist Not Locked, No Update to Peform")


    def write_Verilog_File(self,file="LL",file_name="",output_dir=r"./tmp/"):
        print("Generating Output Verilog File")
        if(file=="LL"):
            cir=self.LLverilog+"\n\n\n"+self.postsat_lib+"\n\n\n"+self.gate_lib
            cir=re.sub(r"\n",r"\n ",cir)
            cir=re.sub(r" module",r"module",cir)
            cir=re.sub(r" endmodule",r"endmodule",cir)

            bits=self.top_module.io["inputs"]["lockingkeyinput"]['bits']

            cir=yosys.synthesize_verilog_flatten_gate(verilog=cir,top=self.top_module_name)
            cir=f"// lockingkey = {bits}'b{self.top_module.bitkey} \n"+cir
        elif(file=="org"):
            cir=self.gate_level_flattened + "\n\n\n" + self.gate_lib
            cir=re.sub(r"\n",r"\n ",cir)
            cir=re.sub(r" module",r"module",cir)
            cir=re.sub(r" endmodule",r"endmodule",cir)

            cir=yosys.synthesize_verilog_flatten_gate(verilog=cir,top=self.top_module_name)
        else:
            raise Exception(f"Wrong file type {file}")
        

        cir=format_verilog_org(cir)
        cir=re.sub(r"\n",r"\n ",cir)
        # cir=re.sub(r"module",r"\n module",cir)
        # cir=re.sub(r"endmodule",r"endmodule\n",cir)
        cir=re.sub(r"\\","",cir)
        cir=re.sub(r"\s+module",r" \n\nmodule",cir)
        cir=re.sub(r"\s+endmodule",r" endmodule",cir)


        top_path=os.path.join(output_dir,f"top{file_name}.v")

        print(f"\t Writing Output Verilog File to {top_path}")
        with open(top_path,"w") as f:
            f.write(cir)
        
        print("\t Done")
        yosys.verify_verilog(top_path,self.top_module_name)
        

        print("Done Generating Output Verilog File")



    def gen_verification_files(self,file_name="",output_dir=r"/mnt/d/alis_files/LAPTOP/alis_files/university_files/PROJECTS_2022-2023/FYP/Circuits/top"):
        # r"/mnt/d/alis_files/LAPTOP/alis_files/university_files/PROJECTS_2022-2023/FYP/Circuits/top"
        # self.update_LLverilog()
        print("Generating Verification Files")
        # print("\t Updating Logic Locked Verilog Code")
        # self.update_LLverilog()
        print(f"\t Generating Miter Circuit Verilog and Testbench")
        cir,testbench=gen_miterCircuit(self.gate_level_flattened,self.LLverilog,self.postsat_lib+"\n\n\n"+self.gate_lib,self.top_module_name,self.top_module.bitkey,self.top_module.io["Clock_pins"])

        cir=re.sub(r"\n",r"\n ",cir)
        cir=re.sub(r" module",r"module",cir)
        cir=re.sub(r" endmodule",r"endmodule",cir)


        top_path=os.path.join(output_dir,f"top{file_name}.v")
        test_path=os.path.join(output_dir,f"testbench{file_name}.sv")
        # print(top_path,test_path)
        print(f"\t Writing miter circuit verilog to {top_path}")
        with open(top_path,"w") as f:
            f.write(cir)
        print("\t Done")

        print(f"\t Writing miter circuit testbench to {test_path}")
        with open(test_path,"w") as f:
            f.write(testbench)
        print("\t Done")
        
        print("\t Verifying Miter circuit top.v")
        yosys.verify_verilog(top_path,'top')
        print("\t Verification Done Without Error")
        print("Done Generating Verification Files")




    def gen_results(self,org=True):
        gate_count=0
        for i in self.top_module.gates:
            gate_count+=len(self.top_module.gates[i])
        
        if(org):
            self.org_gate_count=gate_count
            return gate_count
        else:
            self.LL_gate_count=gate_count
            FF_count=0
            for i in self.top_module.FF_tech:
                FF_count+=len(self.top_module.FF_tech[i])

            overhead=(gate_count-self.org_gate_count)*100/gate_count
            return gate_count,overhead,FF_count
            print("Overhead in Number of Gates: ",(gate_count-self.org_gate_count)*100/gate_count)
            print("Expected Overhead in Number of Flip-Flops: ",(gate_count-self.org_gate_count)*100/FF_count)
            






















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

