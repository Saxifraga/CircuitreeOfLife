# I want to create a class for building up circuits component by component

class Circuit(object):

    def __init__(self):
        self.netlist = []
        self.source = 'vin 1 0 0.0 ac 1.0 sin(0 1 1k)'
