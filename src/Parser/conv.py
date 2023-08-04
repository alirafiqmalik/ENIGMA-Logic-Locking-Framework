import re
from src.Parser.verilog_parser import extract_io_v,gates_module_extraction
from src.Parser.bench_parser import extract_gates_b,extract_io_b
from src.utils import format_verilog,io_port,det_FF_node

gate_to_assign={'BUF':'','NOT':'~', 'AND':'&', 'OR':'|','XOR':'^','NAND':'&', 'NOR':'|','XNOR':'^'}


def bench_to_verilog_vlib(bench,vlib_var,clkpin="Clock",modulename="top"):
    gate_mapping_vlib,gates_vlib,FF_vlib=vlib_var
    bench=re.sub(" +"," ",bench)
    gates,gate_count = extract_gates_b(bench)
    inputs = extract_io_b(bench, mode="input")
    outputs = extract_io_b(bench, mode="output")

    gate_list = list(gates.keys())


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
    verilog_init=""

    for i in gate_list:
        Node = gates[i]
        if(i=="DFF"):
            for k in FF_vlib:
                inputs=FF_vlib[k]["inputs"]
                port=FF_vlib[k]["port"]
                if(len(inputs)==2):
                    template=FF_vlib[k]
            port=template["port"]
            inputs=template["inputs"]
            output=template["outputs"][0]
            module_name=k

            for j in Node:
                if((j[0] not in outputs) and (j[0] not in wires)):
                    verilog_wire +="wire {};".format(j[0])
                    wires.append(j[0])
                
                tmp={}
                for mIO in template["port_list"]:
                    type_node=det_FF_node(mIO)
                    if(type_node=="clock"):
                        tmp[mIO]=clkpin
                    elif(type_node=="inputs"):
                        tmp[mIO]=j[1]
                    elif(type_node=="outputs"):
                        tmp[mIO]=j[0]
                init_name=f"{i}_out_{j[0]}_"
                verilog_init+=f"{module_name} {init_name} {port.format(**tmp)}\n"
                
        else:
            template=gates_vlib[gate_mapping_vlib[i][0]]
            port=template["port"]
            inputs=template["inputs"]
            output=template["outputs"][0]
            module_name=gate_mapping_vlib[i][0]
            for j in Node:
                if((j[0] not in outputs) and (j[0] not in wires)):
                    verilog_wire +="wire {};".format(j[0])
                    wires.append(j[0])
                tmp={}
                for mIO,mNode in zip(inputs,j[1:]):
                    tmp[mIO]=mNode
                tmp[output]=j[0]

                formatted_out=re.sub(r"[^A-Za-z0-9]",r"",j[0])
                init_name=f"{i}_out_{formatted_out}_"
                verilog_init+=f"{module_name} {init_name} {port.format(**tmp)}\n"
                
    verilog += verilog_wire + verilog_init + "endmodule"
    return verilog, gate_count



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


