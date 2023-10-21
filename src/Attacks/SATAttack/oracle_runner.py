from attacks.satattack.circuit_solver import solve_ckt

class OracleRunner:
  def __init__(self, ckt,bin=False):
    self.ckt = ckt

  def run(self, inputs):
    """Run a set of inputs against the oracle"""
    return solve_ckt(self.ckt, inputs)

  def run_bin(self, inputs):
    print(inputs)
    ''.join([str(int(i)) for i in inputs])
    """Run a set of inputs against the oracle"""
    return solve_ckt(self.ckt, inputs)
