import os
import subprocess
from src.path_var import *
import src.utils as utils

def verify_verilog(path,top):
  cmd = """
     {yosys_path} -q -p'
      read_verilog {path}
      hierarchy -check -top {top}
      '
  """
  path=f"\"{path}\""
  result = subprocess.run(cmd.format(yosys_path=yosys_path,path=path,top=top), shell=True)
  if(result.returncode==1):
    print(result)
    raise Exception("Error code 1\nVerilog Code Syntax Error")
  elif(result.returncode==0):
    return True
    # print("Verilog Code Working Without Error")
  else:
    print(result)
    raise Exception(f"Unknown Error Code {result.returncode}")


def synthesize_verilog(verilog, top,flag = "flatten"):
    with open("./tmp/tmp_syn1.v", "w") as f:
        f.write(verilog)
    file_name=f"{top}_2_{flag}.v"
    output_file_path=f"./tmp/{file_name}"
    output_file_path2=f"./tmp/{top}_unformated.v"
    readin="read_verilog ./tmp/tmp_syn1.v"
    
    if(os.path.isfile(output_file_path)):
        print(f"File Already Synthesize, Delete file in tmp to re-synthesize file {file_name}")
    else:
        if flag == "flatten":
            cmd = """
                {yosys_path} -q -p'
                {readin}
                hierarchy -check -top {module_name}
                proc; opt; fsm; opt; memory; opt;
                techmap; opt
                flatten
                opt_clean -purge
                dfflibmap -liberty ./vlib/mycells.lib
                abc -liberty ./vlib/mycells.lib  
                opt_clean -purge
                write_verilog -noattr {out_file}
                write_verilog -noattr {out_file2}
                '
            """
            
        elif flag == "dont_flatten":
            cmd = """
                {yosys_path} -q -p'
                {readin}
                hierarchy -check -top {module_name}
                proc; opt; fsm; opt; memory; opt;
                techmap; opt
                dfflibmap -liberty ./vlib/mycells.lib
                abc -liberty ./vlib/mycells.lib 
                opt_clean -purge
                write_verilog -noattr {out_file}
                write_verilog -noattr {out_file2}
                '
            """
        else:
            Exception("Enter either 'flatten' or 'don't flatten' ")
        # Run the command and capture the output
        
        
        result=subprocess.run(cmd.format(yosys_path=yosys_path,module_name=top,out_file=output_file_path,out_file2=output_file_path2,readin=readin), shell=True)

        if(result.returncode==1):
            raise Exception("Error code 1\nVerilog Code Syntax Error or yosys Path not found")
        elif(result.returncode==0):
            pass
            # print("Verilog Code Working Without Error")
        else:
            raise Exception(f"Unknown Error Code {result.returncode}")
        
    
    synthesized_verilog = open(output_file_path, "r").read()
    synthesized_verilog = utils.format_verilog(synthesized_verilog)

    with open(output_file_path,"w") as f:
        f.write(synthesized_verilog)
    #os.remove("./tmp/tmp_syn1.v")
    #os.remove("./tmp/tmp_syn2.v")

    return synthesized_verilog












def synthesize_verilog_flatten_gate(verilog, top):
    filesintmp=os.listdir("./tmp")
    if("tmp_syn2.v" in filesintmp):
        print("File already exists, Returning Old File")
        return open("./tmp/tmp_syn2.v").read()
         
    with open("./tmp/tmp_syn2.v", "w") as f:
        f.write(verilog)
    file_name=f"{top}_outgatelevel_flatten.v"
    output_file_path=f"./tmp/{file_name}"
    output_file_path2=f"./tmp/{top}_unformated.v"
    readin="read_verilog ./tmp/tmp_syn2.v"
    
    cmd = """
        {yosys_path} -q -p'
        {readin}
        hierarchy -check -top {module_name}
        proc; opt; fsm; opt; memory; opt;
        techmap; opt
        flatten
        opt_clean -purge
        write_verilog -noattr {out_file}
        write_verilog -noattr {out_file2}
        '
    """
        
    result=subprocess.run(cmd.format(yosys_path=yosys_path,module_name=top,out_file=output_file_path,out_file2=output_file_path2,readin=readin), shell=True)

    if(result.returncode==1):
        raise Exception("Error code 1\nVerilog Code Syntax Error or yosys Path not found")
    elif(result.returncode==0):
        pass
        # print("Verilog Code Working Without Error")
    else:
        raise Exception(f"Unknown Error Code {result.returncode}")
    
    
    synthesized_verilog = open(output_file_path, "r").read()
    synthesized_verilog = utils.format_verilog_org(synthesized_verilog)

    with open(output_file_path,"w") as f:
        f.write(synthesized_verilog)
    
    return synthesized_verilog



# def synthesize_bench(bench):
#     text_file = open("./tmp/tmp_syn1.bench", "w")
#     text_file.write(bench)
#     text_file.close()
    
#     cmd = """
#         ~/FYP/linux/yosys/build/yosys-abc'
#         read_bench ./tmp/tmp_syn1.bench
#         write_bench -l ./tmp/tmp_syn2.bench
#         '
#     """
#     synthesized_verilog = open(f"./tmp/tmp_syn2.v", "r").read()
#     synthesized_verilog = format_verilog(synthesized_verilog)
#     with open(f"./tmp/tmp_syn2.v","w") as f:
#         f.write(synthesized_verilog)
#     #os.remove("./tmp/tmp_syn1.v")
#     #os.remove("./tmp/tmp_syn2.v")
#     return synthesized_verilog
