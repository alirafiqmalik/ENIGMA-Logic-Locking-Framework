# Setup before running
Change yosys path in src/path_var.py to your path for yosys
 **if yosys is in build dir, give path to yosys bin file:**

yosys_path="~/FYP/linux/yosys/build/yosys"

 **if yosys is installed using apt, write yosys:**

yosys_path="yosys"


# Example Run

**To Create New Netlist File for Locking use:**
```
obj=AST(file_path="./input_files/tmporg.v",rw="w",flag="v",top="locked",filename="locked_new")
```

This reads verilog code from file "./input_files/tmporg.v" and creates a json file in output_files with name "locked_new" with top module "locked"


**Run this command once at start only , then using the following command afterwards:**

```
obj = AST(file_path="./output_files/locked_new.json",rw='r',top="locked",filename="locked") # r for read from file
```

This reads in the json file generated for original circuit

To save any changes, use obj.writeLLFile() which writes to a new json file filename="locked"


# Example Run of code after Initialing function

```
obj = AST(file_path="./output_files/locked_new.json",rw='r',filename="locked")


LL=PreSAT(obj.top_module)
LL.set_key(256,key=123121341221213213) # setting key for locking operation
# key integer val= key
# using locking techniques
# LL.RLL()
LL.SLL()

# obj.top_module.save_graph()  # saves graph in svg form in tmp dir but a little slow
obj.writeLLFile() # saves locked circuit to a new json file filename="locked"

```






<!-- # ##############################################################
# RUNNING SAT ATTACK
# For NOW
```
python3 /home/alira/FYP/sat_attack/run.py <locked> <unlocked> file_type(b or v)
Example
python3 /home/alira/FYP/sat_attack/run.py /home/alira/FYP/tmp/tmprtl.v /home/alira/FYP/tmp/ortl.v v
```
# ############################################################## -->
