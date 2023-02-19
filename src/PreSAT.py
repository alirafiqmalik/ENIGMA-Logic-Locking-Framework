from src.AST import *

class LogicLocking:
    def __init__(self, module) -> None:
      self.module=module
      self.circuitgraph=module.circuitgraph

    def InsertKeyGate(self, NodeA: str, NodeB: str, gatetype: str = 'XOR') -> None:
      keygatecount=len(self.module.lockingdata["gates"])
      
      keygate_name=f"keygate_{gatetype}_{str(keygatecount)}"
      self.circuitgraph.remove_edge(NodeA, NodeB)

      keywire_name="keywire"+str(len(self.module.io["wires"]))
      
      # self.circuitgraph.add_node(keywire_name,)
      
      self.circuitgraph.add_edge(NodeA, keywire_name)
      self.circuitgraph.add_edge(keywire_name, keygate_name)
      self.circuitgraph.add_edge(keygate_name, NodeB)

      keygate_input_name="lockingkeyinput"+str(len(self.module.lockingdata["inputs"]))
      self.circuitgraph.add_edge(keygate_input_name, keygate_name)

      self.circuitgraph.add_edge("module#"+self.module.module_name,keygate_input_name)
      # print(self.module.self.module_name)


      self.module.lockingdata["gates"].append(keygate_name)
      self.module.lockingdata["inputs"].append(keygate_input_name)
      self.module.lockingdata["wires"].append(keywire_name)

      self.module.io['wires'][keywire_name]=connector(1,0,0)
      self.module.io['inputs'][keygate_input_name]=connector(1,0,0)
      self.module.io["input_ports"]+=f"{keygate_input_name},"

      # print(NodeA)
      # print(NodeA,self.circuitgraph.nodes[NodeA])
      # print(NodeB,self.circuitgraph.nodes[NodeB])

      if(gatetype in self.module.gates.keys()):
          self.module.gates[gatetype].append({"init_name": keygate_name,"inputs": [keywire_name,keygate_input_name] ,"outputs": NodeB})
      else:
          self.module.gates[gatetype]=[{"init_name": keygate_name,"inputs": [keywire_name,keygate_input_name] ,"outputs": NodeB}]

      # if("self.module#" in NodeA):
      #   print(self.circuitgraph.nodes[NodeA])
      #   # print("A",self.module.linkages[NodeA.split("#")[-1]])
      # elif("self.module#" in NodeB):
      #   print(self.circuitgraph.nodes[NodeB])
      #   # print("A",self.module.linkages[NodeB.split("#")[-1]])
      # else:
      #   pass


    def RLL(self, n: int, key: int):
      bitkey = format(key, "b")
      print(2**n, "<----->", key, "<----->", (2**n) >= key)
      if (n > len(bitkey)):
          bitkey = format(key, "0"+str(n)+"b")
      elif (n < len(bitkey)):
          print("ERROR")
          print("Number of Gates < Number of Key-Bits")
          return None
      # else:
      print("n == Bits")

      print("######################################", end="\n          ")
      print(key, " ----------> ", bitkey)
      print("######################################")

      random.seed(10)
      i=-1
      while(1):
          if(i==(n-1)):
              break
          else:
              i+=1
          
          tmp=list(self.module.io['wires'].keys())
          tp = random.randint(0, len(tmp)-1)
          if(self.module.io['wires'][tmp[tp]]["bits"]==1):
            inp = list(self.circuitgraph.predecessors(tmp[tp]))
            if (bitkey[-(i+1)] == '1'):
                self.InsertKeyGate(inp[0], tmp[tp], 'XNOR')
            elif(len(inp)==0):
                pass
            else:
                self.InsertKeyGate(inp[0], tmp[tp], 'XOR')