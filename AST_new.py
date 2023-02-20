import src.utils as utils
import src.verification as ver
from src.AST import AST
from src.PreSAT import LogicLocking
import networkx as nx



obj=AST(file_path="./input_files/tmporg.v",rw="w",flag="v",top="locked",filename="locked_new")
obj = AST(file_path="./output_files/locked_new.json",rw='r',top="locked",filename="locked") # r for read from file
# obj.save_module_connections()


LL=LogicLocking(obj.top_module)

LL.set_key(10,323)
LL.SLL()

obj.top_module.save_graph()
obj.writeLLFile()



cir,testbench=ver.gen_miterCircuit(obj.gate_level_flattened,obj.LLverilog)

with open("./tmp/top.v","w") as f:
  f.write(cir)

with open("./tmp/testbench.v","w") as f:
  f.write(testbench)

with open("/home/alira/FYP_FINAL/tmpll.v","w") as f:
  f.write(cir)



path="/home/alira/FYP_FINAL/tmpll.v"
top="top"

utils.verify_verilog(path,top)








# ~/FYP/linux/yosys/build/yosys -q -p'
# read_verilog /home/alira/FYP_FINAL/tmpll.v
# hierarchy -check -top locked
# '




# while(LL.keycount!=0):
  # tmp=update()
  # print(tmp)
  # LL.LayerTraversal([tmp],mode="f")
  # print(LL.keycount)
  # tmp=update()
  # LL.LayerTraversal([tmp],mode="r")
#   print(LL.keycount)
#   # if(LL.keycount==0):
#   #   break
#   # LL.LayerTraversal([tmp[tp]],mode="r")


# G=obj.modules['sarlock'].circuitgraph
# LayerTraversal(G,["lock_out"],mode='f')
# print("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n")
# LayerTraversal(G,["lock_out"])















































































































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


