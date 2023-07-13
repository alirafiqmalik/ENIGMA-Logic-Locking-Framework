import subprocess

# subprocess.run("python3 /home/alira/FYP/sat_attack/cmd_sat.py /home/alira/FYP/tmp/obfi2.bench /home/alira/FYP/tmp/orgi2.bench b",shell=True)

keys={}
cmd="python3 /home/alira/FYP/sat_attack/cmd_sat.py /home/alira/FYP/tmp/obfi.bench /home/alira/FYP/tmp/orgi.bench b"
tmp=subprocess.run(cmd,shell=True,capture_output=True)
tx=tmp.stdout.decode("utf-8").split("\n")[:-1]
keynode=tx[0].split(" ")
keyval=tx[1]
if(len(keynode)==len(keyval)):
  for i in range(len(keyval)):
    if(keynode[i] not in keys):
      keys[keynode[i]]=keyval[i]
    else:
      keys[keynode[i]]=[keys[keynode[i]],keyval[i]]


cmd="python3 /home/alira/FYP/sat_attack/cmd_sat.py /home/alira/FYP/tmp/obfi.bench /home/alira/FYP/tmp/orgi.bench b"
tmp=subprocess.run(cmd,shell=True,capture_output=True)
tx=tmp.stdout.decode("utf-8").split("\n")[:-1]
keynode=tx[0].split(" ")
keyval=tx[1]
if(len(keynode)==len(keyval)):
  for i in range(len(keyval)):
    if(keynode[i] not in keys):
      keys[keynode[i]]=keyval[i]
    elif(keys[keynode[i]]!=keyval[i]):
      keys[keynode[i]]=[keys[keynode[i]],keyval[i]]



cmd="python3 /home/alira/FYP/sat_attack/cmd_sat.py /home/alira/FYP/tmp/obfi.bench /home/alira/FYP/tmp/orgi.bench b"
tmp=subprocess.run(cmd,shell=True,capture_output=True)
tx=tmp.stdout.decode("utf-8").split("\n")[:-1]
keynode=tx[0].split(" ")
keyval=tx[1]
if(len(keynode)==len(keyval)):
  for i in range(len(keyval)):
    if(keynode[i] not in keys):
      keys[keynode[i]]=keyval[i]
    elif(keys[keynode[i]]!=keyval[i]):
      keys[keynode[i]]=[keys[keynode[i]],keyval[i]]



cmd="python3 /home/alira/FYP/sat_attack/cmd_sat.py /home/alira/FYP/tmp/obfi2.bench /home/alira/FYP/tmp/orgi2.bench b"
tmp=subprocess.run(cmd,shell=True,capture_output=True)
tx=tmp.stdout.decode("utf-8").split("\n")[:-1]
# print(tx)
keynode=tx[0].split(" ")
keyval=tx[1]
if(len(keynode)==len(keyval)):
  for i in range(len(keyval)):
    if(keynode[i] not in keys):
      keys[keynode[i]]=keyval[i]
    elif(keys[keynode[i]]!=keyval[i]):
      keys[keynode[i]]=[keys[keynode[i]],keyval[i]]

print(keys)