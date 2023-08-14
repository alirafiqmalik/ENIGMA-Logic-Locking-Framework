import re
import concurrent.futures
from src.Parser.verilog_parser import extract_io_v,gates_module_extraction
from src.Parser.bench_parser import extract_gates_b,extract_io_b
from src.utils import format_verilog,io_port,det_FF_node

gate_to_assign={'BUF':'','NOT':'~', 'AND':'&', 'OR':'|','XOR':'^','NAND':'&', 'NOR':'|','XNOR':'^'}

def gen_line(i,j,inputs,output,port,module_name):
    tmp={}
    for mIO,mNode in zip(inputs,j[1:]):
        tmp[mIO]=mNode
    tmp[output]=j[0]

    formatted_out=re.sub(r"[^A-Za-z0-9_]",r"",j[0])
    init_name=f"{i}_out_{formatted_out}_"
    return f"{module_name} {init_name} {port.format(**tmp)}\n"


def proc_nested(i,out,inp,inputs,output,port,module_name,layer=0):
    tmpouts=[]
    txt=""
    for c,t in enumerate(range(0,len(inp)-1,2)):
        tmpi=f"{out}_{layer}_{c}"
        tmpouts.append(tmpi)
        txt+=gen_line(i,[tmpi]+inp[t:t+2],inputs,output,port,module_name)

    if(inp[t+2:]):
        tmpouts=tmpouts+inp[t+2:]

    if(len(tmpouts)==2):
        txt+=gen_line(i,[out]+tmpouts,inputs,output,port,module_name)
        return tmpouts,txt

    tmpouts_r,txt_r=proc_nested(i,out,tmpouts,inputs,output,port,module_name,layer+1)
    return tmpouts+tmpouts_r,txt+txt_r

def gen_line_multi(i,j,inputs,output,port,module_name):
    return proc_nested(i,j[0],j[1:],inputs,output,port,module_name,layer=0)

def process_FF_node(Nodeseg,clkpin,outputs,template,port,module_name):
    local_wires=[]
    local_verilog_init=""
    # local_verilog_wire=""
    for j in Nodeseg:
        if((j[0] not in outputs) and (j[0] not in local_wires)):
            # local_verilog_wire +="wire {};".format(j[0])
            local_wires.append(j[0])
    
        tmp={}
        for mIO in template["port_list"]:
            type_node=utils.det_FF_node(mIO)
            if(type_node=="clock"):
                tmp[mIO]=clkpin
            elif(type_node=="inputs"):
                tmp[mIO]=j[1]
            elif(type_node=="outputs"):
                tmp[mIO]=j[0]
        init_name=f"DFF_out_{j[0]}_"
        # print(f"{module_name} {init_name} {port.format(**tmp)}\n")
        local_verilog_init+=f"{module_name} {init_name} {port.format(**tmp)}\n"
        
    return local_wires,local_verilog_init

def proc_node(Node,outputs,template,port,module_name,i):
    inputs=template["inputs"]
    output=template["outputs"][0]
    local_wires=[]
    local_verilog_init=""
    # local_verilog_wire=""
    for j in Node:
        if((j[0] not in outputs) and (j[0] not in local_wires)):
            # local_verilog_wire +="wire {};\n".format(j[0])
            local_wires.append(j[0])
        if(len(j[1:])>2):
            new_wires_all,verilog_init_i=gen_line_multi(i,j,inputs,output,port,module_name)
            local_verilog_init+=verilog_init_i
            
            for tmpwire in new_wires_all:
                if((tmpwire not in outputs) and (tmpwire not in local_wires)):
                    local_wires.append(tmpwire)
                    # local_verilog_wire +="wire {};\n".format(tmpwire)
        else:
            local_verilog_init+=gen_line(i,j,inputs,output,port,module_name)
    
    return local_wires,local_verilog_init


