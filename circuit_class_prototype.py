# I want to create a class for building up circuits component by component

class Circuit:

    def __init__(self):
        self.netlist = []
        self.source = 'V1 1 0 sin(0 1 1e6)'

    def add_component_series(name, lastnodenum, value):
        new_node_num = lastnodenum + 1
        new_obj = Component(name, lastnodenum, new_node_num, value)

        #TODO I need to connect the new node to ground somehow. If there is no parallel component,
        # it needs to have a wire put it to ground.

        self.netlist.append(new_obj)
        return new_node_num     # do I also need to return the netlist...?

    def add_component_parallel(component, lastnodenum, name, value):
        new_obj = Component(name, lastnodenum, 0, value)
        self.netlist.append(new_obj)
        return  # do I need to return the netlist?
