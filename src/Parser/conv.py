from src.Parser.verilog_parser import extract_io_v,extract_gates_v
from src.Parser.bench_parser import extract_gates_b,extract_io_b
from src.utils import format_verilog,io_port

gate_to_assign={'BUF':'','NOT':'~', 'AND':'&', 'OR':'|','XOR':'^','NAND':'&', 'NOR':'|','XNOR':'^'}


def bench_to_verilog(bench,clkpin="Clock",modulename="top"):
    gates,gate_count = extract_gates_b(bench)
    # print("HERE ",gates)
    inputs = extract_io_b(bench, mode="input")
    outputs = extract_io_b(bench, mode="output")

    gate_list = list(gates.keys())

    print("tmpcheck",gates["DFF"])
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

    # clock=""
    # if("DFF" in gate_list):
    #     for k in inputs:
    #         if(("clk" in k.lower()) or ("clock" in k.lower())):
    #             clock=k
    #     if(clock==""):
    #         print("################### ERROR ###################")
        
    #     for i in gates["DFF"]:
    #         verilog += "reg "+i[0]+" ;"

    #     verilog+="always@(posedge {})begin ".format(clock)
    #     for i in gates["DFF"]:
    #         verilog += i[0]+" = "+i[1]+" ;"
    #     verilog+=" end "
        

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

    
    verilog = format_verilog(verilog)
    return verilog, gate_count



####################################################################################################################################
####################################################################################################################################


def verilog_to_bench(verilog,gate_mapping):
    verilog = format_verilog(verilog)
    inputs,_=extract_io_v(verilog,mode="input")
    outputs,_=extract_io_v(verilog,mode="output")
    
    gates,gate_count=extract_gates_v(verilog,gate_mapping)

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

    
    for i in gates:
        if(i=='BUF' or i=='NOT'):
            for j in gates[i]:
                bench+="{} = {}({})\n".format(j[1],i,j[0])
        else:
            for j in gates[i]:
                bench+="{} = {}({},{})\n".format(j[2],i,j[0],j[1])
    return bench


