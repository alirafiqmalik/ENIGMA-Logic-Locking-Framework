import src.utils as utils
from src.AST import AST
import src.AST as ASTf
from src.LL import LogicLocking
import re


# obj=AST(file_path="input_files/demo.v",rw="w",flag="v",top="top",filename="demoorg")
obj = AST(file_path="./output_files/demoorg.json",rw='r',filename="demolocked") # r for read from file



# print(obj.top_module.circuitgraph["DFF__1207_"])
# obj.top_module.nodeio("DFF__1207_")
# print(obj.top_module.circuitgraph.nodes["DFF__1207_"])

# obj.update_LLverilog()


# obj.top_module.save_graph(svg=True)

LL=LogicLocking(obj)
# LL.PreSAT.set_key(3) # for TRLL, keycount<=Total No of original gates
# LL.PreSAT.SLL()


LL.PreSAT.set_key(50) # for TRLL, keycount<=Total No of original gates
LL.PreSAT.SLL()
# LL.PreSAT.TRLL_plus()


# LL.PostSAT.set_key(14) # for TRLL, keycount<=Total No of original gates
# # # # # LL.RLL()
# LL.PostSAT.AntiSAT()





# LL.PostSAT.set_key(5) # for TRLL, keycount<=Total No of original gates
# # # # LL.RLL()
# LL.PostSAT.AntiSAT()

# AntiSAT()

# obj.top_module.linkages["antisat_2"]['code']
# print(obj.top_module.linkages["antisat_2"]['port'])
    # code=tmpi.linkages[j]['code']
    # links=tmpi.linkages[j]['links']
    # print(j,tmpj['module_name'],tmpj['links'],tmpj['code'])
    # for L,R,D in links:
    #   print(L,R,D)

# for i in obj.modules:
#     obj.modules[i].gen_graph()
# obj.gen_graph_links()

# obj.
obj.writeLLFile()
obj.gen_verification_files()
# obj.top_module.save_graph(svg=True)



# utils.verify_verilog(path="tmp/top.v",top='top')






















# module {name} ({portnodes},KEY,Q);
# {nodes}
# input [2*{ic}-1:0] KEY;
# output Q;
# wire [{ic-1}:0]A;
# assign A={portnodes};
# wire Q1,Q2;
# g_block g(A,KEY[{ic}-1:0],Q1);
# g_block gc(A,KEY[2*{ic}-1:n],Q2);
# assign Q = Q1 & (~Q2);
# endmodule


# module {module_name}({portnodes},KEY,Q);
# {nodes}
# input [{ic-1}:0]KEY;
# wire [{ic-1}:0]A;
# assign A={portnodes};
# output reg Q;
# always@(*)begin if(A==KEY)Q=1;
# else Q=0;
# end endmodule"

            

# ~/FYP/linux/yosys/build/yosys -p '
# read_verilog input_files/demo.v
# hierarchy -check -top top
# proc; opt; fsm; opt; memory; opt;
# techmap; opt
# dfflibmap -liberty ./vlib/mycells.lib
# abc -liberty ./vlib/mycells.lib  
# flatten
# opt_clean -purge
# write_verilog -noattr ./tmp/tmp_syn2flatten.v
# '




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


