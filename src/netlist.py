import networkx as nx
import re

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
