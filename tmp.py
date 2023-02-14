from src.utils import *
import re
import multiprocessing
import random


verilog="""
module sarlock(inputs, key, lock_out);
wire _00_;
wire _01_;
wire _02_;
wire _03_;
wire _04_;
wire _05_;
wire _06_;
wire _07_;
wire _08_;
wire _09_;
wire _10_;
wire _11_;
wire _12_;
wire _13_;
wire _14_;
wire _15_;
wire _16_;
wire _17_;
wire _18_;
wire _19_;
wire _20_;
wire _21_;
wire _22_;
wire _23_;
wire [4:0] ckt_out;
input [7:0] inputs;
wire [7:0] inputs;
input [7:0] key;
wire [7:0] key;
output lock_out;
wire lock_out;
NOT_g _24_ ( .A#$%_5(inputs[3]), .^Y#$%_5(_00_) );
XNOR_g _25_ ( .^&A(inputs[0]), .B&*(key[0]), .Y_-(_01_) );
XNOR_g _26_ ( .A(inputs[7]), .dsdsB(key[7]), .Y(_02_) );
AND_g _27_ ( .A(_01_), .B(_02_), .Y(_03_) );
XNOR_g _28_ ( .A(inputs[1]), .B(key[1]), .Y(_04_) );
XNOR_g _29_ ( .A(inputs[3]), .B(key[3]), .Y(_05_) );
AND_g _30_ ( .A(_04_), .B(_05_), .Y(_06_) );
AND_g _31_ ( .A(_03_), .B(_06_), .Y(_07_) );
NOR_g _32_ ( .A(inputs[5]), .B(inputs[6]), .Y(_08_) );
NOR_g _33_ ( .A(inputs[4]), .B(inputs[7]), .Y(_09_) );
AND_g _34_ ( .A(_08_), .B(_09_), .Y(_10_) );
NOR_g _35_ ( .A(inputs[1]), .B(inputs[2]), .Y(_11_) );
AND_g _36_ ( .A(inputs[0]), .B(_00_), .Y(_12_) );
AND_g _37_ ( .A(_11_), .B(_12_), .Y(_13_) );
NAND_g _38_ ( .A(_10_), .B(_13_), .Y(_14_) );
XNOR_g _39_ ( .A(inputs[5]), .B(key[5]), .Y(_15_) );
XNOR_g _40_ ( .A(inputs[2]), .B(key[2]), .Y(_16_) );
AND_g _41_ ( .A(_15_), .B(_16_), .Y(_17_) );
XNOR_g _42_ ( .A(inputs[6]), .B(key[6]), .Y(_18_) );
XNOR_g _43_ ( .A(inputs[4]), .B(key[4]), .Y(_19_) );
AND_g _44_ ( .A(_18_), .B(_19_), .Y(_20_) );
AND_g _45_ ( .A(_17_), .B(_20_), .Y(_21_) );
AND_g _46_ ( .A(_14_), .B(_21_), .Y(_22_) );
NAND_g _47_ ( .A(_07_), .B(_22_), .Y(_23_) );
XNOR_g _48_ ( .A(ckt_out[0]), .B(_23_), .Y(lock_out) );
ckt c ( .a(inputs[3:0]), .b(inputs[7:4]), .c(ckt_out) );
endmodule
"""


def gates_extraction(verilog):
    pattern = r"(\w+)_g\s+(\w+)\s+\(\s*.*\((.*)\),\s*\.B\((.*)\),\s*\.Y\((.*)\)\s*\);"
    regex = re.compile(pattern)
    matches = regex.finditer(verilog)
    # Initialize an empty dictionary to store the gate information
    gates = {}

    # Iterate over the matches
    for match in matches:
        # Extract the gate type, input A, input B, and output from the match
        gate_type, gate_name, input_a, input_b, output = match.groups()
        
        # Add the gate information to the dictionary
        gates[gate_name] = {
            "type": gate_type,
            "inputs": [input_a, input_b],
            "outputs": output
        }

    return gates



def gates_module_extraction():
  gate_tech={}
  sub_module=[]
  def process_chunk(chunk):
    # gated={'BUF':[],'NOT':[], 'AND':[], 'OR':[],'XOR':[],'NAND':[], 'NOR':[],'XNOR':[]}
    # for type,init,extra in chunk:
    type,init,extra=chunk
    # re.sub("_g","",type)
    if(type in ['BUF_g','NOT_g', 'AND_g', 'OR_g', 'NAND_g', 'NOR_g','XOR_g','XNOR_g']):
      tmpx=re.findall(r'\.\S+\(([^\(\),]+)\)',extra)
      # print(type,tmpx)
      tmpx.reverse()
      if re.sub("_g","",type) not in gate_tech:
        gate_tech[re.sub("_g","",type)]=[{"init_name": init,"inputs": tmpx[1:] ,"outputs": tmpx[0]}]
      else:
        gate_tech[re.sub("_g","",type)].append({"init_name": init,"inputs": tmpx[1:] ,"outputs": tmpx[0]})
      # print(gate_tech)
    else:
      links=[]
      for i in extra.split(","):
        Lnode,Rnode=re.findall("\.(.*)\((.*)\)",i)[0]
        nodel={}
        noder={}

        if(":" in Rnode):
          nodename,startbit,endbit=re.findall(r"(.*)\[(\d+):(\d+)\]",Rnode)[0]
          startbit=int(startbit)
          endbit=int(endbit)
          noder=connector(startbit-endbit+1,startbit,endbit)
          noder["node_name"]=nodename
        else:
          noder=Rnode

        if(":" in Lnode):
          nodename,startbit,endbit=re.findall(r"(.*)\[(\d+):(\d+)\]",Lnode)[0]
          startbit=int(startbit)
          endbit=int(endbit)
          nodel=connector(startbit-endbit+1,startbit,endbit)
          noder["node_name"]=nodename
        else:
          nodel=Lnode
        links.append((nodel,noder))
      sub_module.append({"module_name": type, "init_name": init, "links":links})

  for i in re.findall(r"(\w+) (\w+) \((.*)\);",verilog):
    process_chunk(i)

  return gate_tech,sub_module






