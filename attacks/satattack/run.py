import argparse
import time

# python3 /home/alira/FYP/sat_attack/run.py /home/alira/FYP/tmp/tmprtl.v /home/alira/FYP/tmp/ortl.v

# python3 /home/alira/FYP/sat_attack/run.py /home/alira/FYP/linux/CSAW/ASSURE_LOCKED/design1/design1.bench /home/alira/FYP/linux/CSAW/ASSURE_LOCKED/design1/oracle1.bench b

# python3 /home/alira/FYP/sat_attack/run.py /home/alira/FYP/tmp.bench /home/alira/FYP/tmp2.bench b

import sat_attack

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform a SAT attack on a locked circuit.")
    parser.add_argument("locked_ckt", help="The locked benchmark file")
    parser.add_argument("oracle", help="The unlocked benchmark file")
    parser.add_argument("file_type", help="The benchmark file type (v or b)")

    args = parser.parse_args()

    attack = sat_attack.SatAttack(args.locked_ckt, args.oracle,args.file_type)

    start = time.time()
    attack.run()
    end = time.time()

    print("\nIterations: %i" % (attack.iterations))
    print("Elapsed time: %.3fs" % (end - start))

