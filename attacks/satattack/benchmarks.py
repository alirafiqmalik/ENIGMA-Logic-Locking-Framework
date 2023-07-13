import circuit
from src.Parser.verilog_parser import extract_io_v,extract_gates_v
from src.Parser.bench_parser import extract_io_b,extract_gates_b
from src.utils import format_verilog
from node import Node,DFF



def read_nodes_v(filename):
  verilog=open(filename).read()
  verilog=format_verilog(verilog)
  inp,_=extract_io_v(verilog,'input')
  out,_=extract_io_v(verilog,'output')
  gates,_=extract_gates_v(verilog)

  node={}
  for i in inp:
    if('key' in i):
      node[i]=Node(i,[],"Key Input")
    else:
      node[i]=Node(i,[],"Primary Input")

  for i in gates:
    for j in gates[i]:

      tmpj=list(j[:-1])
      node[j[-1]]=Node(j[-1],tmpj,i.title())
  return node,out


def read_nodes_b(filename):
  netlist=open(filename).read()  
  inp= extract_io_b(netlist,mode='input')
  out=extract_io_b(netlist,mode='output')
  gates,_=extract_gates_b(netlist)



  node={}

  for i in inp:
    if('key' in i):
      node[i]=Node(i,[],"Key Input")
    else:
      node[i]=Node(i,[],"Primary Input")

  for i in gates:
    for j in gates[i]:
      node[j[0]]=Node(j[0],list(j[1:]),i.title())
  return node,out





def read_ckt(filename,file_type):
    """
    Reads in a circuit from a benchmark file.
    filename: the name of the benchmark file
    returns: object representation of the circuit
    """
    if(file_type=='b'):
       nodes, output_names = read_nodes_b(filename)
    elif(file_type=='v'):
      nodes, output_names = read_nodes_v(filename)
    else:
      Exception("ERROR")
      return None

    # print("H ",nodes)
    # print("There  ",nodes['a'],type(nodes['a']))
    return circuit.Circuit.from_nodes(nodes, output_names)








# def read_nodes2(filename):
#     """
#     Reads in the nodes of a circuit from a benchmakr file.
#     filename: the name of the benchmark file
#     returns: the nodes of the circuit, the output names of the circuit
#     """
#     with open(filename) as f:
#         t = tokenizer.Tokenizer(f)
#         p = parser.Parser()
#         nodes, output_names = p.parse(t)
#         # print("HERE ",nodes, output_names)
#         # print("There  ",nodes['a'],type(nodes['a']))
#         return nodes, output_names


# def get_expected_key(filename):
#     key = {}

#     with open(filename) as f:
#         for line in f.readlines():
#             if "KeyGate" in line:
#                 tokens = line.split()

#                 key_name = tokens[2][0:-1]
#                 key_bit = tokens[0] == "xnor"

#                 if "NOT" in tokens[1]:
#                     key_bit = not key_bit

#                 key[key_name] = key_bit                
#     print("exp = ",key)
#     return key
