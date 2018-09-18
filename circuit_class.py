'''circuit_class written by Rachel Sassella for her senior engineering project, Spring 2017.

The circuit class describes circuit objects, composed of lists of component objects. This
class was implemented for a genetic algorithm, so both circuits and components are meant
to be easy to change and manipulate. Methods in this class are mostly related to mutation of
individual components.
'''

import component_class as comp
import copy
import numpy as np
'''A circuit is either initialized with a voltage source and no other netlist components,
or it has two lists (halves of netlists) passed in, in which case it appends those to
the netlist instead'''

class Circuit:

    def __init__(self, list1 = None, list2 = None):
        self.source = comp.Component('V1', 1, 0, 'ac 1')    #every circuit needs a source
        self.netlist = []
        # lists are passed in for crossover
        if list1 != None:
            for l in list1:
                self.netlist.append(l)
            if list2 != None:
                for l in list2:
                    self.netlist.append(l)
        # elif (list1 == None) != (list2 == None):
        #     print "ERROR: empty lists cannot be added to netlists"
        else:
            self.netlist = [self.source]

    '''Adds a given component in series with the node 'lastnodenum'. All component values
    except for TOPNODE must be given as arguments'''
    def add_component_series(self, name, lastnodenum, value):
        new_node_num = str(int(lastnodenum) + 1)
        new_obj = comp.Component(name, lastnodenum, new_node_num, value)
        self.netlist.append(new_obj)
        return new_node_num     # returns the lastest node number

        '''Puts a given component in parallel with circuit, between the last node lastnodenum and
        the ground. All component values except for TOPNODE must be given as arguments'''
    def add_component_parallel(self, name, lastnodenum, value):
        new_obj = comp.Component(name, lastnodenum, '0', value)
        self.netlist.append(new_obj)
        return

        '''Increments the digit in a given component's name by 1. Ex: R1 -> R2, L43 -> L44.
        Useful for renumbering circuits. Returns the new name as a string'''
    def rename(self, component_name):
        dig = []
        let = []
        #separate the digits from the letters in the component name
        for char in component_name:
            if char.isdigit():
                dig.append(char)
            else:
                let.append(char)
        dig = "".join(dig)
        let = "".join(let)
        dig = str(int(dig) + 1) #increment the value by 1
        let = [let, dig]
        my_name = "".join(let)
        return my_name

    '''mutate() is one of the key methodss in the genetic algorithm. When it is called on a
    circuit object, it runs through each component and generates a random number. Based on the number,
    there's an 85 percent chance of an actual mutation occurring.
    No value is returned, but the circuit's netlist has been altered by the end.
    '''
    def mutate(self):
        for i in range(1,len(self.netlist)):
            n = np.random.randint(0,20)

            # Perform a component value mutation
            if n < 5 or n > 15:   #40% chance of numerical mutation
                element = self.netlist[i]
                val = element.value
                # split 'val' into letters and digits
                dig = []
                let = []
                for char in val:
                    if char.isdigit() or char == '.':
                        dig.append(char)
                    else:
                        let.append(char)
                dig = float("".join(dig))
                m = np.random.randint(0,2)
                #exponent = np.random.normal(0.0, 0.8)
                # add or subtract a random value from the numerical part of the component val
                if m == 0:
                    #dig += (np.random.random()*10**exponent)
                    dig += 1.5*np.random.random()
                elif m ==1:
                    #dig = abs(dig - (np.random.random()*10**exponent))
                    dig = 1.5*abs(dig - np.random.random())
                dig = str(dig)
                dig = [dig, let[0]]
                my_val = "".join(dig)
                element.value = my_val
            # topological mutation: 5% chance while netlist has fewer than 12 components
            # beware: for some reason, this elif likes to change indentation automatically
            elif n==15 and (len(self.netlist)<12):
                element = self.netlist[i]
                m = np.random.randint(0,2)
                if m == 0:
                    self.parallelize(element.name)
                elif m == 1:
                    self.serialize(element.name)
        # component type mutation (R L C), 40% chance
        #    # change name; if name before or name after is R,
            #change prefix on value (ex: .234k --> .234 u)
            elif n>4 and n<14:
                element = self.netlist[i]
                component_name = element.name

                dig = []
                let = []
                for char in component_name:
                    if char.isdigit():
                        dig.append(char)
                    else:
                        let.append(char)
                dig = "".join(dig)
                let = "".join(let)
                types = ['R', 'L', 'C']
                this_one = let
                # R might change to R, etc, so put in while loop till it changes properly
                while let == this_one:  #break out of loop when
                    g = np.random.randint(0,3)
                    this_one = types[g]
                let = this_one
                #dig = str(int(dig) + 1)
                let = [let, dig]
                my_name = "".join(let)
                element.name = my_name
                self.check_nums()
                self.unit_adjust(element.name)
        self.check_nums()
        return

    '''supporting function for component type mutation. If type changes, value prefix has to change
    to make sense. Ex: .04 kilo ohms shouldn't change to .04 kilofarads, but to .04 microfarads if
    R --> C'''
    def unit_adjust(self, comp_name):
        for element in self.netlist:
            if element.name == comp_name:
                component = element
                break
        name = component.name
        if name[0] == 'R':
            unit = 'k'
        else:
            unit = 'u'
        val = component.value
        # split 'val' into letters and digits
        dig = []
        let = []
        for char in val:
            if char.isdigit() or char == '.':
                dig.append(char)
            else:
                let.append(char)
        dig = "".join(dig)
        val = [dig, unit]
        val = "".join(val)
        component.value = val
        return

    '''Supporting function for topological mutations in mutation method. Takes an element name,
    finds element in netlist, copies it, and places the copy in series with the original'''
    def serialize(self, comp_name):
        for element in self.netlist:
            if element.name == comp_name:
                component = element
        # deepcopy is necessary so we don't just get the address
        new_comp = copy.deepcopy(component)
        new_comp.name = self.rename(component.name)
        bot = component.bottomnode
        new_top = bot   #topnode of copy is bottomnode of original
        new_bot = str(int(bot) + 1) #increment top bottomnode by one
        new_comp.topnode = new_top
        new_comp.bottomnode = new_bot
        self.netlist.append(new_comp)
        return

    '''Supporting function for topological mutations in mutation method. Takes an element name,
    finds element in netlist, copies it, and places the copy in parallel with the original.
    '''
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

    ''' Simulation data is measured at the highest-numbered node on the circuit. max_node is
    how we find that highest-numbered node'''
    def max_node(self):
        max_node = 0
        # run through netlist, change max_node if you find a higher value
        for element in self.netlist:
            if element.bottomnode > max_node:
                max_node = element.bottomnode
            if element.topnode > max_node:
                max_node = element.topnode
        return max_node

    '''Split netlist in half. This is necessary for crossover. Returns the two halves of the
    netlist as a two-element list'''
    def half_func(self):
        l = len(self.netlist)
        return self.netlist[0:l/2], self.netlist[l/2:l]

    # TODO implement a function to delete a random component (not V1)
    # ^^ still possible to implement, but I elected not to do this because of the danger of
    # deleting things that would cause an open circuit

    '''check_nums checks the netlist for components with duplicate names. This is a relatively
    time-consuming process, as it takes O(n^2) for n elements in the netlist. However, a netlist
    with non-unique component names cannot be simulated in Ngspice'''
    def check_nums(self):
        self.delete_garbage()
        for i in range(len(self.netlist)):
            templist = copy.deepcopy(self.netlist)
            #pop the first element so we aren't comparing anything to itself
            stat_element = templist.pop(i)
            for j in range(len(templist)):
                dynamic_element = templist[j]
                if stat_element.name == dynamic_element.name:   #if two names are the same
                    letter = dynamic_element.name[0]
                    num = int(dynamic_element.name[1:len(dynamic_element.name)])
                    rest = str(num+1)   # renumber the second one
                    new_name = letter, rest
                    new_name = "".join(new_name)
                    if j < i:
                        net_index = j
                    else:
                        net_index = j + 1
                    self.netlist[net_index].name = new_name
        return

    '''components between 0 and 1 are across the voltage source and will have no real effect on the
    dynamics of the circuit. Delete them to economize on space. This method doesn't seem to work all
    the time; really needs to get debugged properly at some point'''
    def delete_garbage(self):
        for i in range(1,len(self.netlist)):
            element = self.netlist[i]
            top = element.topnode
            bottom = element.bottomnode
            if (top == 0 and bottom == 1) or (top == 1 and bottom ==0):
                self.netlist.remove(element)
        return

    '''Returns netlist as an array. Good for using on test functions to make the outputs more readable;
    not actually necessary for the current genetic algorithm'''
    def format_netlist(self,net):
        net = str(net)
        net = net.split(',')
        net = np.asarray(net)
        return net

    def __repr__(self):
        return str(self)

    def __str__(self):
        this_list = "".join(str(self.netlist))
        return this_list
