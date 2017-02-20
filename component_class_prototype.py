# I want to create a class for adding components

class Component:

    def __init__(self, name, topnode, bottomnode, value):
        self.name = name    #When I generate a component, it needs name (ex R1, C23)
        # Not sure how to assign this name
        self.value = value
        self.topnode = topnode
        self.bottomnode = bottomnode

    def __str__(self):
        return '{} {} {} {}'.format(self.name, self.topnode, self.bottomnode, self.value)

    def __repr__(self):
        return str(self)

    #def mutate():
