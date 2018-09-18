''' component_class.py written by Rachel Sassella, Spring 2017.
The component class describes the structure and characteristics of circuit components
(voltage sources, resistors, inductors, and capacitors) appropriate for use in Ngspice
netlists. Each component is described by its name, its value, and the two nodes that
bracket its position. A component must recieve all this information as inputs in order
to be instantiated correctly.
'''

class Component:

    def __init__(self, name, topnode, bottomnode, value):
        self.name = name    #When I generate a component, it needs name (ex R1, C23)
        self.value = value
        self.topnode = topnode
        self.bottomnode = bottomnode

    def __str__(self):
        return '{} {} {} {}'.format(self.name, self.topnode, self.bottomnode, self.value)
        # all characteristics of the component are returned
        # ready to be written to the netlist file!

    def __repr__(self):
        return str(self)
