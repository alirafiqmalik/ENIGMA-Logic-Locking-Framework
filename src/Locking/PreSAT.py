from src.Netlist.AST import *

class PreSAT:
    def __init__(self, module) -> None:
      self.module=module
      self.circuitgraph=module.circuitgraph

    
    def set_key(self,n , key=None):
      self.keycount=n
      if(key==None):
        self.keyint,self.bitkey=randKey(self.keycount)
      else:  
        self.keyint=key
        self.bitkey = format(key, "b")

      if (n > len(self.bitkey)):
          self.bitkey = format(self.keyint, "0"+str(n)+"b")
      elif (n < len(self.bitkey)):
          print("ERROR")
          print("Number of Gates < Number of Key-Bits")
          return None
      self.module.bitkey=self.bitkey+self.module.bitkey
      print("\t Key for PreSat locking Set")
      # print(self.module.bitkey)

    
    def InsertKeyGate(self, NodeA: str, NodeB: str, gatetype: str = 'XOR') -> None:
      keygatecount=len(self.module.lockingdata["gates"])
      
      keygate_name=f"keygate_{gatetype}_{str(keygatecount)}"
      self.circuitgraph.remove_edge(NodeA, NodeB)

      keywire_name="keywire"+str(len(self.module.io["wires"]))
      
      self.circuitgraph.add_node(keygate_name,type="gate",logic=gatetype)
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
      # print(NodeA,Na)
      if(Na['type']=='gate'):
        self.module.gates[Na['logic']][NodeA]['outputs']=keywire_name
      elif('DFF' in Na['type'].upper()):
        # print(Na,NodeA)
        self.module.FF_tech[Na['type']][NodeA]['outputs']=keywire_name
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
          if(i==(self.keycount-1)):
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
                    # print(self.bitkey[self.keycount-1],i,out,end="\n")
                    self.keycount-=1
                else:
                    self.InsertKeyGate(i, out, 'XOR')
                    # print(self.bitkey[self.keycount-1],i,out,end="\n")
                    self.keycount-=1
          current_layer = next_layer
          count+=1


    def SLL(self):

      tx=self.module.io['wires']

      locked=[]

      while(1):
        random_key = random.choice(list(tx.keys()))
        tp = tx[random_key]
        if((tp['bits']==1) and random_key not in locked ):
          break

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
        gatetype=random.choice(list(noninvlist.keys()))
        gates=gio[gatetype]
        gates_keys=list(gates.keys())
        # print(gates_keys)

        if(len(gates_keys)==0):
          raise Exception("Can Not Perform TRLL for this Circuit \n Keybits larger than number of gates") 

        gate=random.choice(gates_keys)
        gateio=gates[gate]
        invgatecount=len(invlist)

        self.module.circuitgraph.remove_edge(gate, gateio['outputs'])

        wire_name="new_inverter_wire"+str(len(self.module.io['wires']))
        invgate=f"NOT_inserted_{invgatecount}_"+str(random.randint(1,10000))

        
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
      # print(self.circuitgraph.nodes[inverter])
      
      self.circuitgraph.add_node(inverter,type="gate",logic=new_gatetype)
      self.circuitgraph.add_node(keygate_input_name,type="input",port="lockingkeyinput")

      self.circuitgraph.add_edge(keygate_input_name,inverter)
      self.circuitgraph.add_edge("module#"+self.module.module_name,keygate_input_name)

      # print(self.circuitgraph.nodes[inverter])

      gio=self.module.gates
      if(new_gatetype not in gio):
          gio[new_gatetype]={}  
      gio[new_gatetype][inverter]=gio["NOT"].pop(inverter)
      gio[new_gatetype][inverter]["inputs"].append(keygate_input_name)

      bit="0" if new_gatetype=="XOR" else "1"
      # self.module.bitkey=bit+self.module.bitkey
      self.module.lockingdata["inputs"].append((keygate_input_name,bit))
      
      if("lockingkeyinput" not in self.module.io['inputs']):
        self.module.io['inputs']["lockingkeyinput"]=connector(1,0,0)
        self.module.io["input_ports"]+="lockingkeyinput,"
      else:
        self.module.io['inputs']["lockingkeyinput"]=connector(bitval+1,0,bitval)


    def get_gates(self):# AllGates ← all_gates(C)
      # N onInvList ← get_noninverters(AllGates)
      gates=self.module.gates
      noninvlist={i:gates[i] for i in gates.keys() if i!="NOT"}
      # InvList ← get_inverters(AllGates)
      if("NOT" in gates.keys()):
        invlist=gates['NOT']
      else:
        gates["NOT"]={}
        invlist=gates["NOT"]

      return invlist,noninvlist



    def TRLL_Locking(self,split,invlist,noninvlist):
      # procedure Locking(C,K,split,InvList,NonInvList):

      #   for k in {0,split - 1} do
      #     gate ← choose_rand_gate(InvList)
      #     InvList ← InvList - {gate}
      #     if (RANDOM % 2) then
      #     replace_gate(gate,{XNOR},C)
      #     Key[k] ← 0
      #     else
      #     replace_gate(gate,{XOR},C)
      #     Key[k] ← 1
        
      #   for k in {split,K - 1} do
      #     gate ← choose_rand_gate(N onInvList)
      #     N onInvList ← N onInvList - {gate}
      #     if (RANDOM % 2) then
      #     insert_gate(gate,{XNOR},C)
      #     Key[k] ← 1
      #     else
      #     insert_gate(gate,{XOR},C)
      #     Key[k] ← 0
      #   return Key, C

      print("\t\t\t Replacing Inveters with Keygates")
      for i in range(0,split):
        rnd=self.bitkey[self.keycount-i-1]
        # rnd=random.randint(0,1)
        inv_keys=list(invlist.keys())
        
        if(len(inv_keys)==0):
          raise Exception("Can Not Perform TRLL for this Circuit \n Keybits larger than number of gates") 
        
        gate=random.choice(inv_keys)
        if(rnd=="1"):
          self.ReplaceInverter(inverter=gate,new_gatetype="XOR")
        else:
          self.ReplaceInverter(inverter=gate,new_gatetype="XNOR")

      print("\t\t\t Done Replacing Inveters with Keygates")
      print("\t\t\t Inserting Keygates")
      for i in range(split,self.keycount):
        rnd=self.bitkey[self.keycount-i-1]
        # rnd=random.randint(0,1)
        gate_type=random.choice(list(noninvlist.keys()))
        gates=noninvlist[gate_type]
        gate=random.choice(list(gates.keys()))
        gate_o=gates[gate]['outputs']
        # print("HERE  ",gate)
        
        if(rnd=="1"):
          self.InsertKeyGate(gate,gate_o,gatetype="XNOR")
          # self.ReplaceInverter(inverter=gate,new_gatetype="XNOR")
        else:
          self.InsertKeyGate(gate,gate_o,gatetype="XOR")
          # self.ReplaceInverter(inverter=gate,new_gatetype="XOR")
      print("\t\t\t Done Inserting Keygates")


    def TRLL_plus(self):
      print("\t Starting TRLL_plus Logic Locking")
      gatecount=0
      for i in self.module.gates:
        gatecount+=len(self.module.gates[i])
      
      # split ← RANDOM % K
      split=random.randint(0,self.keycount-1)
      
      invlist,noninvlist,=self.get_gates()
      # print(noninvlist)

      # num inv ← num(InvList)
      invgatecount=len(invlist)
      # print(invgatecount,split)

      # if num inv < split then
      #   ProduceInverters(C,N onInvList,split-num_inv)
      if(invgatecount<split):
        # print(invgatecount,split)
        print("\t\t Inserting Inverters")
        self.InsertInverters(noninvlist,invlist,split-invgatecount)
        print("\t\t Done Inserting Inverters")
      
      # invlist,noninvlist,=get_gates(obj.top_module.gates)
      
      self.TRLL_Locking(split,invlist,noninvlist)
      print("\t Done TRLL_plus Logic Locking")
      

    def InsertMUX(self, NodeA: str, NodeB: str, NodeC: str, gatetype: str = 'MUX') -> None:
      keygatecount=len(self.module.lockingdata["gates"])
      
      keygate_name=f"keygate_{gatetype}_{str(keygatecount)}"
      self.circuitgraph.remove_edge(NodeA, NodeB)
      
      keywire_name="keywire"+str(len(self.module.io["wires"]))
      
      self.circuitgraph.add_node(keygate_name,type="gate",logic=gatetype)
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
      # print(NodeA,Na)
      if(Na['type']=='gate'):
        self.module.gates[Na['logic']][NodeA]['outputs']=keywire_name
      elif('DFF' in Na['type']):
        # print(Na,NodeA)
        self.module.FF_tech[Na['type']][NodeA]['outputs']=keywire_name
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