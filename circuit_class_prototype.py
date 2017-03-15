# I want to create a class for building up circuits component by component
import component_class_prototype as comp
import copy


class Circuit:

    def __init__(self, list1 = None, list2 = None):

        self.source = comp.Component('V1', 1, 0, 'sin(0 1 1e6)')
        self.netlist = []
        if list1 != None and list2 != None:
            for l in list1:
                self.netlist.append(l)
            for l in list2:
                self.netlist.append(l)
        elif (list1 == None) != (list2 == None):
            print "ERROR: empty lists cannot be added to netlists"
        else:
            self.netlist = [self.source]

    def add_component_series(self, name, lastnodenum, value):
        new_node_num = str(int(lastnodenum) + 1)
        new_obj = comp.Component(name, lastnodenum, new_node_num, value)

        #TODO I need to connect the new node to ground somehow. If there is no parallel component,
        # it needs to have a wire put it to ground.

        self.netlist.append(new_obj)
        return new_node_num     # do I also need to return the netlist...?

    def add_component_parallel(self, name, lastnodenum, value):
        new_obj = comp.Component(name, lastnodenum, '0', value)
        #print(new_obj)
        self.netlist.append(new_obj)
        return  # do I need to return the netlist?

    def rename(self, component_name):
        dig = []
        let = []
        for char in component_name:
            if char.isdigit():
                dig.append(char)
            else:
                let.append(char)
        dig = "".join(dig)
        let = "".join(let)
        dig = str(int(dig) + 1)
        let = [let, dig]
        my_name = "".join(let)
        return my_name

    def serialize(self, comp_name):
        for element in self.netlist:
            if element.name == comp_name:
                component = element
        new_comp = copy.deepcopy(component)
        new_comp.name = self.rename(component.name)
        bot = component.bottomnode
        new_top = bot
        new_bot = str(int(bot) + 1)
        new_comp.topnode = new_top
        new_comp.bottomnode = new_bot
        #print new_comp
        #print component
        self.netlist.append(new_comp)
        return

    def parallelize(self, comp_name):
        for element in self.netlist:
            #print 'element', element
            if element.name == comp_name:
                component = element
        new_comp = copy.deepcopy(component)
        my_name = component.name
        new_comp.name = self.rename(my_name)

        self.netlist.append(new_comp)
        return

    def half_func(self):
        l = len(self.netlist)
        return self.netlist[0:l/2], self.netlist[l/2:l]

    def check_nums(self):
        for i in range(len(self.netlist)):
            templist = copy.deepcopy(self.netlist)
            stat_element = templist.pop(i)
            for j in range(len(templist)):
                dynamic_element = templist[j]
                if stat_element.name == dynamic_element.name:
                    letter = dynamic_element.name[0]
                    num = int(dynamic_element.name[1:len(dynamic_element.name)])
                    rest = str(num+1)
                    new_name = letter, rest
                    new_name = "".join(new_name)
                    if j < i:
                        net_index = j
                    else:
                        net_index = j + 1
                    self.netlist[net_index].name = new_name
        return

    def __repr__(self):
        return str(self)

    def __str__(self):
        this_list = "".join(str(self.netlist))
        return this_list
