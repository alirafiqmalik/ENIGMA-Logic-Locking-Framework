from src.AST import AST
import networkx as nx
import pickle
import base64
import json
import re

from src.utils import connector





# if __name__=="__main__":

# obj=AST(file_path="./input_files/tmporg.v",rw="w",flag="v",top="locked",filename="locked_new")
obj = AST(file_path="./output_files/locked_new.json",rw='r',top="locked",filename="locked") # r for read from file
# obj.save_module_connections()





obj.modules['sarlock'].save_graph()



# obj.modules['sarlock'].circuirgraph


keygates={"XNOR":[]}

# gate_tech[re.sub("_g","",type)]=[{"init_name": init,"inputs": tmpx[1:] ,"outputs": tmpx[0]}]
def InsertKeyGate(tmpselfmodule, NodeA: str, NodeB: str, gatetype: str = 'XOR') -> None:
  keygatecount=len(tmpselfmodule.lockingdata["gates"])
  
  keygate_name=f"keygate_{gatetype}_{str(keygatecount)}"
  keygate = f"{gatetype}#{keygate_name}"
  tmpselfmodule.circuitgraph.remove_edge(NodeA, NodeB)

  keywire_name="keywire"+str(len(tmpselfmodule.io["wires"]))
  keywire = f"wire#{keywire_name}"
  
  tmpselfmodule.circuitgraph.add_node(keywire,)
  
  tmpselfmodule.circuitgraph.add_edge(NodeA, keywire)
  tmpselfmodule.circuitgraph.add_edge(keywire, keygate)
  tmpselfmodule.circuitgraph.add_edge(keygate, NodeB)

  keygate_input_name="lockingkeyinput"+str(len(tmpselfmodule.lockingdata["inputs"]))
  tmpselfmodule.circuitgraph.add_edge("input#"+keygate_input_name, keygate)


  tmpselfmodule.lockingdata["gates"].append(keygate_name)
  tmpselfmodule.lockingdata["inputs"].append(keygate_input_name)
  tmpselfmodule.lockingdata["wires"].append(keywire_name)

  tmpselfmodule.io['wires'][keywire_name]=connector(1,0,0)

  tmpselfmodule.io['inputs'][keygate_input_name]=connector(1,0,0)

  print(NodeA)

  if(gatetype in tmpselfmodule.gates.keys()):
    tmpselfmodule.gates[gatetype].append({"init_name": keygate_name,"inputs": [keywire_name,NodeB] ,"outputs": NodeB})
  else:
    tmpselfmodule.gates[gatetype]=[{"init_name": keygate_name,"inputs": [keywire_name,NodeB] ,"outputs": NodeB}]




InsertKeyGate(obj.modules['sarlock'],"module#c","wire#ckt_out[1]")


obj.modules['sarlock'].save_graph()


obj.writeLLFile()

def test(self):
    def InsertKeyGate(self, NodeA: str, NodeB: str, gatetype: str = 'XOR') -> None:
        keygatecount = self.gates[gatetype]
        keygate = gatetype+"_"+str(keygatecount)
        self.circuitgraph.remove_edge(NodeA, NodeB)

        # keywire = "KEY"+str(len(self.wires))
        keywire = "keywire"+str(len(self.wires))

        self.circuitgraph.add_edge(NodeA, keywire)
        self.circuitgraph.add_edge(keywire, keygate)
        self.circuitgraph.add_edge(keygate, NodeB)

        # self.circuitgraph.add_edge("KEY["+str(self.keygatescount)+"]", keygate)
        # self.inputs.append("KEY["+str(self.keygatescount)+"]")

        self.circuitgraph.add_edge("keyinput_"+str(self.keygatescount), keygate)
        self.inputs.append("keyinput_"+str(self.keygatescount))

        self.wires.append(keywire)

        self.gates[gatetype] += 1
        self.gatecount += 1

        self.keygates[gatetype] += 1
        self.keygatescount += 1







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


