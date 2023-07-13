class Node():
    def __init__(self, name, inputs, type2):
        self.name = name
        self.inputs = inputs
        self.type = type2
        self.z3_repr = None
        # print("HERE = ",name,"-",inputs,"-",type2)
        # print("THERE = ",type(name),type(inputs),type(type2))

    def __str__(self):
        return "<" + str(self.name) + ": " + str(self.type) + " " + str(self.inputs) + ">"

    def __repr__(self):
        return "<" + str(self.name) + ": " + str(self.type) + " " + str(self.inputs) + ">"


class DFF:
  def __init__(self,outputQ,inputD,Clock,Reset):
    self.inputD=inputD
    self.name=outputQ
    self.Clock=Clock
    self.Reset=Reset
    self.type2="DFF"
    self.z3_repr = None
    self.Clock_curr=False
    self.Clock_prev=False

  def syncronous_update(self):
    self.Clock_curr=self.Clock.value()
  
  def __str__(self):
    return "<" + str(self.name) + ": " + str(self.type2) + " " + str(self.inputD) + ">"

  def __repr__(self):
    return "<" + str(self.name) + ": " + str(self.type2) + " " + str(self.inputD) + ">"


    