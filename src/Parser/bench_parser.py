import re
from src.utils import sortio


bench_gates=['DFF','BUF','NOT', 'AND', 'OR', 'NAND', 'NOR','XOR','XNOR']

####################################################################################################################################
####################################################################################################################################
def extract_gates_b(bench):
    tmp={i:[] for i in bench_gates}
    matches = re.findall(r"(\w+)\s*=\s*(\w+)\((.*?)\)", bench, re.MULTILINE)
    output_list = [(match[0], match[1], *re.findall(r"G\d+", match[2])) for match in matches]

    tmp={i:[] for i in bench_gates}
    for i in output_list:
        if i[1].upper()=='NOT' or i[1].upper()=='BUF' or i[1].upper()=='DFF':
            tmp[i[1].upper()].append((i[0],i[2]))
            pass
        elif i[1].upper() in bench_gates:
            tmp[i[1].upper()].append((i[0],i[2:]))
    
    gate_count = {i: len(tmp[i]) for i in tmp}
    
    return tmp,gate_count

def extract_io_b(bench,mode="input"):
    tmp=re.findall(mode.upper()+r"\((.*)\)",bench)
    sortio(tmp)
    return tmp