# Deprecated
import networkx as nx
import re
from node import Node
import attacks.satattack.circuit as circuit
import src.utils as utils


class Netlist():
  def __init__(self,netlist:str)->None:#mode:str="graph"
    self.netlist=netlist
    self.inputs=re.findall(r"INPUT\((.*)\)\n",netlist)
    self.outputs=re.findall(r"OUTPUT\((.*)\)\n",netlist)
    
    self.wires=[]

    self.gates={'BUF': 0,'NOT': 0, 'AND': 0, 'OR': 0, 'NAND': 0, 'NOR': 0,'XNOR':0,'XOR':0}

    self.FFelements={'DFF':0}

    self.gen_graph()  

    self.wires.sort()
    self.info()
    
  def gen_graph(self,netlist=None):
    if(netlist==None):
      netlist=self.netlist

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

  
  def info(self)->None:
    self.gatecount=0
    for i in self.gates.keys():
      self.gatecount+=self.gates[i]

    self.FFcount=0
    for i in self.FFelements.keys():
      self.FFcount+=self.FFelements[i]
    print("Gate Nodes   = ",self.gates)
    print("Total Gates  = ",self.gatecount)
    print("Flip-Flop Elements",self.FFelements)
    print("Total Flip-Flop Elements",self.FFcount)
    print("Total Wires  = ",len(self.wires))
    print("Input Nodes  = ",len(self.inputs))
    print("Output Nodes = ",len(self.outputs))
    print("Total Nodes  = ",int(self.circuitgraph.number_of_nodes()))
    print("Gates + Wires + Inputs + Outputs = ",self.gatecount + len(self.wires) + len(self.inputs) + len(self.outputs))
  
  def graph(self):
    return self.circuitgraph
  
  def inputnodes(self)->list:
    return self.inputs
  
  def outputnodes(self)->list:
    return self.outputs
  
  def gatenodes(self)->dict:
    return self.gates
  
  def wirenodes(self)->list:
    return self.wires  #wires

  def FFnodes(self)->dict:
    return self.FFelements

  def nodeio(self,Node)->None:
    print("Node outputs = ",list(self.circuitgraph.successors(Node))) 
    print("Node inputs = ",list(self.circuitgraph.predecessors(Node)))
  
  # def generatekey(self,keyval):
  #   self.keyval=keyval
  #   self.keybit=bitarray(keyval)
  #   print(self.keyval,self.keybit)
  #   pass

  def graph_to_bench(self,outpath:str)->None:
    graphtonetlist=""
    for i in self.inputnodes():
      graphtonetlist+="INPUT("+i+")"+"\n"
      #print("INPUT("+i+")")
    
    for i in self.outputnodes():
      #print("OUPUT("+i+")")
      graphtonetlist+="OUTPUT("+i+")"+"\n"
    for i in self.gatenodes().keys():
      for j in range(self.gatenodes()[i]):
        tmpj=i+"_"+str(j)
        inp=list(self.circuitgraph.predecessors(tmpj))
        out=list(self.circuitgraph.successors(tmpj))
        if(i=="NOT" or i=='BUF'):
          graphtonetlist+=out[0]+" = "+i+"("+inp[0]+")"+"\n"
        else:
          graphtonetlist+=out[0]+" = "+i+"("+inp[0]+","+inp[1]+")"+"\n"
    print("Writing BENCH File to Location: ",outpath)
    with open(outpath, 'w') as f:
      f.write(graphtonetlist)



class cone_ckt:
  def __init__(self,outputs,primary_inputs,key_inputs,nodes,depth) -> None:
    self.primary_inputs=primary_inputs
    self.key_inputs=key_inputs
    self.nodes=nodes
    self.outputs=outputs
    self.depth=depth

class SATobj:
  def __init__(self,oracle_ckt:cone_ckt,locked_ckt:cone_ckt) -> None:
    self.oracle_ckt_cone=oracle_ckt
    self.locked_ckt_cone=locked_ckt
    self.keyinputs=self.locked_ckt_cone.key_inputs
    self.prim_inputs=self.locked_ckt_cone.primary_inputs
    
    self.oracle_ckt=circuit.Circuit.from_nodes(self.oracle_ckt_cone.nodes, self.oracle_ckt_cone.outputs)
    self.locked_ckt=(self.locked_ckt_cone.nodes, self.locked_ckt_cone.outputs)


class Analyze_Netlist:
  def __init__(self,locked_module_obj=None,unlocked_module_obj=None) -> None:
    self.locked=locked_module_obj
    self.unlocked=unlocked_module_obj
    self.attack_outputs={}


    if(self.locked!=None and self.unlocked!=None):
      self.common_outputs=utils.get_common_elements(self.locked.io["outputs"],self.unlocked.io["outputs"])
      self.diff_outputs=utils.get_difference(self.locked.io["outputs"],self.unlocked.io["inputs"])
      self.gen_cone_data()

  def gen_cone_data(self):
    def traverse_graph_r(obj,out_node):
      if(obj.circuitgraph.nodes[out_node]["type"]=="input"):
          if("key" in out_node and out_node not in self.keyinputs):
            self.keyinputs.append(out_node)
            self.nodes[out_node]=Node(out_node,[],"Key Input")
          elif(out_node not in self.primary_inp):
              self.primary_inp.append(out_node)
              self.nodes[out_node]=Node(out_node,[],"Primary Input")
          return 
      elif(obj.circuitgraph.nodes[out_node]["type"]=="output"):
          if(out_node not in self.out):
            self.out.append(out_node)
      elif(out_node in self.nodes):
        return
      
      pred=obj.circuitgraph.predecessors(out_node)
      self.depth+=1
      for i in pred:
        if(obj.circuitgraph.nodes[i]["type"]=="gate"): 
          self.nodes[out_node]=Node(out_node,list(obj.circuitgraph.predecessors(i)),utils.det_logic(obj.circuitgraph.nodes[i]["logic"],obj.gates))
        traverse_graph_r(obj,i) 
    
    
    
    self.common_outputs.sort(key=lambda s: int(''.join(filter(str.isdigit,s)) or 0))

    for i in self.common_outputs:
      pred1=list(self.unlocked.circuitgraph.predecessors(i))
      pred2=list(self.locked.circuitgraph.predecessors(i))
      if not (pred2 or pred1):
        print(pred1,pred2)
        continue

      self.primary_inp=[]
      self.keyinputs=[]
      self.out=[]
      self.nodes={}
      self.depth=0
      traverse_graph_r(self.unlocked,i)
      if(i not in self.out):
        self.out.append(i)
      self.out.sort(key=lambda s: int(''.join(filter(str.isdigit,s)) or 0))
      oracle_ckt=cone_ckt(self.out,self.primary_inp,self.keyinputs,self.nodes,self.depth)
      

      self.primary_inp=[]
      self.keyinputs=[]
      self.out=[]
      self.nodes={}
      self.depth=0
      traverse_graph_r(self.locked,i)
      if(i not in self.out):
        self.out.append(i)
      self.out.sort(key=lambda s: int(''.join(filter(str.isdigit,s)) or 0))
      locked_ckt=cone_ckt(self.out,self.primary_inp,self.keyinputs,self.nodes,self.depth)
      
      self.attack_outputs[i]=SATobj(oracle_ckt,locked_ckt)
      
      if(oracle_ckt.outputs==locked_ckt.outputs and locked_ckt.outputs==self.common_outputs):
        break