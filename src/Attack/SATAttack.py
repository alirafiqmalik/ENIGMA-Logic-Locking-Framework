import re
import z3
import time
import argparse
import src.Attack.attacks.satattack.circuit as circuit
import src.Attack.attacks.satattack.sat_model as sat_model
import src.Attack.attacks.satattack.benchmarks as benchmarks
import src.Attack.attacks.satattack.dip_finder as dip_finder
import src.Attack.attacks.satattack.oracle_runner as oracle_runner


class SatAttack:
    """The main class for conducting the SAT attack."""

    def __init__(self, locked_filename, unlocked_filename,file_type):
        self.locked_filename = locked_filename
        self.unlocked_filename = unlocked_filename
        self.file_type=file_type
        self.iterations = 0

    def run(self):
        """Run the SAT attack."""
        # print("Reading in locked circuit...")

        if(self.file_type=='b'):
            self.nodes, self.output_names = benchmarks.read_nodes_b(self.locked_filename)
        elif(self.file_type=='v'):
            self.nodes, self.output_names = benchmarks.read_nodes_v(self.locked_filename)

        # print("Reading in unlocked circuit...")

        self.oracle_ckt = benchmarks.read_ckt(self.unlocked_filename,self.file_type)


        key_inputs = [node.name for node in self.nodes.values() if node.type == "Key Input"]
        primary_inputs = [node.name for node in self.nodes.values() if node.type == "Primary Input"]

        # for i in self.nodes:
        #     print(i)
        # print("\n# Primary Inputs: %i" % (len(primary_inputs)))
        # print("# Key Inputs: %i" % (len(key_inputs)))

        finder = dip_finder.DipFinder(self.nodes, self.output_names)
        runner = oracle_runner.OracleRunner(self.oracle_ckt)

        oracle_io_pairs = []
        
        while finder.can_find_dip():
            dip = finder.find_dip()
            oracle_output = runner.run(dip)
            # print(dip)
            # print(oracle_output)
            finder.add_constraint(dip, oracle_output)

            oracle_io_pairs.append((dip, oracle_output))
            self.iterations += 1

        key = self._find_key(oracle_io_pairs, key_inputs)
        self.key=key
        # print(key)
        # expected_key = benchmarks.get_expected_key(self.locked_filename)

        # print("\nExpected key: %s" % (self._key_string(expected_key)))
       

        # print("\nChecking for circuit equivalence...\n")
        self._check_key(key)
        if self._check_key(key):
            # print("Locked and unlocked circuits match")
            print("%s" % (self._key_string(key)))
        else:
            print("-1")

    def _find_key(self, oracle_io_pairs, key_names):
        """
        Find a key that satisfies all DIPs found during the SAT attack.
        This key will be in the set of correct keys.

        oracle_io_pairs: array of dip/output pairs in the form of (dip, output)

        returns: key that satisfies all dip constraints
        """

        s = z3.Solver()

        for io_pair in oracle_io_pairs:
            dip = io_pair[0]
            output = io_pair[1]

            constraint_ckt = circuit.Circuit.specify_inputs(dip, self.nodes, self.output_names)
            output_constraints = [constraint_ckt.outputs()[name] == output[name] for name in output.keys()]

            s.add(*output_constraints)

        s.check()
        # print("######################################## ERROR #####################################")
        # print(s)
        model = s.model()
        key = sat_model.extract_from_model(model, key_names, completion=True)
        return key

    def _check_key(self, key):
        """
        Check that the key returned from the SAT attack is correct. It
        does this by creating a miter circuit with a locked version
        and an oracle. If the diff signal returned from the miter circuit
        cannot be True, then the circuits are equivalent.

        key: the key returned from the SAT attaack
        """

        locked_ckt = circuit.Circuit.specify_inputs(key, self.nodes, self.output_names)
        miter = circuit.Circuit.miter(locked_ckt, self.oracle_ckt)

        s = z3.Solver()
        s.add(miter.outputs()["diff"] == True)

        return s.check() == z3.unsat


    def _key_string(self, key):
        def x(name):
            tmp=re.findall("[\d]+",name)
            # print("TMP",tmp)
            if (tmp!=[]):
                return int(tmp[0])
                # return tmp
            else:
                return 0
        ordered_names = sorted(key.keys(), key=x,reverse=True)
        # print(key.keys())
        # print(ordered_names)
        for i in ordered_names[:-1]:
            print(i,end=" ")
        
        # print(ordered_names[-1])
        
        key_string = ""

        for name in ordered_names:
            if key[name]:
                key_string += "1"
            else:
                key_string += "0"

        return key_string






# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Perform a SAT attack on a locked circuit.")
#     parser.add_argument("locked_ckt", help="The locked benchmark file")
#     parser.add_argument("oracle", help="The unlocked benchmark file")
#     parser.add_argument("file_type", help="The benchmark file type (v or b)")

#     args = parser.parse_args()

#     attack = SatAttack(args.locked_ckt, args.oracle,args.file_type)

#     start = time.time()
#     attack.run()
#     end = time.time()

    # print("\nIterations: %i" % (attack.iterations))
    # print("Elapsed time: %.3fs" % (end - start))