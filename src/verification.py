from src.utils import format_verilog_org,extract_io_v,get_difference_abs
import re


####################################################################################################################################
####################################################################################################################################
# testbench="`include \"{top_module}.v\" `timescale 1ns/10ps \n module {testbench_module}();integer count; {cir_inputs} reg clk;wire [{outputlength}:0] Q;wire Z;integer file;initial begin file = $fopen(\"{log_path}\", \"w\"); clk = 0;forever begin #5 clk = ~clk;end end initial begin repeat ({outerloop}) begin {{{key_inputs_p}}} =$random;$fwrite(file, \"iteration\\n\");$fwrite(file, \"keyinputs,Inputs,Q,Z\\n\");count=0;repeat ({innerloop}) begin {{{cir_inputs_p}}} =$random; #10;if(Z==0) begin count=count+1; end $fwrite(file, \"%b,%b,%b,%b\\n\", {{{key_inputs_p}}}, {{{cir_inputs_p}}}, Q, Z);end $fwrite(file, \"OER:, %f\\n\",count*100/{innerloop});end $finish;$fclose(file); end {top_module} dut (.Q(Q),.Z(Z),{top_port});endmodule"
# "`include \"{top_module}.v\" `timescale 1ns/10ps \n module {testbench_module}();integer count;reg {key_inputs_p};reg {cir_inputs_p};reg clk;wire [{outputlength}:0] Q;wire Z;integer file;initial begin file = $fopen(\"{log_path}\", \"w\");$fwrite(file, \"keyinputs,Inputs,Q,Z\n\"); clk = 0;forever begin #5 clk = ~clk;end end initial begin repeat (5) begin {{{key_inputs_p}}} =$random;repeat (10) begin {{{cir_inputs_p}}} =$random; #10;if(Z==1) count=count+1;$fwrite(file, \"%b,%b,%b,%b\\n\", {{{key_inputs_p}}}, {{{cir_inputs_p}}}, Q, Z);end end $finish;$fclose(file); end {top_module} dut (.Q(Q),.Z(Z),{top_port});endmodule"

testbench="`timescale 1ns/10ps module {testbench_module}();integer count,xc; {cir_inputs}reg clk;wire [{outputlength}:0] Q;wire Z;integer file;initial begin file = $fopen(\"{log_path}\", \"w\");clk = 0;forever begin #5 {clock_pins} clk = ~clk;end end initial begin xc=0;repeat ({outerloop}) begin if(xc<=2)begin {{{key_inputs_p}}} ={key_bit_count}'b{key_bit_val};$fwrite(file, \"iteration with Correct key \\n\");end else begin {{{key_inputs_p}}} =$random;$fwrite(file, \"iteration \\n \");end $fwrite(file, \"keyinputs,Inputs,Q,Z \\n\"); count=0;xc=xc+1;repeat ({innerloop}) begin {{{cir_inputs_p}}} =$random;#10;if(Z==0) begin count=count+1;end $fwrite(file, \"%b,%b,%b,%b \\n\", {{{key_inputs_p}}}, {{{cir_inputs_p}}}, Q, Z);end $fwrite(file, \"OER:, %f \\n \",count*100/{innerloop});end $finish;$fclose(file);end {top_module} dut (.Q(Q),.Z(Z),{top_port});endmodule"
# r"`include '{top_module}.v' `timescale 1ns/10ps module {testbench_module}();integer count,xc; {cir_inputs}reg clk;wire [{outputlength}:0] Q;wire Z;integer file;initial begin file = $fopen('{log_path}', 'w');clk = 0;forever begin #5 clk = ~clk;end end initial begin xc=0;repeat ({outerloop}) begin if(xc==0){{{key_inputs_p}}} ={key_bit_count}'b{key_bit_val};{{{key_inputs_p}}} =$random;$fwrite(file, 'iteration');$fwrite(file, 'keyinputs,Inputs,Q,Z \n');count=0;xc=xc+1;repeat ({innerloop}) begin {{{cir_inputs_p}}} =$random;#10;if(Z==0) begin count=count+1;end $fwrite(file, '%b,%b,%b,%b \n', {{{key_inputs_p}}}, {{{cir_inputs_p}}}, Q, Z);end $fwrite(file, 'OER:, %f \n\n',count*100/{innerloop});end $finish;$fclose(file);end {top_module} dut (.Q(Q),.Z(Z),{top_port});endmodule"
def gen_miter_testbench(key_inputs_p,
                        key_bit_count,
                        key_bit_val,
                        cir_inputs,
                        cir_inputs_p,
                        Clock_pins,
                        top_port,
                        outputlength,
                        testbench_module="testbench",
                        top_module="top",
                        log_path="logfile.txt"):
    
    clk_txt=""
    for i in Clock_pins:
        clk_txt+=f"assign {i}=clk;\n"
        cir_inputs_p=re.sub(i+",?","",cir_inputs_p)
    
    # print("hh ",cir_inputs_p)
        
    

    # Clock_pins=Clock_pins
        # reg {cir_inputs_p}
    return testbench.format(testbench_module=testbench_module,
                            top_module=top_module,
                            key_bit_count=key_bit_count,
                            key_bit_val=key_bit_val,
                            outputlength=outputlength,
                            key_inputs_p=key_inputs_p,
                            clock_pins=clk_txt,
                            cir_inputs=re.sub("(^|\n)input","reg",cir_inputs),
                            cir_inputs_p=cir_inputs_p,
                            log_path=log_path,
                            top_port=top_port,
                            innerloop=500,
                            outerloop=500
                            )

