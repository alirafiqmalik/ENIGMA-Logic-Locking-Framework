from src.AST import AST
from src.PreSAT import LogicLocking



# obj=AST(file_path="./input_files/tmporg.v",rw="w",flag="v",top="locked",filename="locked_new")
obj = AST(file_path="./output_files/locked_new.json",rw='r',top="locked",filename="locked") # r for read from file
# obj.save_module_connections()


# LL=LogicLocking(obj.modules['sarlock'])

# LL.RLL(6,8)

# obj.modules['sarlock']
















# for i in obj.modules['sarlock'].circuitgraph.nodes:
#   print(i,obj.modules['sarlock'].circuitgraph.nodes[i])


obj.modules['sarlock'].save_graph()


obj.writeLLFile()




# import random

# rndx=list(obj.module_connections.nodes())
# rndi=random.randint(0,len(rndx)-1)




# print(rndx[rndi])
# # rnd=


# # for i in obj.module_connections:
# #   print(i)



# # print(i,j['module_name'],module_connections[i][j['module_name']])  







# module=obj.modules["locked"]
# for i in obj.modules:
#   tmpi=obj.modules[i]
#   print(i)
#   for j in tmpi.linkages:
#     print(j["module_name"],j["init_name"])
#   print("#####################")



# for i in obj.modules:
#   tmpi=obj.modules[i]
#   print(i)
#   for j in tmpi.linkages:
#     tmpi.io["inputs"]["lockingkey"]=connector(4,3,0)
#     print(obj.modules[i].io["inputs"])
    
#     # print(i,j['module_name'],j['init_name'])
#     j['L'].append("key")
#     j['R'].append("lockingkey[0]")




# for i in obj.modules:
#   tmpi=obj.modules[i]
#   # print(i)
#   # tmpi.bin_graph()
#   for j in tmpi.linkages:
#     # print(i,j['module_name'],j['init_name'])
#     port=""
#     for L,R in zip(j['L'],j['R']):
#       # print(L,R)
#       port+=f".{L}({R}), "
#       # pass
#     # for k in j['links']:
#     #   port+=f".{k[0]}({k[1]}), "
#     #   # print(f".{k[0]}({k[1]}), ",end="")
#     print(port[:-2])



# obj.writeLLFile()
# obj.update_LLverilog()

# obj.top_module.save_graph()

# def t(self):
#   LLverilog=""
#   LLverilog+=self.top_module.gate_level_verilog+"\n"
#   for i in self.modules:
#     LLverilog+=self.modules[i].gate_level_verilog+"\n"
#   return LLverilog


# LLverilog=t(obj)
# # print(LLverilog) 
























































































































#obj=AST("./input_files/tmporg.v",rw="w",flag="v")
# tmp=open("tmp/tmp_syn2dont_flatten.v").read()
# print(format_verilog(tmp,remove_wire=True))



# print(obj.top_module.gates)
# print(list(obj.top_module.linkages.keys())[0])
# print()

# for i in obj.modules:
#     print(i.module_name,end=" ==>  ")
#     print(i.gates.keys())
#     print(i.linkages.keys())
    




















# class Netlist():
#   def __init__(self,AST,netlist:str)->None:#mode:str="graph"
#     self.AST=AST
#     self.netlist=netlist
#     self.inputs=re.findall(r"INPUT\((.*)\)\n",netlist)
#     self.outputs=re.findall(r"OUTPUT\((.*)\)\n",netlist)
    
#     self.wires=[]

#     self.gates={'BUF': 0,'NOT': 0, 'AND': 0, 'OR': 0, 'NAND': 0, 'NOR': 0,'XNOR':0,'XOR':0}

#     self.FFelements={'DFF':0}

#     self.gen_graph()  

#     self.wires.sort()
#     self.info()
    
#   def gen_graph(self,netlist=None):
#     if(netlist==None):
#       netlist=self.netlist

    # self.circuitgraph = nx.DiGraph()
    # for i in self.gates.keys():
    #   if i=='NOT' or i=='BUF':
    #     tmp=re.findall("(.*) = "+ i +"\((.*)\)\n?",netlist)
    #     for count,j in enumerate(tmp):
    #       #print(j)
    #       self.circuitgraph.add_edge(i+"_"+str(count),j[0].strip())
    #       self.circuitgraph.add_edge(j[1].strip(),i+"_"+str(count))
    #       for k in j:
    #         tmpk=k.strip()
    #         if( (tmpk not in self.inputs) and (tmpk not in self.outputs) and (tmpk not in self.wires) ):
    #           self.wires.append(tmpk)
    #           #print(k)
    #   else:
    #     tmp=re.findall("(.*) = "+ i +"\((.*),(.*)\)\n?",netlist)
    #     for count,j in enumerate(tmp):
    #       #print(j)
    #       self.circuitgraph.add_edge(i+"_"+str(count),j[0].strip())
    #       self.circuitgraph.add_edge(j[1].strip(),i+"_"+str(count))
    #       self.circuitgraph.add_edge(j[2].strip(),i+"_"+str(count))
    #       for k in j:
    #         tmpk=k.strip()
    #         if( (tmpk not in self.inputs) and (tmpk not in self.outputs) and (tmpk not in self.wires) ):
    #           self.wires.append(tmpk)
    #           #print(k)
    #   self.gates[i]+=len(tmp)

  
#   def info(self)->None:
#     self.gatecount=0
#     for i in self.gates.keys():
#       self.gatecount+=self.gates[i]

#     self.FFcount=0
#     for i in self.FFelements.keys():
#       self.FFcount+=self.FFelements[i]
#     print("Gate Nodes   = ",self.gates)
#     print("Total Gates  = ",self.gatecount)
#     print("Flip-Flop Elements",self.FFelements)
#     print("Total Flip-Flop Elements",self.FFcount)
#     print("Total Wires  = ",len(self.wires))
#     print("Input Nodes  = ",len(self.inputs))
#     print("Output Nodes = ",len(self.outputs))
#     print("Total Nodes  = ",int(self.circuitgraph.number_of_nodes()))
#     print("Gates + Wires + Inputs + Outputs = ",self.gatecount + len(self.wires) + len(self.inputs) + len(self.outputs))
  

#   def nodeio(self,Node)->None:
#     print("Node outputs = ",list(self.circuitgraph.successors(Node))) 
#     print("Node inputs = ",list(self.circuitgraph.predecessors(Node)))
  

#   def graph_to_bench(self,outpath:str)->None:
#     graphtonetlist=""
#     for i in self.inputnodes():
#       graphtonetlist+="INPUT("+i+")"+"\n"
#       #print("INPUT("+i+")")
    
#     for i in self.outputnodes():
#       #print("OUPUT("+i+")")
#       graphtonetlist+="OUTPUT("+i+")"+"\n"
#     for i in self.gatenodes().keys():
#       for j in range(self.gatenodes()[i]):
#         tmpj=i+"_"+str(j)
#         inp=list(self.circuitgraph.predecessors(tmpj))
#         out=list(self.circuitgraph.successors(tmpj))
#         if(i=="NOT" or i=='BUF'):
#           graphtonetlist+=out[0]+" = "+i+"("+inp[0]+")"+"\n"
#         else:
#           graphtonetlist+=out[0]+" = "+i+"("+inp[0]+","+inp[1]+")"+"\n"
#     print("Writing BENCH File to Location: ",outpath)
#     with open(outpath, 'w') as f:
#       f.write(graphtonetlist)


