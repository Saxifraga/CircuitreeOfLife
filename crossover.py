import numpy as np
import circuit_class_prototype as cir
import component_class_prototype as comp



def random_component(dig):
    n = np.random.randint(0,3)
    dig = str(dig)
    if n == 0:
        c = 'R'
    if n == 1:
        c = 'C'
    if n ==2 :
        c = 'L'
    bip = c, dig
    component = "".join(bip)
    return component

# trying to change this to include random exponent
# we want 10^-3 = .001 to 10^3 = 1000--> .001 k = 1, 1000k = 1 M
# .001 u = 1 pF, 1000 u = 1 mF
# uhh so say gaussian distribution between -3 and 3
def random_value(c_type):
    rootval = np.random.random()
    #exponent = np.random.normal(-1.0, 0.5)
    #rootval = rootval * 10**(exponent)
    if c_type == 'C' or c_type == 'L':
        val = str(rootval), 'u'
    else:
        val = str(rootval), 'k'
    return "".join(val)

def build_random():
    r = cir.Circuit()
    comp0 = random_component(1)
    r.add_component_series(comp0, 1, random_value(comp0[0]))
    comp1 = random_component(2)
    r.add_component_parallel(comp1,2, random_value(comp1[0]))
    comp2 = random_component(3)
    r.add_component_series(comp2, 2, random_value(comp2[0]))
    comp3 = random_component(4)
    r.add_component_parallel(comp3, 3, random_value(comp3[0]))
    return r

## ORIGINAL build_random() function:
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

def cross_funcs(a,b):
    [a1, a2] = a.half_func()
    [b1, b2] = b.half_func()
    new_a = cir.Circuit(a1,b2)
    new_b = cir.Circuit(b1, a2)
    new_a.check_nums()
    new_b.check_nums()
    #print 'the baby\n', new_a
    return new_a, new_b


# problem: if I format the netlist first, then I can't

def test_func():
    n = cir.Circuit()
    n.add_component_series('R1', '1', '1k')
    n.add_component_series('R1', '2', '1k')
    n.add_component_series('R1', '3', '1k')
    n.add_component_series('R1', '4', '1k')
    # n.add_component_series('R1', '5', '1k')
    n.check_nums()
    n = n.format_netlist(n)
    return



# def formats_netlist(net):
#     net = str(net)
#     net = net.split(',')
#     net = np.asarray(net)
#     return net

# r1 = build_random()
# r2 = build_random()
#
#
# r=cross_funcs(r1, r2)
# r.check_nums()
# print r.format_netlist(r)


# def build_net_2():
#     net2 = cir.Circuit()
#     node = net2.add_component_series('L1', )
#
