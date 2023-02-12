from src.AST import AST
import networkx as nx
import pickle
import base64
import json
import re







# if __name__=="__main__":

# obj=AST("./input_files/tmporg.v",rw="w",flag="v",top="locked")
obj = AST("./output_files/locked.json",rw='r',top="locked") # r for read from file

# print(obj.submodule)

module=obj.submodule["sarlock"]

# print(module.module_name)
# print(module.io["inputs"])
# print(module.io["outputs"])
# print(module.gates)
# print(module.linkages)


def nodeio(circuitgraph,Node):
    print("Node outputs = ",list(circuitgraph.successors(Node))) 
    print("Node inputs = ",list(circuitgraph.predecessors(Node)))

circuitgraph = nx.DiGraph()



# circuitgraph.add_node("output#"+node_output, type="output")

# print(module.linkages)

# for i in module.linkages:
#     tmpi=module.linkages[i]
#     init_name="init#"+i
#     print(tmpi["module_name"])
#     print(tmpi["linkages"])



wire=[]
for init_name in module.gates:
    tmpi=module.gates[init_name]
    logic_gate=tmpi["type"]
    node_input=tmpi["inputs"]
    node_output=tmpi["outputs"]
    node_name=logic_gate+"#"+init_name


    circuitgraph.add_node(node_name, type="gate",logic=logic_gate)

    if(node_output in module.io["outputs"]):
        circuitgraph.add_node("output#"+node_output, type="output")
        circuitgraph.add_edge(node_name, "output#"+node_output)
    else:
        wire.append(node_output)
        circuitgraph.add_node("wire#"+node_output, type="wire")
        circuitgraph.add_edge(node_name, "wire#"+node_output)

    for i in node_input:
        if(re.sub("\[.*\]","",i) in module.io["inputs"]):
            circuitgraph.add_node("input#"+i, type="input")
            circuitgraph.add_edge("input#"+i,node_name)
        else:
            wire.append(i)
            circuitgraph.add_node("wire#"+i, type="wire")
            circuitgraph.add_edge("wire#"+i,node_name)


circuitgraph.add_node("module#"+module.module_name, type="module")
for i in module.io["outputs"]:
    tmpi=module.io["outputs"][i]
    if(tmpi['bits']==1):
        circuitgraph.add_edge("output#"+i,"module#"+module.module_name)
    else:
        for k in range(tmpi['endbit'],tmpi["startbit"]+1):
            # print("output#"+i+f"[{k}]")
            circuitgraph.add_edge("output#"+i+f"[{k}]","module#"+module.module_name)

for i in module.io["inputs"]:
    tmpi=module.io["inputs"][i]
    if(tmpi['bits']==1):
        circuitgraph.add_edge("module#"+module.module_name,"input#"+i)
    else:
        for k in range(tmpi['endbit'],tmpi["startbit"]+1):
            # print("input#"+i+f"[{k}]")
            circuitgraph.add_edge("module#"+module.module_name,"input#"+i+f"[{k}]")




# print( module.io["inputs"])
# # print(module.linkages)
# print(module.io["input_ports"])

for i in module.linkages:
    module_name=i["module_name"]
    init_name=i["init_name"]
    # print(i,i["linkages"]) 
    circuitgraph.add_node("module#"+module_name, type="module",init_name=init_name)
    for j in i["links"]:
      print(j[0],j[1])
        # if("[" in j[1]):
        #     bus_node_name,endbit,startbit=re.findall("(.*)\[(.*):(.*)\]",j[1])[0]
        #     # print(bus_node_name,startbit,endbit)
        #     # print(obj.submodule[module_name].io)
        #     # print(j[0] in obj.submodule[module_name].io["input_ports"])
        #     if(j[0] in obj.submodule[module_name].io["input_ports"]):
        #         for k in range(int(startbit),int(endbit)+1):
        #             module_node=bus_node_name+f"[{k}]"
        #             link_node=j[0]+f"[{k}]"
        #             # print(j[0]+f"[{k}]",bus_node_name+f"[{k}]")
        #             circuitgraph.add_edge("module#"+module.module_name,module_node) 
        #     elif(j[0] in obj.submodule[module_name].io["output_ports"]):
        #         for k in range(int(startbit),int(endbit)+1):
        #             module_node=bus_node_name+f"[{k}]"
        #             link_node=j[0]+f"[{k}]"
        #             # print(j[0]+f"[{k}]",bus_node_name+f"[{k}]")
        #             # circuitgraph.add_edge("module#"+module.module_name,module_node) 
        #     else:
        #         print("EXCEPTION")
        #         raise Exception(f"{bus_node_name} not found in ")








nx.drawing.nx_agraph.write_dot(circuitgraph, "./tmp/tmp.dot")

import subprocess
subprocess.run("dot -Tsvg ./tmp/tmp.dot > ./tmp/tmp.svg", shell=True)

# print(module.module_LLverilog)
# print(module.module_LLcircuitgraph)



















class Netlist():
  def __init__(self,module):
    module.io
  
  
  def gen_graph(self,netlist=None):
    self.circuitgraph = nx.DiGraph()
    for i in self.gates.keys():
      if i=='NOT' or i=='BUF':
        tmp=re.findall("(.*) = "+ i +"\((.*)\)\n?",netlist)
        for count,j in enumerate(tmp):
          #print(j)
          self.circuitgraph.add_edge(i+"_"+str(count),j[0].strip())
          self.circuitgraph.add_edge(j[1].strip(),i+"_"+str(count))
          for k in j:
            tmpk=k.strip()
            if( (tmpk not in self.inputs) and (tmpk not in self.outputs) and (tmpk not in self.wires) ):
              self.wires.append(tmpk)
              #print(k)
      else:
        tmp=re.findall("(.*) = "+ i +"\((.*),(.*)\)\n?",netlist)
        for count,j in enumerate(tmp):
          #print(j)
          self.circuitgraph.add_edge(i+"_"+str(count),j[0].strip())
          self.circuitgraph.add_edge(j[1].strip(),i+"_"+str(count))
          self.circuitgraph.add_edge(j[2].strip(),i+"_"+str(count))
          for k in j:
            tmpk=k.strip()
            if( (tmpk not in self.inputs) and (tmpk not in self.outputs) and (tmpk not in self.wires) ):
              self.wires.append(tmpk)
              #print(k)
      self.gates[i]+=len(tmp)











































































































#obj=AST("./input_files/tmporg.v",rw="w",flag="v")
# tmp=open("tmp/tmp_syn2dont_flatten.v").read()
# print(format_verilog(tmp,remove_wire=True))



# print(obj.top_module.gates)
# print(list(obj.top_module.linkages.keys())[0])
# print()

# for i in obj.submodule:
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


