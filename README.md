# Enigma Logic Locking Framework

Enigma is a logic locking framework designed for securing integrated circuits by inserting additional circuitry known as "logic locks." These locks protect against intellectual property theft and unauthorized modifications. Enigma provides a set of tools and techniques for implementing logic locking in Verilog designs.

## File Structure

The file structure of Enigma is organized as follows:


<pre>
input_files/
├── Benchmarks/
│   ├── demo.v
│   └── tmporg.v
├── src/
│   ├── Attack
│   │   ├── SATAttack.py
│   │   └── attacks/
│   │      └── satattack
│   ├── Locking
│   │   ├── LL.py
│   │   ├── PostSAT.py
│   │   └── PreSAT.py
│   ├── Netlist
│   │   ├── AST.py
│   │   └── netlist.py
│   ├── Parser
│   │    ├── verilog_parser.py
│   │    ├── bench_parser.py
│   │    └── conv.py
│   ├── Verification
│   │   └── verification.py
│   ├── path_var.py
│   ├── utils.py
├── tmp/ (temporary working directory)
├── vlib/
│   ├── mycells.v
│   └── mycells.lib
├── .gitattributes
├── .gitignore
├── README.md
└── main.py
</pre>


## Prerequisites

Before using Enigma, please ensure you have the following prerequisites installed:

- Yosys: Logic synthesis tool used by Enigma. Make sure to set the correct path to Yosys in `src/path_var.py`.

## Usage

To use Enigma, follow the example run commands provided below:

To create:

```python
from src.Netlist.AST import AST

obj = AST(file_path="./input_files/tmporg.v", rw="w", flag="v", top="locked", filename="locked_new")
```

This command reads the Verilog code from ./input_files/tmporg.v and creates a JSON file in the output_files directory named locked_new, with the top module set to "locked".

After the:
```python
obj = AST(file_path="./output_files/locked_new.json", rw='r', top="locked", filename="locked")
```

This command reads the JSON file generated for the original circuit.

To save modified netlist as JSON file, run:

```python
obj.writeLLFile()
```

Example Usage:

```python
from src.Netlist.AST import AST
from src.PreSAT import PreSAT

obj = AST(file_path="./output_files/locked_new.json", rw='r', filename="locked")
LL = PreSAT(obj.top_module)
LL.set_key(256, key=123121341221213213)  # Setting the key for locking operation
LL.RLL()
obj.writeLLFile()  # Saves the locked circuit to a new JSON file named "locked"
```

## Prerequisites Running SAT Attack
To perform a SAT attack, you can use the sat_attack/run.py script. Currently, you need to provide the file type (binary or Verilog) as an argument.

Example command:
```bash
python3 /path/to/enigma/sat_attack/run.py file_type(b or v)
```
For example, to run the attack on a Verilog file:

```bash
python3 /path/to/enigma/sat_attack/run.py /path/to/verilog_file.v v
```

## License
<!-- Enigma is released under the  License. See the LICENSE file for more details. -->



