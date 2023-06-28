from src.LL import LogicLocking
import src.utils as utils
from src.AST import AST



# top="c5315"
# pathin="input_files/Benchmarks/ISCAS85/"+f"{top}/{top}.v"

top="soc_top"
pathin="input_files/soc_top.v"
# path="../FYP/linux/bare-metal-processor/design"

# obj=AST(file_path=pathin,rw="w",flag="v",top=top,filename=f"{top}org") #Run to Read in Verilog Design
# obj.top_module.save_graph(svg=True)

obj = AST(file_path=f"./output_files/{top}org.json",rw='r',filename=f"{top}locked_test") #Run to read in AST Format

utils.clean_dir("./tmp")
countorg=obj.gen_results()

bits=128
LL=LogicLocking(obj) #Object for Locking Circuit
# 291480291480291480291480
LL.PreSAT.set_key(bits,key=155078537555888897905301648718854418945) # set Key bits or Locking Key Integer Value
LL.PreSAT.SLL()  # perform Strong Logic Locking on Circuit


# LL.PostSAT.set_key(bits) # set Key bits or Locking Key Value
# LL.PostSAT.Sarlock()  # perform Strong Logic Locking on Circuit


obj.writeLLFile() # Write Locked circuit to AST format file

obj.write_Verilog_File(file="LL",file_name="locked_top") # Write Locked circuit Verilog Code to File

# obj.top_module.save_graph(svg=True)
outpath=r"/mnt/d/alis_files/LAPTOP/alis_files/university_files/PROJECTS_2022-2023/FYP/Circuits/top"
obj.gen_verification_files(output_dir=outpath) #Generate Verification Testbench Files

# # obj.top_module.save_graph(svg=True)
count_ll,overhead,FF_count=obj.gen_results(org=False)

print(countorg,count_ll,overhead,bits*100/(FF_count+bits))
























# # c5315
# # pathin="input_files/Benchmarks/ISCAS85/"+f"{top}/{top}.v"
# # pathin="input_files/demo.v"

# top="picorv32"
# pathin="/home/alira/FYP/linux/picorv32/picorv32.v"

# top="demo"
# pathin="input_files/demo.v"

# top="c5315"
# pathin="input_files/Benchmarks/ISCAS85/"+f"{top}/{top}.v"

# top="c5315"
# pathin="input_files/Benchmarks/ISCAS85/"+f"{top}/{top}.v"
# /home/alira/FYP/linux/Final_Demo/bare-metal-processor/design/soc_top_locked/src/soc_top.v







# for i in range(1,2):
#   ti={0:"RLL",1:"SLL",2:"TRLL",3:"SARLOCK",4:"RLL_sarlock",5:"SLL_sarock",6:"TRLL_sarock"}
#   obj = AST(file_path=f"./output_files/{top}org.json",rw='r',filename=f"{top}locked_{ti[i]}") #Run to read in AST Format


#   # # 16733 16618
#   countorg=obj.gen_results()
#   # print(countorg)
#   # # obj.update_org_verilog()

#   # # # obj.top_module.save_graph(svg=True) #Run to save circuit Graph as a SVG
#   # bits=128
#   # LL=LogicLocking(obj) #Object for Locking Circuit


#   # LL.PreSAT.set_key(bits) # set Key bits or Locking Key Value
  
