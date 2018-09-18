import numpy as np
import circuit_class as cir
import component_class as comp

'''
crossover.py written by Rachel Sassella for E90 project, Spring 2017

Somewhat counter-intuitively, crossover.py only contains one function related to crossover.
The bulk of the functions in this module are for randomly generating circuits for the first
generation of the genetic algorithm. Crossover is performed in cross_funcs(), which takes two
netlists and recombines them to make two offspring circuits.'''

''' cross_funcs takes two circuit objects as inputs, uses the circuit method half_func()
to split the netlists in half, then instantiates the crossed-over offspring as circuits.
Finally, it uses the check_nums function to ensure that each component is uniquely numbered. '''
def cross_funcs(a,b):
    [a1, a2] = a.half_func()    #uses circuit method to split netlist in half
    [b1, b2] = b.half_func()
    new_a = cir.Circuit(a1,b2)
    new_b = cir.Circuit(b1, a2)
    new_a.check_nums()
    new_b.check_nums()
    #print 'the baby\n', new_a
    return new_a, new_b

'''random_component randomly generates the name of a resistor, capacitor, or inductor for
building up random circuits. Because components must be uniquely numbered, random_component()
takes a single numerical argument. It returns the name of the component (ex R2, C17, etc)'''
def random_component(dig):
    n = np.random.randint(0,3)  # equal chance for each component type
    dig = str(dig)  #'dig' refers to the number that will follow the letter in the component name
    if n == 0:
        c = 'R'     #generates a resistor
    if n == 1:
        c = 'C'     #generates a capacitor
    if n ==2 :
        c = 'L'     #generates an inductor
    bip = c, dig
    component = "".join(bip)    #gives full name as string
    return component


'''random_value() takes a component type and returns a value for that component, with an
appropriate order of magnitude abbreviation. The values are randomly generated between
0 and 1. I also tried making the order of magnitude vary by implementing a randomly generated
exponent (normal distribution), but this affected convergence times. It can be uncommented
if the user is feeling brave. There is corresponding code in the value mutation section of
circuit_class.py'''

def random_value(c_type):
    rootval = np.random.random()
    #UNCOMMENT THE FOLLOWING if you want greater variety in component values
    # exponent = np.random.normal(0.0, 1.0)
    # rootval = rootval * 10**(exponent)
    if c_type == 'C' or c_type == 'L':
        val = str(rootval), 'u'         # u is for micro-henry or mirco-farad
    else:
        val = str(rootval), 'k'         # k is for kilo-ohm
    return "".join(val)

''' build_random() is the second iteration of the function to build circuits up from random
components. The original version is commented below. This version uses a four-component,
two-rung ladder topology hard-coded in. The original used randomly generated topology, too.
'''
def build_random():
    r = cir.Circuit()   # instantiate a circuit object r (only contains voltage source rn)
    comp0 = random_component(1) #randomly generate component
    r.add_component_series(comp0, 1, random_value(comp0[0]))    #add in series w voltage source
    comp1 = random_component(2)
    r.add_component_parallel(comp1,2, random_value(comp1[0]))
    comp2 = random_component(3)
    r.add_component_series(comp2, 2, random_value(comp2[0]))
    comp3 = random_component(4)
    r.add_component_parallel(comp3, 3, random_value(comp3[0]))
    return r

'''the ORIGINAL build_random() function:'''
# def build_random():
#     r = cir.Circuit()
#     i = 1
#     imax = 6
#     comp0 = random_component(1)
#     r.add_component_series(comp0, 1, random_value(comp0[0]))
#
#     while i < imax:
#         n = np.random.randint(0,3)
#         m = np.random.randint(0,2)
#         element = r.netlist[-1]
#         node = element.bottomnode
#         if node == str(0):
#             node = np.random.randint(1,3)
#         if n ==0 or n==1:
#             cname = random_component(i)
#             if m == 0:
#                 r.add_component_series(cname, node,random_value(cname[0]))
#             if m == 1:
#                 r.add_component_parallel(cname, node, random_value(cname[0]))
#         if n ==2:
#             if m ==0:
#                 r.parallelize(element.name)
#             else:
#                 r.serialize(element.name)
#         i +=1
#     r.check_nums()
#     return r
