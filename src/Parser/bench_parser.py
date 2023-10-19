import re
from src.utils import sortio


bench_gates=['DFF','BUF','NOT', 'AND', 'OR', 'NAND', 'NOR','XOR','XNOR']

####################################################################################################################################
####################################################################################################################################
def extract_gates_b(bench):
    tmp={i:[] for i in bench_gates}
    matches = re.findall(r"(.+)\s*=\s*(.+)\((.*?)\)", bench, re.MULTILINE)
    output_list = [(match[0], match[1], *match[2].split(",")) for match in matches]

    for i in output_list:
        if i[1].upper()=='NOT' or i[1].upper()=='BUF' or i[1].upper()=='DFF':
            tmp[i[1].strip().upper()].append((i[0].strip(),i[2].strip()))
            pass
        elif i[1].upper() in bench_gates:
            tmpl=[i[0].strip()]+[k.strip() for k in i[2:]]
            tmp[i[1].strip().upper()].append(tmpl)
        else:
            raise Exception("Something is wrong here")
    
    gate_count = {i: len(tmp[i]) for i in tmp}
    return {key:val for key,val in tmp.items() if(val)},gate_count

def extract_io_b(bench,mode="input"):
    tmp=re.findall(mode.upper()+r"\((.*)\)",bench)
    sortio(tmp)
    return tmp