def bench_to_verilog_vlib(bench,
                          vlib_var,
                          clkpin="Clock",
                          modulename="top",
                          num_threads = 4 # Number of threads to use for parallel processing
                          # You can adjust this number based on your system's capabilities
                          ):
    
    bench=re.sub(" +"," ",bench)

    gate_mapping_vlib,gates_vlib,FF_vlib=vlib_var
    
    
    
    gates,gate_count = bench_parser.extract_gates_b(bench)
    inputs_netlist = bench_parser.extract_io_b(bench, mode="input")
    outputs_netlist = bench_parser.extract_io_b(bench, mode="output")

    gate_list = list(gates.keys())    

    wires=[]
    verilog_wire=""
    verilog_init=""

    if(("DFF" in gates)):
        if(clkpin not in inputs_netlist):
            inputs_netlist.append(clkpin)
        
        gate_list.remove("DFF")
        Node = gates["DFF"]
        for k in FF_vlib:
            FF_in=FF_vlib[k]["inputs"]
            port=FF_vlib[k]["port"]
            if(len(FF_in)==2):
                template=FF_vlib[k]
                break

        port=template["port"]
        module_name=k

        # Split 'Node' list into chunks for parallel processing
        if(len(Node)>num_threads):
            chunk_size = len(Node) // num_threads
        else:
            chunk_size=len(Node)
        # 
        chunks = [Node[i:i+chunk_size] for i in range(0, len(Node), chunk_size)]
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_threads) as executor:
            val=executor.map(process_FF_node, 
                            chunks,
                            [clkpin]*num_threads,
                            [outputs_netlist]*num_threads,
                            [template]*num_threads,
                            [port]*num_threads,
                            [module_name]*num_threads
                            )
        
        for i,j in val:
            verilog_init+=j
            wires+=i
    

    for i in gate_list:
        # 
        Node = gates[i]
        
        template=gates_vlib[gate_mapping_vlib[i][0]]
        port=template["port"]
        # inputs_netlist=template["inputs_netlist"]
        # output=template["outputs_netlist"][0]
        module_name=gate_mapping_vlib[i][0]
        
        # Split 'Node' list into chunks for parallel processing
        if(len(Node)>num_threads):
            chunk_size = len(Node) // num_threads
        else:
            chunk_size=len(Node)
        # 
        chunks = [Node[i:i+chunk_size] for i in range(0, len(Node), chunk_size)]
              
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_threads) as executor:
            result=executor.map(proc_node, 
                                chunks,
                                [outputs_netlist]*num_threads,
                                [template]*num_threads,
                                [port]*num_threads,
                                [module_name]*num_threads,
                                [i]*num_threads
                                )
        
        for i,j in result:
            verilog_init+=j
            wires+=i
    
    
    wires=list(set(wires))
        
    for i in wires:
        verilog_wire +="wire {};".format(i)
    
    
    
    porti, input_dec,replace_i = utils.io_port(inputs_netlist, mode="input")
    porto, output_dec,replace_o = utils.io_port(outputs_netlist, mode="output")

    verilog = "module {} ({},{});{}".format(modulename,porti, porto, input_dec+output_dec)

    verilog += verilog_wire + verilog_init + "endmodule"
    return verilog


