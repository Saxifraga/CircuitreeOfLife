import numpy as np
import circuit_class_prototype as cir
import iterate_evaluate as ie
import component_class_prototype as comp

def format_netlist(net):
    net = str(net)
    net = net.split(',')
    net = np.asarray(net)
    return net

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

def random_value(c_type):
    rootval = np.random.random()
    if c_type == 'C' or c_type == 'L':
        val = str(rootval), 'u'
    else:
        val = str(rootval), 'k'
    return "".join(val)


def build_random():
    r = cir.Circuit()
    i = 1
    imax = 6
    comp0 = random_component(1)
    r.add_component_series(comp0, 1, random_value(comp0[0]))

    while i < imax:
        n = np.random.randint(0,3)
        m = np.random.randint(0,2)
        element = r.netlist[-1]
        node = element.bottomnode
        if n ==0 or n==1:
            cname = random_component(i)
            if m == 0:
                r.add_component_series(cname, node,random_value(cname[0]))
            if m == 1:
                r.add_component_parallel(cname, node, random_value(cname[0]))
        if n ==2:
            if m ==0:
                r.parallelize(element.name)
            else:
                r.serialize(element.name)
        i +=1
    r.check_nums()
    return r


def build_hpf():
    hpf = cir.Circuit()
    node = hpf.add_component_series('R1', '1', '50k')
    hpf.add_component_parallel('C1', node, '10p')
    hpf.serialize('R1')
    hpf = format_netlist(hpf)
    return hpf

# problem: if I format the netlist first, then I can't

def test_func():
    n = cir.Circuit()
    n.add_component_series('R1', '1', '1k')
    n.add_component_series('R1', '2', '1k')
    n.add_component_series('R1', '3', '1k')
    n.add_component_series('R1', '4', '1k')
    # n.add_component_series('R1', '5', '1k')
    n.check_nums()
    n = format_netlist(n)
    return

def cross_funcs(a,b):
    [a1, a2] = a.half_func()
    [b1, b2] = b.half_func()
    new_a = cir.Circuit(a1,b2)
    print 'the baby\n', new_a
    return new_a


r1 = build_random()
r2 = build_random()
print 'r1\n', r1, '\n'
print 'r2\n', r2, '\n'

r=cross_funcs(r1, r2)
r.check_nums()
print r

# def build_net_2():
#     net2 = cir.Circuit()
#     node = net2.add_component_series('L1', )
#