def gen_miterCircuit(verilog,verilogLL,gatemodules,top,key,Clock_pins):
    LLinp,LLport_i=extract_io_v(verilogLL)
    # print("here  ",LLport_i,LLinp)
    LLout,LLport_o=extract_io_v(verilogLL,mode="output")
    Uinp,Uport_i=extract_io_v(verilog)

    miter_circuit="module {topname}({inputport}{outputport});\n".format(topname="top",inputport=LLport_i,outputport="Q,Z")
    cir_inputs=""
    for i in LLinp:
        tmpi=LLinp[i]
        if(tmpi['bits']==1):
            cir_inputs+=f"input {i};\n"
        else:
            cir_inputs+=f"input [{tmpi['endbit']}:{tmpi['startbit']}] {i};\n"
    
    miter_circuit+=cir_inputs

        # miter_circuit+="input {};\n".format(LLport_i[:-1])
    # miter_circuit+="output {};\n".format(LLport_o[:-1])

    keyinputs=get_difference_abs(LLinp,Uinp)
    # print(keyinputs['bits'])
    # keyinputs.sort(key=lambda x:re.findall(r"\d+",x)[0],reverse=True)
    keyporti=""
    keyports=""
    for i in keyinputs:
        keyporti+=".{}({}),".format(i,i)
        keyports+="{},".format(i)

    orgport_i=""
    orgport_o=""
    encport_o=""
    compare_o=""
    compare_Z="assign Z= "
    for i in Uinp:
        orgport_i+=".{}({}),".format(i,i)

    count=0
    for i in LLout:
        tmpi=LLout[i]
        orgport_o+=".{}({}),".format(i,i+"_org")
        encport_o+=".{}({}),".format(i,i+"_enc")
        if(tmpi['bits']==1):
            compare_o+="assign {}={}=={};\n".format("Q[{}]".format(count),i+"_enc",i+"_org")
            compare_Z+="Q[{}]&".format(count)
            count+=1
            miter_circuit+=f"wire {i}_enc, {i}_org;\n"
        else:
            miter_circuit+=f"wire [{tmpi['endbit']}:{tmpi['startbit']}] {i}_enc, {i}_org;\n"
            # print(f"wire [{tmpi['endbit']}:{tmpi['startbit']}] {i}_enc, {i}_org;\n")
            for j in range(tmpi['startbit'],tmpi['endbit']+1):
                compare_o+="assign {}={}=={};\n".format("Q[{}]".format(count),f"{i}_enc[{j}]",f"{i}_org[{j}]")
                compare_Z+="Q[{}]&".format(count)
                count+=1


    compare_o="output Z;\noutput [{}:0]Q;\n".format(count-1)+compare_o
    compare_o+=compare_Z[:-1]+";\n"

    
    miter_circuit+="orgcir org({});\n".format(orgport_i+orgport_o[:-1])
    miter_circuit+="enccir enc({});\n".format(orgport_i+keyporti+encport_o[:-1])
    miter_circuit+=compare_o

    miter_circuit+="endmodule\n\n\n\n"

    

    miter_circuit+=re.sub(r"module "+top+"\(","module enccir(",verilogLL)+"\n\n\n\n"

    miter_circuit+=re.sub(r"module "+top+"\(","module orgcir(",verilog)


    # gatemodules=open("./vlib/mycells.v").read()

    miter_circuit+=gatemodules

    # print(LLinp[keyinputs[0]]['bits'])
    # print(cir_inputs)

    # print(print(Uport_i[:-1]))

    
    
    miter_testbench=gen_miter_testbench(key_inputs_p=keyports[:-1],
                                        key_bit_count=LLinp[keyinputs[0]]['bits'],
                                        key_bit_val=key,
                                        cir_inputs=cir_inputs,
                                        Clock_pins=Clock_pins,
                                        cir_inputs_p=Uport_i[:-1],
                                        top_port=orgport_i+keyporti[:-1],
                                        outputlength=count-1,
                                        testbench_module="testbench",
                                        top_module="top",
                                        log_path="logfile.txt",
                                        )

    miter_testbench=format_verilog_org(miter_testbench)
    return miter_circuit,miter_testbench