def bench_to_verilog(bench,clkpin="Clock",modulename="top"):
    bench=re.sub(" +"," ",bench)
    gates,gate_count = extract_gates_b(bench)
    # print("HERE ",gates)
    inputs = extract_io_b(bench, mode="input")
    outputs = extract_io_b(bench, mode="output")

    gate_list = list(gates.keys())

    # print(gate_list)
    # print(gates)


    if(("DFF" in gate_list) and clkpin not in inputs):
        print("DFF IN CIRCUIT")
        clockp=","+clkpin
        clockio="input {};".format(clkpin)
    else:
        clockio=""
        clockp=""

    porti, input_dec,replace_i = io_port(inputs, mode="input")
    porto, output_dec,replace_o = io_port(outputs, mode="output")
    verilog = "module {} ({},{});{}".format(modulename,
        porti+clockp, porto, input_dec+output_dec+clockio)


    wires=[]
    verilog_wire=""
    verilog_assign=""
    for i in gate_list:
        tmp = gates[i]
        
        if i == 'NOT':
            for j in tmp:
                if((j[0] not in outputs) and (j[0] not in wires)):
                    verilog_wire +="wire {};".format(j[0])
                    wires.append(j[0])
                verilog_assign += "assign " + j[0]+" = ~"+j[1]+" ;"
        elif i == 'BUF':
            for j in tmp:
                if((j[0] not in outputs) and (j[0] not in wires)):
                    verilog_wire +="wire {};".format(j[0])
                    wires.append(j[0])
                verilog_assign += "assign " + j[0]+" = "+j[1]+" ;"
        elif i == "AND":
            for j in tmp:
                if((j[0] not in outputs) and (j[0] not in wires)):
                    verilog_wire +="wire {};".format(j[0])
                    wires.append(j[0])
                verilog_assign += "assign " + j[0]+" = "+j[1]+" & "+j[2]+" ;"
        elif i == "NAND":
            for j in tmp:
                if((j[0] not in outputs) and (j[0] not in wires)):
                    verilog_wire +="wire {};".format(j[0])
                    wires.append(j[0])
                verilog_assign += "assign " + j[0]+" = ~("+j[1]+" & "+j[2]+") ;"
        elif i == "OR":
            for j in tmp:
                if((j[0] not in outputs) and (j[0] not in wires)):
                    verilog_wire +="wire {};".format(j[0])
                    wires.append(j[0])
                verilog_assign += "assign " + j[0]+" = "+j[1]+" | "+j[2]+" ;"
        elif i == "NOR":
            for j in tmp:
                if((j[0] not in outputs) and (j[0] not in wires)):
                    verilog_wire +="wire {};".format(j[0])
                    wires.append(j[0])
                verilog_assign += "assign " + j[0]+" = ~("+j[1]+" | "+j[2]+") ;"
        elif i == "XOR":
            for j in tmp:
                if((j[0] not in outputs) and (j[0] not in wires)):
                    verilog_wire +="wire {};".format(j[0])
                    wires.append(j[0])
                verilog_assign += "assign " + j[0]+" = "+j[1]+" ^ "+j[2]+" ;"
        elif i == "XNOR":
            for j in tmp:
                if((j[0] not in outputs) and (j[0] not in wires)):
                    verilog_wire +="wire {};".format(j[0])
                    wires.append(j[0])
                verilog_assign += "assign " + j[0]+" = ~("+j[1]+" ^ "+j[2]+") ;"
        elif i == "DFF":
            print(tmp)
            for j in tmp:
                verilog_assign += "reg {};always@(posedge {})begin {}<={}; end ".format(j[0],clkpin,j[0],j[1])


    verilog += verilog_wire + verilog_assign + "endmodule"

    
    # verilog = utils.format_verilog(verilog)
    return verilog, gate_count


####################################################################################################################################
####################################################################################################################################


def verilog_to_bench(verilog,gate_mapping,gates_vlib,FF_vlib):
    verilog = format_verilog(verilog)
    inputs,_=extract_io_v(verilog,mode="input")
    outputs,_=extract_io_v(verilog,mode="output")
    
    gate_tech,sub_module,(FF_tech,Clock_pins,Reset_pins)=gates_module_extraction(verilog,gate_mapping,gates_vlib,FF_vlib)

    bench=""

    for i in inputs:
        tmpi=inputs[i]
        if(tmpi["bits"]==1):
            bench+="INPUT({})\n".format(i)
        else:
            for k in range(tmpi['startbit'],tmpi['endbit']+1):
                bench+="INPUT({})\n".format(i+f"[{k}]")

        
    for i in outputs:
        tmpi=outputs[i]
        if(tmpi["bits"]==1):
            bench+="OUTPUT({})\n".format(i)
        else:
            for k in range(tmpi['startbit'],tmpi['endbit']+1):
                bench+="OUTPUT({})\n".format(i+f"[{k}]")

    
    # for i in gates:
    #     if(i=='BUF' or i=='NOT'):
    #         for j in gates[i]:
    #             bench+="{} = {}({})\n".format(j[1],i,j[0])
    #     else:
    #         for j in gates[i]:
    #             bench+="{} = {}({},{})\n".format(j[2],i,j[0],j[1])
    return bench


