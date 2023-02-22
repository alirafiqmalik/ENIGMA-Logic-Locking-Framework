from src.AST import *

class PreSAT:
    def __init__(self, module) -> None:
      self.module=module
      self.circuitgraph=module.circuitgraph

    
    def set_key(self,n , key=None):
      self.nbits=n
      if(key==None):
        self.keyint,self.bitkey=randKey(self.nbits)
      else:  
        self.keyint=key
        self.bitkey = format(key, "b")

      # print(2**n, "<----->", self.keyint, "<----->", (2**n) >= self.keyint)
      if (n > len(self.bitkey)):
          self.bitkey = format(self.keyint, "0"+str(n)+"b")
      elif (n < len(self.bitkey)):
          print("ERROR")
          print("Number of Gates < Number of Key-Bits")
          return None
      # else:
      # print("n == Bits")

      # print("######################################", end="\n          ")
      # print(self.keyint, " ----------> ", self.bitkey)
      print(self.bitkey)
      self.module.bitkey=self.bitkey
      # print("######################################")

    
    
    def InsertKeyGate(self, NodeA: str, NodeB: str, gatetype: str = 'XOR') -> None:
      keygatecount=len(self.module.lockingdata["gates"])
      
      keygate_name=f"keygate_{gatetype}_{str(keygatecount)}"
      self.circuitgraph.remove_edge(NodeA, NodeB)

      keywire_name="keywire"+str(len(self.module.io["wires"]))
      
      # self.circuitgraph.add_node(keywire_name,)
      self.circuitgraph.add_node(keywire_name,type="wire",port=keywire_name)
      
      self.circuitgraph.add_edge(NodeA, keywire_name)
      self.circuitgraph.add_edge(keywire_name, keygate_name)
      self.circuitgraph.add_edge(keygate_name, NodeB)

      bitval=len(self.module.lockingdata['inputs'])
      # print(bitval)
      keygate_input_name=f"lockingkeyinput[{bitval}]"
      self.circuitgraph.add_node(keygate_input_name,type="input",port="lockingkeyinput")
      self.circuitgraph.add_edge(keygate_input_name, keygate_name)

      self.circuitgraph.add_edge("module#"+self.module.module_name,keygate_input_name)
      # print(self.module.self.module_name)


      self.module.lockingdata["gates"].append(keygate_name)
      bit="0" if gatetype=="XOR" else "1"
      self.module.lockingdata["inputs"].append((keygate_input_name,bit))
      self.module.lockingdata["wires"].append(keywire_name)

      self.module.io['wires'][keywire_name]=connector(1,0,0)
      
      
      if("lockingkeyinput" not in self.module.io['inputs']):
        self.module.io['inputs']["lockingkeyinput"]=connector(1,0,0)
        self.module.io["input_ports"]+="lockingkeyinput,"
      else:
        # bits=self.module.io['inputs'][keygate_input_name]["bits"]
        self.module.io['inputs']["lockingkeyinput"]=connector(bitval+1,0,bitval)
        # self.module.io["input_ports"]+=f"{keygate_input_name},"

      # print(NodeA)
      Na=self.circuitgraph.nodes[NodeA]
      # Nb=self.circuitgraph.nodes[NodeB]
      if(Na['type']=='gate'):
        self.module.gates[Na['logic']][NodeA]['outputs']=keywire_name
        # self.module.gates[Na['logic']][NodeA]=keywire_name
      else:
        raise Exception("NOT A GATE WHYYYYYY???????????")
      
      # if(Nb['type']=='wire'):
      #   self.module.gates[Na['logic']]['output']=keywire_name
      # else:
      #   raise Exception("NOT A GATE WHYYYYYY")

      # print(NodeA,self.circuitgraph.nodes[NodeA])
      # print(NodeB,self.circuitgraph.nodes[NodeB])

      if(gatetype not in self.module.gates.keys()):
        self.module.gates[gatetype]={}
        
      self.module.gates[gatetype][keygate_name]={"inputs": [keywire_name,keygate_input_name] ,"outputs": NodeB}
      # else:
      #     self.module.gates[gatetype]={}
      #     self.module.gates[gatetype][keygate_name]={"inputs": [keywire_name,keygate_input_name] ,"outputs": NodeB}

      # if("self.module#" in NodeA):
      #   print(self.circuitgraph.nodes[NodeA])
      #   # print("A",self.module.linkages[NodeA.split("#")[-1]])
      # elif("self.module#" in NodeB):
      #   print(self.circuitgraph.nodes[NodeB])
      #   # print("A",self.module.linkages[NodeB.split("#")[-1]])
      # else:
      #   pass

    def RLL(self):
      random.seed(10)
      i=-1
      while(1):
          if(i==(self.nbits-1)):
              break  
          tmp=list(self.module.io['wires'].keys())
          tp = random.randint(0, len(tmp)-1)
          if(self.module.io['wires'][tmp[tp]]["bits"]==1):
            inp = list(self.circuitgraph.predecessors(tmp[tp]))
            if(len(inp)==0):
              pass
            elif (inp[0] in self.module.lockingdata["gates"]):
              pass
            elif (self.bitkey[-(i+1)] == '1'):
                self.InsertKeyGate(inp[0], tmp[tp], 'XNOR')
                i+=1
            else:
                self.InsertKeyGate(inp[0], tmp[tp], 'XOR')
                i+=1


    def LayerTraversal(self,sources,mode="f"):
      G=self.circuitgraph
      if(mode=='f'):
        check=lambda x: list(G.successors(x))
      elif(mode=='r'):
        check=lambda x: list(G.predecessors(x))
      else:
        raise Exception("ERROR INVALID MODE, SET mode to 'f' or 'b' ")

      if(type(sources)==list):
        current_layer = sources
      else:
        current_layer=[sources]
      visited = set(sources)

      for source in current_layer:
        if source not in G:
            raise nx.NetworkXError(f"The node {source} is not in the graph.")   
      count=1
      while current_layer:
          next_layer = list()
          for node in current_layer:
              for child in check(node):
                  if child not in visited:
                      visited.add(child)
                      next_layer.append(child)
          if(~count%2):
              # print(current_layer)
              # print("_____________________________")
              for i in current_layer:
                if("module#" in i):
                  continue
                if(self.keycount==0):
                  break 
              
                out=list(G.successors(i))[0]
                # print(i,out,end="\n")
                # print(out in self.module.lockingdata["wires"],self.module.lockingdata["wires"])
                if(i in self.module.lockingdata["gates"]):
                  pass
                elif(self.bitkey[self.keycount-1]=='1'):
                    self.InsertKeyGate(i, out, 'XNOR')
                    print(self.bitkey[self.keycount-1],i,out,end="\n")
                    self.keycount-=1
                else:
                    self.InsertKeyGate(i, out, 'XOR')
                    print(self.bitkey[self.keycount-1],i,out,end="\n")
                    self.keycount-=1
          current_layer = next_layer
          count+=1
          # 


    def SLL(self):
      self.keycount=self.nbits
      tx=self.module.io['wires']

      locked=[]

      while(1):
        random_key = random.choice(list(tx.keys()))
        tp = tx[random_key]
        if((tp['bits']==1) and random_key not in locked ):
          break

      self.keycount=self.nbits
      while(1):
        self.LayerTraversal(random_key,mode="f")
        if(self.keycount==0):
          locked.append(random_key)
          break
        self.LayerTraversal(random_key,mode="r")
        # print(self.keycount)
        if(self.keycount==0):
          locked.append(random_key)
          break

    
    def InsertInverters(self,noninvlist,invlist,s):
      for _ in range(s):
        gio=self.module.gates
        gatetype=random.choice(noninvlist)
        # print(gatetype,gates[gatetype])
        gates=gio[gatetype]


        gate=random.choice(list(gates.keys()))
        gateio=gates[gate]
        invgatecount=len(invlist)

        self.module.circuitgraph.remove_edge(gate, gateio['outputs'])

        wire_name="new_inverter_wire"+str(len(self.module.io['wires']))
        invgate=f"NOT_inserted_{invgatecount}_"

        
        new_gatetype=invert_gate(gatetype)
        self.circuitgraph.add_node(gate,type="gate",logic=new_gatetype)
        self.circuitgraph.add_node(wire_name,type="wire",port=wire_name)
        self.circuitgraph.add_node(invgate,type="gate",logic="NOT")
        
        
        
        self.circuitgraph.add_edge(gate, wire_name)
        self.circuitgraph.add_edge(wire_name,invgate)
        self.circuitgraph.add_edge(invgate,gateio['outputs'])
        


        
        if(new_gatetype not in gio):
          gio[new_gatetype]={}  
        gio[new_gatetype][gate]=gio[gatetype].pop(gate)

        
        gio["NOT"][invgate]={'inputs':[wire_name],"outputs":gateio['outputs']}
        self.module.io['wires'][wire_name]=connector(1,0,0)
        gateio['outputs']=wire_name
        





    def ReplaceInverter(self,inverter,new_gatetype="XOR"):
      bitval=len(self.module.lockingdata['inputs'])
      keygate_input_name=f"lockingkeyinput[{bitval}]"
      print(self.circuitgraph.node[inverter])
      self.circuitgraph.add_node(keygate_input_name,type="input",port="lockingkeyinput")

      self.circuitgraph.add_edge(keygate_input_name,inverter)
      self.circuitgraph[inverter]['type']=new_gatetype

      print(self.circuitgraph.node[inverter])

      gio=self.module.gates
      if(new_gatetype not in gio):
          gio[new_gatetype]={}  
      gio[new_gatetype][inverter]=gio["NOT"].pop(inverter)
      gio[new_gatetype][inverter]["inputs"].append(keygate_input_name)

      bit="0" if new_gatetype=="XOR" else "1"
      self.module.lockingdata["inputs"].append((keygate_input_name,bit))
      

      
      if("lockingkeyinput" not in self.module.io['inputs']):
        self.module.io['inputs']["lockingkeyinput"]=connector(1,0,0)
        self.module.io["input_ports"]+="lockingkeyinput,"
      else:
        self.module.io['inputs']["lockingkeyinput"]=connector(bitval+1,0,bitval)







      # print(self.module.gates.keys())

      # print(inverter,gateio)
      
      # self.circuitgraph.remove_node(inverter)

      
      # self.circuitgraph.add_edge(inverter, gateio['outputs'])

      # self.circuitgraph.remove_node(inverter)



      new_gatetype="XOR"


      # self.circuitgraph.add_node(gate,type="gate",logic=new_gatetype)
      # self.circuitgraph.add_node(wire_name,type="wire",port=wire_name)
      # self.circuitgraph.add_node(invgate,type="gate",logic="NOT")
      
      
      
      # self.circuitgraph.add_edge(gate, wire_name)
      # self.circuitgraph.add_edge(wire_name,invgate)
      # self.circuitgraph.add_edge(invgate,gateio['outputs'])
      


      
      # if(new_gatetype not in gio):
      #   gio[new_gatetype]={}  
      # gio[new_gatetype][gate]=gio[gatetype].pop(gate)

      
      # gio["NOT"][invgate]={'inputs':[wire_name],"outputs":gateio['outputs']}
      # self.module.io['wires'][wire_name]=connector(1,0,0)
      # gateio['outputs']=wire_name

