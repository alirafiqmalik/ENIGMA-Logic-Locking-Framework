import src.utils as utils
import src.verification as ver
from src.AST import AST
import src.AST as ASTf
from src.PreSAT import PreSAT
import src.PostSAT as PostSAT
import networkx as nx
import re


# obj=AST(file_path="./input_files/Benchmarks/ISCAS85/c17/c17.v",rw="w",flag="v",top="c17",filename="c17org")
obj = AST(file_path="./output_files/c17org.json",rw='r',filename="c17locked") # r for read from file
# obj.save_module_connections()




# LL=PreSAT(obj.top_module)
# LL.set_key(3) # for TRLL, keycount<=Total No of original gates
# # # LL.RLL()
# # # LL.SLL()
# LL.TRLL_plus()
# print(obj.linkages[obj.top_module_name])
def AntiSAT():
  modulename="anitsat"
  inputs=obj.top_module.io["inputs"].copy()
  if("lockingkeyinput" in inputs):
    inputs.pop("lockingkeyinput")

  nodes,ic=ASTf.node_to_txt(inputs,mode="input",return_bits=True)
  initname=f"{modulename}_{len(obj.modules)+1}"

  portnodes=obj.top_module.io["input_ports"]
  portnodes=re.sub("lockingkeyinput,","",portnodes)
  portnodes=portnodes[:-1]

  tmp=f"module {modulename}({portnodes},KEY,Q);\n{nodes}input [{ic-1}:0] KEY;\nwire [{ic-1}:0] A;\nassign A={{{portnodes}}};\noutput reg Q;\nalways@(*)begin \nif(A==KEY)Q=1;\nelse Q=0;\nend \nendmodule"

  a=len(obj.top_module.lockingdata["inputs"])+1+ic
  b=len(obj.top_module.lockingdata["inputs"])+1

  links=[]
  port=""
  for i in inputs:
    links.append((i,i,"I"))
    port+=f".{i}({i}), "
  port+=f".KEY(lockingkeyinput[{b}:{a}])"
  port+=".Q(Q_int)"

  links.append(("KEY",f"lockingkeyinput[{b}:{a}]","I"))
  links.append(("Q","Q_int","O"))

  obj.top_module.io['wires']["Q_int"]=utils.connector(1,0,0)

  obj.top_module.linkages={}
  obj.top_module.linkages[initname]={"module_name": "antisat","links":links,"port":port,"code":tmp}

  if("lockingkeyinput" not in obj.top_module.io['inputs']):
    obj.top_module.io['inputs']["lockingkeyinput"]=utils.connector(1,0,0)
    obj.top_module.io["input_ports"]+="lockingkeyinput,"
  else:
    obj.top_module.io['inputs']["lockingkeyinput"]=utils.connector(a+1,0,a)



AntiSAT()

for i in obj.modules:
  tmpi=obj.modules[i]
  for j in tmpi.linkages:
    tmpj=tmpi.linkages[j]
    module_name=tmpi.linkages[j]['module_name']
    code=tmpi.linkages[j]['code']
    links=tmpi.linkages[j]['links']
    # print(j,tmpj['module_name'],tmpj['links'],tmpj['code'])
    for L,R,D in links:
      print(L,R,D)


obj.gen_graph_links()
obj.top_module.save_graph(svg=True)
obj.writeLLFile()
obj.gen_verification_files()



# utils.verify_verilog(path="tmp/top.v",top='top')










# modulename="anitsat"
# L=list(inputs.keys()).copy()
# R=list(inputs.keys()).copy()

# initname=f"{modulename}_{len(postsat_blocks)}"
# # print(initname)

# portnodes=obj.top_module.io["input_ports"]
# portnodes=re.sub(",lockingkeyinput,","",portnodes)
# t,c=ASTf.node_to_txt(inputs,mode="input",return_bits=True)
# # print(re.sub("(^|\n)input","wire",t))
# ic=c
# nodes=t
# # print(inputs)
# port=modulename+"{initname} ({portnodes}, {KEY}, {Q});"
# tmp=f"module {modulename}({portnodes},KEY,Q);\n{nodes}input [{ic-1}:0]KEY;\nwire [{ic-1}:0]A;\nassign A={{{portnodes}}};\noutput reg Q;\nalways@(*)begin \nif(A==KEY)Q=1;\nelse Q=0;\nend \nendmodule"
# # print(tmp)
# a=len(obj.top_module.lockingdata["inputs"])+1+ic
# b=len(obj.top_module.lockingdata["inputs"])+1
# R.append(f"lockingkeyinput[{b}:{a}]")
# R.append("Q_int")
# L.append("KEY")
# L.append("Q")
# print(L)
# print(R)