if __name__ == '__main__':

  
  # for type,init,extra in re.findall(r"(\w+) (\w+) \((.*)\);",verilog)[0:5]:
  #   print(extra)
  #   tmpx=re.findall(r'\.\S+\(([^\(\),]+)\)',extra)
  #   tmpx.reverse()
  #   print(type,init,tmpx)
  #   print()

  # manager=multiprocessing.Manager()
  #   # gate_tech={'BUF':[],'NOT':[], 'AND':[], 'OR':[],'XOR':[],'NAND':[], 'NOR':[],'XNOR':[]}
  #   # sub_module=[]
  # gate_tech = manager.dict()
  # sub_module = manager.list()
  gate_tech,sub_module=tmpfn()
  


  for i in gate_tech:
    print(i,len(gate_tech[i]))

  
  print(sub_module)


# if __name__ == "__main__":
#   manager = multiprocessing.Manager()
#   # with multiprocessing.Manager() as manager:
#   # gate_tech = manager.dict()
#   # sub_module = manager.list()
#   processes=[]
#   for i in re.findall(r"(\w+) (\w+) \((.*)\);",verilog):
#     process = multiprocessing.Process(target=process_chunk, args=(i,))
#     process.start()
#     processes.append(process)

#   for process in processes:
#     process.join()

#   print(gate_tech)
  




  

  #   processes = []
  #   for chunk in re.findall(r"(\w+) (\w+) \((.*)\);",verilog):
  #     # print(chunk)
      # process = multiprocessing.Process(target=process_chunk, args=(chunk,))
      # print(process)
      # process.start()
      # processes.append(process)

  # for process in processes:
  #     process.join()



  # print(re.findall(r"(\w+) (\w+) \((.*)\);",verilog)[0])
  # re.findall(r"(\w+) (\w+) \((.*)\);",verilog)[0]
  # print()
  # d,l=traverse_array_with_multiprocessing(re.findall(r"(\w+) (\w+) \((.*)\);",verilog)[:], 10)
  # print(d)
  











# """
# input [3:0] test,tmp;
# input [6:0] testxy;
# input[10:2] dump;
# input check,check3;
# input check6;

# """



# nodes,port=extract_io_v(verilog,mode="input")

# print(nodes.keys())

# for i in nodes:
#     print(nodes[i])

# print(port)

















import networkx as nx
import json
import pickle
import base64

# G = nx.DiGraph()
# # Add node with attributes
# G.add_node(1, mode='red', type='circle')
# G.add_node(2, mode='green', type='square')
# G.add_edge(1, 2)



# G1 = nx.DiGraph()
# # Add node with attributes
# G1.add_node(4, mode='red', type='circle')
# G1.add_node(2, mode='green', type='square',init="init")
# G1.add_node(3, mode='blue', type='triangle')
# G1.add_edge(4, 2)
# G1.add_edge(3, 2)



# G_merged = nx.DiGraph()

# # Add nodes and their attributes from G and G1 to G_merged
# for node, attrs in G.nodes(data=True):
#     G_merged.add_node(node, **attrs)

# for node, attrs in G1.nodes(data=True):
#     G_merged.add_node(node, **attrs)



# G_merged.add_edges_from(G1.edges())
# G_merged.add_edges_from(G.edges())

# # Access node attributes
# print(G_merged.nodes[1]) # Output: {'mode': 'red', 'type': 'circle'}
# print(G_merged.nodes[2]) # Output: {'mode': 'green', 'type': 'square'}






# Encode the graph object to a binary string using pickle
binary_data = pickle.dumps(G_merged)

# Encode the binary string to a base64 string
base64_data = base64.b64encode(binary_data).decode('utf-8')

# Store the base64 encoded data in a JSON object
data = {'DiGraph': base64_data}

# Write the JSON object to a file
with open('./tmp/graph.json', 'w') as f:
    json.dump(data, f)

# Load the JSON object from the file
with open('./tmp/graph.json', 'r') as f:
    data = json.load(f)

# Decode the base64 string back to binary
binary_data = base64.b64decode(data['DiGraph'].encode('utf-8'))

# Decode the binary string back to a graph object
G2 = pickle.loads(binary_data)

# # Check if the graph has been successfully decoded
# assert nx.is_isomorphic(G_merged, G2)