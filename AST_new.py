from src.AST import AST
import networkx as nx
import pickle
import base64
import json
import re

from src.utils import connector





# if __name__=="__main__":

# obj=AST(file_path="./input_files/tmporg.v",rw="w",flag="v",top="locked",filename="new")
obj = AST(file_path="./output_files/locked_new.json",rw='r',top="locked") # r for read from file


# print(obj.top_module.circuitgraph)

module=obj.submodule["sarlock"]

module.save_graph()


# def process_node(R):
#   if(":" in R):
#     node,endbit,startbit=re.findall("(.*)\[(\d+):?(\d*)\]",R)[0]
#     endbit,startbit=int(endbit),int(startbit)
#   elif("[" in R):
#     node,bit=re.findall("(.*)\[(\d+)\]",R)[0]
#     endbit,startbit=int(bit),int(bit)
#   else:
#     node=R
#     print("NODE  ",node)
#     if(R in module.io['inputs']):
#       endbit=module.io['inputs'][node]['endbit']
#       startbit=module.io['inputs'][node]['startbit']
#     elif(R in module.io['outputs']):
#       endbit=module.io['outputs'][node]['endbit']
#       startbit=module.io['outputs'][node]['startbit']
#     elif(R in module.io['wires']):
#       endbit=module.io['wires'][node]['endbit']
#       startbit=module.io['wires'][node]['startbit']
#     else:
#       raise Exception("NODE NOT FOUND")
#   return node,endbit,startbit





def process_node(R):
  if(":" in R):
    node,endbit,startbit=re.findall("(.*)\[(\d+):?(\d*)\]",R)[0]
    endbit,startbit=int(endbit),int(startbit)
  elif("[" in R):
    node,bit=re.findall("(.*)\[(\d+)\]",R)[0]
    endbit,startbit=int(bit),int(bit)
  else:
    node=R
    endbit,startbit=None,None

  if(node in module.io['inputs']):
    Node=module.io['inputs'][node]
    type='inputs'
  elif(R in module.io['outputs']):
    Node=module.io['outputs'][node]
    type='outputs'
  elif(R in module.io['wires']):
    Node=module.io['wires'][node]
    type='wires'
  else:
    raise Exception("NODE NOT FOUND")

  if(endbit==None):
    endbit=Node['endbit']
    startbit=Node['startbit']

  return node,type,endbit,startbit




for i in module.linkages:
  # print(i['init_name'],i)
  module_node_name="module#"+i['init_name']
  module.circuitgraph.add_node(module_node_name, type="module",module_name=i['module_name'],init_name=i['init_name'])
  for j in i['links']:
    L,R=j
    print(L,process_node(R))
    node,type,endbit,startbit=process_node(R)
    


    if(L in obj.submodule[i['module_name']].io['inputs']):
      pass
      # print(node,endbit,startbit)
      for k in range(startbit,endbit+1):
        module.circuitgraph.add_edge(module_node_name,f"{type}#"+node+f"[{k}]")
        # module.circuitgraph.add_edge("input#"+node+f"[{k}]",module_node_name)
    elif(L in obj.submodule[i['module_name']].io['outputs']):
      for k in range(startbit,endbit+1):
        module.circuitgraph.add_edge(f"{type}#"+node+f"[{k}]",module_node_name)
    else:
      raise Exception("NODE NOT FOUND")
    



    # if(node in module.io['inputs']):
    #   pass
    # elif(node in module.io['outputs']):
    #   pass
    # elif(node in module.io['wires']):
      # if(L in module.io['inputs']):
      #   pass
      # elif(L in module.io['outputs']):
      #   pass
      # else:
      #   pass
    # else:
    #   raise Exception("NODE NOT FOUND")




    # if(node in module.io['inputs']):
    #   # if(module.io['inputs'][node]['bits']):
      # for k in range(start,end+1):
      #   module.circuitgraph.add_edge("input#"+node+f"[{k}]",module_node_name)
    # elif(node in module.io['outputs']):
    #   for k in range(start,end+1):
    #     module.circuitgraph.add_edge(module_node_name,"output#"+node+f"[{k}]")
    # elif(node in module.io['wires']):
    #   if(L in module.io['inputs']):
    #     print("INPUT ",L,R,module.io['inputs'][node])
    #     # for k in range(start,end+1):
    #     # module.circuitgraph.add_edge(module_node_name,"output#"+node+f"[{k}]")
    #   elif(L in module.io['outputs']):
    #     print("OUTPUT ",L,R,module.io['outputs'][node])
    #   else:
    #     pass
    # else:
    #   raise Exception("NODE NOT FOUND")
      


    # if L in obj.submodule[i['module_name']].io['inputs'].keys():
    #   # module.circuitgraph.add_edge("input#"+x,"module#"+i['module_name']) for x in node_bus
    #   print("IF ",L,R)
    # elif L in obj.submodule[i['module_name']].io['outputs'].keys():
    #   pass
    # elif L in obj.submodule[i['module_name']].io['wires'].keys():
    #   pass
    # else:
    #   raise Exception("NODE NOT FOUND")



    # if(re.sub("\[\d+:?\d*\]","",R) in module.io['inputs']):
    #   print("INPUT ",L,R,module.io['inputs'][re.sub("\[\d+:?\d*\]","",R)])
      
    # elif(re.sub("\[\d+:?\d*\]","",R) in module.io['outputs']):
    #   print("OUTPUT ",L,R,module.io['outputs'][re.sub("\[\d+:?\d*\]","",R)])
    # elif(re.sub("\[\d+:?\d*\]","",R) in module.io['wires']):
    #   print("wire ",L,R,module.io['wires'][re.sub("\[\d+:?\d*\]","",R)])
    # else:
    #   raise Exception("NODE NOT FOUND")