#   # if(i==0):
#   #   LL.PreSAT.RLL()  # perform Strong Logic Locking on Circuit
#   # elif(i==1):
#   #   LL.PreSAT.SLL()  # perform Strong Logic Locking on Circuit
#   # elif(i==2):
#   #   LL.PreSAT.TRLL_plus()  # perform Strong Logic Locking on Circuit
#   # elif(i==3):
#   #   # LL.PreSAT.RLL()  # perform Strong Logic Locking on Circuit
#   #   LL.PostSAT.set_key(bits) # set Key bits or Locking Key Value
#   #   LL.PostSAT.Sarlock()  # perform Strong Logic Locking on Circuit
#   # elif(i==4):
#   #   LL.PreSAT.RLL()  # perform Strong Logic Locking on Circuit
#   #   LL.PostSAT.set_key(bits) # set Key bits or Locking Key Value
#   #   LL.PostSAT.Sarlock()  # perform Strong Logic Locking on Circuit
#   # elif(i==5):
#   #   LL.PreSAT.SLL()  # perform Strong Logic Locking on Circuit
#   #   LL.PostSAT.set_key(bits) # set Key bits or Locking Key Value
#   #   LL.PostSAT.Sarlock()  # perform Strong Logic Locking on Circuit
#   # elif(i==6):
#   #   LL.PreSAT.TRLL_plus()  # perform Strong Logic Locking on Circuit
#   #   LL.PostSAT.set_key(bits) # set Key bits or Locking Key Value
#   #   LL.PostSAT.Sarlock()  # perform Strong Logic Locking on Circuit


#   # LL.PostSAT.set_key(bits) # set Key bits or Locking Key Value
#   # LL.PostSAT.Sarlock()  # perform Strong Logic Locking on Circuit


#   # obj.writeLLFile() # Write Locked circcuit to AST format file
#   # outpath="./tmp/"
#   # outpath=r"/mnt/d/alis_files/LAPTOP/alis_files/university_files/PROJECTS_2022-2023/FYP/Circuits/top"
#   # {ti[i]}
#   name="org"#ti[i]
#   obj.write_Verilog_File(file="org",file_name=f"{name}")
#   # obj.gen_verification_files(file_name=f"{ti[i]}",tmpdir=outpath) #Generate Verification Testbench Files
#   # # # obj.top_module.save_graph(svg=True)
#   # count_ll,overhead,FF_count=obj.gen_results(org=False)

#   # print(countorg,count_ll,overhead,bits*100/(FF_count+bits))
















# from src.path_var import *

# cmd = """
# {yosys_path} -q -p'
# {readin}
# hierarchy -check -top {module_name}
# proc; opt; fsm; opt; memory; opt;
# techmap; opt
# dfflibmap -liberty ./vlib/mycells.lib
# abc -liberty ./vlib/mycells.lib  
# flatten
# opt_clean -purge
# write_verilog -noattr {out_file}
# '
# """
















# top="picorv32"
# pathin="/home/alira/FYP/linux/picorv32/picorv32.v"

# obj = AST(file_path=f"./output_files/{top}org.json",rw='r',filename=f"{top}locked") #Run to read in AST Format

# verilog=open("tmp/picorv32_2_flatten.v").read()

# verilog=utils.format_verilog(verilog)

# t=re.findall(r"assign (\\?.*) = (\\?.*) ?;\n",verilog)
# tmp=""
# for i in t:
#     # print(i)
#     node=obj.top_module.io["outputs"][i[0]]
#     if(node['bits']!=1):
#         ct=utils.extract_value(i[1])
#         ei,si=re.findall(f"wire \[(\d+):(\d+)\] {i[0]};",verilog)[0]
#         si,ei=int(si),int(ei)
#         # print(node['bits'],len(ct),ct,si,ei)
#         for k in range(si,ei+1):
#             tmp+=f"BUF_g assignbuf_{i[0]}_{k}_{i[1]}_ ( .A(1'b{ct[k]}), .Y({i[0]}[{k}]) );\n"
#             print(f"BUF_g assignbuf_{i[0]}_{k}_{i[1]}_ ( .A(1'b{ct[k]}), .Y({i[0]}[{k}]) );\n")
#     else:
#         print(f"BUF_g assignbuf_{i[0]}_{i[1]}_ ( .A({i[1]}), .Y({i[0]}) );\n")


#     # print(node['bits'])
#     # print(i[0] in obj.top_module.io["wires"])
#     # print(i[0] in obj.top_module.io["outputs"])
#     # print(obj.top_module.io["outputs"][i[0]])