# if("lockingkeyinput" not in obj.top_module.io['inputs']):
#   obj.top_module.io['inputs']["lockingkeyinput"]=utils.connector(1,0,0)
#   obj.top_module.io["input_ports"]+="lockingkeyinput,"
# else:
#   obj.top_module.io['inputs']["lockingkeyinput"]=utils.connector(a+1,0,a)





# obj.top_module.postSAT_modules["sarlock_init_1"]={"module_name": modulename,"L":L,"R":R,"code":""}


# obj.top_module.gen_graph()
# obj.gen_graph_links(obj.top_module)

# a,b,c =PostSAT.gencc(modulename, inputs, key=10)
# # a,c=PostSAT.gencc_SarLock(modulename=modulename, inputs=inputs,key=10)
# print(a+'\n')
# print(b+'\n')
# print(c+'\n')





# print(tmp)

# obj.top_module.save_graph(svg=True)
# obj.writeLLFile()



# obj.gen_verification_files()







# # tmpx=""
# nodes=obj.top_module.io["inputs"]
# for i in nodes:
#   node=nodes[i]
#   if(node['bits']!=1):
#     print(f"wire [{node['endbit']}:{node['startbit']}] {i}_org;")
#     for k in range(node['startbit'],node['endbit']+1):
#       print(f"assign {i}[{k}] = {i}[{k}]_org ^ FC;")
#       # print(f"assign {i}[{k}] = {i}[{k}]_org ^ FC;")
#   else:
#     print(f"wire {i}_org")
#     print(f"assign {i} = {i}_org ^ FC;") 
  

# def gen_refport(lista,listb=None):
#   if(listb==None):
#     listb=lista
#   tmp=""
#   for i,j in zip(lista,listb):
#     tmp+=f".{i}({j}), "
#   return tmp

# tmp=""
# tmp+=gen_refport(obj.top_module.io["outputs"])
# tmp+=gen_refport(obj.top_module.io["inputs"])
# print(tmp)



# inputs=list(obj.top_module.io["inputs"].keys())
# # inputs.remove("lockingkeyinput")

# a,c=PostSAT.gencc_SarLock(modulename="anitsat", inputs=inputs,key=10)
# print(a+'\n')
# print(c+'\n')



# obj.writeLLFile()


# t=PostSAT.PostSAT_LL(netlist=obj.top_module.module_LLverilog)
# a,c=t.SarLock()















# a,c=PostSAT.gencc_SarLock(modulename="sarlock", inputs=list(obj.top_module.io["inputs"].keys()),key=443)
# print(a+'\n')
# print(c+'\n')


# tmpx=""
# for i in obj.top_module.io["outputs"]:
#     tmpx+="assign {} = {} ^ FC;\n".format(i,i)
#     print(f".{i}({i}), ",end="")
# print()
# for i in obj.top_module.io["inputs"]:
#     print(f".{i}({i})",end="")

# print("\n\n\n"+tmpx)


# top="module top({topbus});\n{topio}\n{CRwire}\n{orgmodule}\n{CRmodule}\n{Xornet}\nendmodule"


# top=top.format(
#                 topbus=iportnodes+","+oportnodes+","+keyport,
#                 topio="input {};\n{}\n{}\n".format(keyport,inputnodes,outputnodes),
#                 CRwire=orgoutputwires+"wire {};\n".format("FC"),
#                 orgmodule="\norg o1({});".format(tmporgport),
#                 CRmodule=pc.format(init="to",portnodes="{%s}"%portnodes_antisat,KEY="{%s}"%keyport,Q="FC"),
#                 Xornet=tmpx
#                 )

# return top+"\n\n{}\n\n{}".format(corrupt,self.netlist)









# tmp=utils.synthesize_verilog(obj.LLverilog+obj.gate_lib, top=obj.top_module_name,flag = "flatten")

# cmd = """
#              ~/FYP/linux/yosys/build/yosys -q -p'
#             read_verilog /home/alira/FYP_FINAL/tmpll.v
#             hierarchy -check -top {}
#             proc; opt; fsm; opt; memory; opt;
#             techmap; opt;
#             flatten
#             # dfflibmap -liberty ./vlib/mycells.lib
#             # abc -liberty ./vlib/mycells.lib  
#             opt_clean -purge
#             # flatten
#             write_verilog -noattr /home/alira/FYP_FINAL/tmpll.v
#             '
#         """
# import subprocess    
# subprocess.run(cmd.format(obj.top_module_name), shell=True)


# tmp=open("/home/alira/FYP_FINAL/tmpll.v").read()

# with open("/home/alira/FYP_FINAL/tmpll.v","w") as f:
#   f.write(tmp)


# path="/home/alira/FYP_FINAL/tmpll.v"
# top="top"

# utils.verify_verilog(path,obj.top_module_name)



# ~/FYP/linux/yosys/build/yosys -q -p'
# read_verilog /home/alira/FYP_FINAL/tmpll.v
# hierarchy -check -top locked
# '