def t(self):
  LLverilog=""
  LLverilog+=self.top_module.gate_level_verilog+"\n"
  for i in self.submodule:
    LLverilog+=self.submodule[i].gate_level_verilog+"\n"
  return LLverilog


LLverilog=t(obj)
# print(LLverilog)




# obj.update_LLverilog()

module.save_graph()


# for i in obj.submodule:
#   print(obj.submodule[i].circuitgraph)

# obj.submodule["ckt"].save_graph()






# print( module.io["inputs"])
# # print(module.linkages)
# print(module.io["input_ports"])

# for i in module.linkages:
#     module_name=i["module_name"]
#     init_name=i["init_name"]
#     # print(i,i["linkages"]) 
#     # print(module.io)
#     # print(obj.submodule[module_name].io)
#     self.circuitgraph.add_node("module#"+module_name, type="module",init_name=init_name)
#     for j in i["links"]:
#       # print("HERE",j[0],j[1])
#       if(":" in j[1]):
#           bus_node_name,endbit,startbit=re.findall("(.*)\[(.*):(.*)\]",j[1])[0]
#           # print(bus_node_name,startbit,endbit)
#           # print(bus_node_name in module.io['inputs'])
#           # print(obj.submodule[module_name].io)
#           # print(j[0] in obj.submodule[module_name].io["input_ports"])
#       #     if(j[0] in obj.submodule[module_name].io["input_ports"]):
#       #         for k in range(int(startbit),int(endbit)+1):
#       #             module_node=bus_node_name+f"[{k}]"
#       #             link_node=j[0]+f"[{k}]"
#       #             # print(j[0]+f"[{k}]",bus_node_name+f"[{k}]")
#       #             self.circuitgraph.add_edge("module#"+module.module_name,module_node) 
#       #     elif(j[0] in obj.submodule[module_name].io["output_ports"]):
#       #         for k in range(int(startbit),int(endbit)+1):
#       #             module_node=bus_node_name+f"[{k}]"
#       #             link_node=j[0]+f"[{k}]"
#       #             # print(j[0]+f"[{k}]",bus_node_name+f"[{k}]")
#       #             # self.circuitgraph.add_edge("module#"+module.module_name,module_node) 
#       #     else:
#       #         print("EXCEPTION")
#       #         raise Exception(f"{bus_node_name} not found in ")








# print(module.module_LLverilog)
# print(module.module_LLself.circuitgraph)






























































































































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