# def extract_assign(verilog):
#     t=re.findall(r"assign (\\?.*) = (\\?.*) ?;\n",verilog)
#     for i in t:
#         print(i)


# extract_assign(verilog)

# with open("tmp/tmp.v","w") as f:
#     f.write(verilog)





# # t=re.findall(r"assign (\\?.*) = (\\?.*) ?;\n",verilog)











# pathl=os.listdir("input_files/Benchmarks/ISCAS85")
# txt="Circuit, Original Gate Count, Locked Gate Count, %Overhead\n"

# for i in pathl:
#   if(i=="c5315"):
#     continue
#   pathin=f"input_files/Benchmarks/ISCAS85/{i}/{i}.v"
#   top=i
#   path=f"output_files/{top}org.json"

#   obj=AST(file_path=pathin,rw="w",flag="v",top=top,filename=f"{top}org") #Run to Read in Verilog Design
#   obj = AST(file_path=f"./output_files/{top}org.json",rw='r',filename=f"{top}locked") #Run to read in AST Format


#   countorg=obj.gen_results()

#   # obj.top_module.save_graph(svg=True) #Run to save circuit Graph as a SVG
#   LL=LogicLocking(obj) #Object for Locking Circuit
#   LL.PreSAT.set_key(128) # set Key bits or Locking Key Value
#   LL.PreSAT.SLL()  # perform Strong Logic Locking on Circuit
#   obj.writeLLFile() # Write Locked circcuit to AST format file
#   obj.gen_verification_files() #Generate Verification Testbench Files
#   # obj.top_module.save_graph(svg=True)
#   count_ll,overhead=obj.gen_results(org=False)

#   txt+=f"{top},{countorg},{count_ll},{overhead}\n"
#   print(i)
#   with open("./tmp/stat.csv","w") as f:
#     f.write(txt)








































# tmp=["1'h0" ,"2'h3", "3'h0","32'd0","32'd124","81'h000000000000000000000","7'b1111100"]





# for i in tmp:
#     num=utils.extract_value(i)
#     print(i,num)




# verilog=open("tmp/picorv32_2_flatten.v").read()




# with open("tmp/tmp.v","w") as f:
#     f.write(verilog) 


# elif("'" in R):
#     if(":" not in L):
#         print(L,re.findall(re.compile(L),verilog))
#     if("'h" in R):
#         pass
#     elif("'d" in R):
#         pass
#     pass
#     # print(i)
# else:
#     pass
#     # print(L,R)








# for i,j in zip(L,R):
#             if(":" not in i):
#                 if(re.findall(re.compile(i),verilog)==[]):
#                     continue
#                 tmpstr+=f"assign {i} = {j};\n"
#             else:
#                 tmpi,ei,si=re.findall(r"(.*)\[(\d+):(\d+)\]",i)[0]
#                 si,ei=int(si),int(ei)
#                 if("'h" in j):
#                     tmpv=utils.extract_value(j,bits=ei-si+1)

#                 for ii,k in enumerate(range(si,ei+1)):
#                     if(re.findall(re.compile(f"{tmpi}[{k}]"),verilog)==[]):
#                             if("'h" not in j):
#                                 print(i,j)
#                             continue
                    
#                     if("'h" in j):
#                         tmpbuf+=f"BUF_g ab_{tmpi}_ ( .A({tmpi}[{k}]), .Y(1'h{tmpv[ei-si-ii]}) );\n"
#                     else:
#                         print(f"BUF_g ab_{tmpi}_ ( .A({tmpi}[{k}]), .Y({j}) );")
#                         tmpbuf+=f"BUF_g ab_{tmpi}_ ( .A({tmpi}[{k}]), .Y({j}) );\n"
                        
#                     # print(k,re.compile(f"{tmpi}[{k}]"),re.findall(re.compile(f"{tmpi}[{k}]"),verilog))















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


