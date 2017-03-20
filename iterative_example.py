import subprocess as sp
import raw_reader as rr
import numpy as np
import matplotlib.pyplot as plt
import circuit_class_prototype as cir
import crossover as cross
import re

spicepath = r'/Applications/ngspice/bin/ngspice'
filepath = r'/Desktop/CircuitreeOfLife/highpass.cir'

def clean_line(line):
    line = str(line)
    line = line.replace('[', '')
    line = line.replace(']', '')
    line = line.replace('\'', '')
    line = line.replace('\"', '')
    return line

def write_netlist(netlist):
    # deletes all the old stuff out of highpass.cir every time
    with open("highpass.cir", "w") as fo:
        #always put in the control loop
        fo.write('* High pass filter\n')
        fo.write('.ac dec 10 1 1e5\n')
        fo.write('.control\n')
        fo.write('save all\n')
        fo.write('run\n')
        fo.write('write\n')
        fo.write('.endc\n')
        fo.write('\n')
        #netlist = netlist.split(',')
        #print netlist
        for line in netlist:
            line = clean_line(line)
            fo.write(line)
            fo.write('\n')
        fo.write('.END')
    return

def iterate(spicepath, netlist):
    write_netlist(netlist) #this definitely should write a new highpass.cir
    #p = sp.Popen(["%s" % (spicepath), "-b", "-r", "hpf.raw", "hp1.cir"])
    p = sp.Popen(["%s" % (spicepath), "-b", "-r", "hpf.raw", "highpass.cir"])
    p.communicate()
    [arrs, plots] = rr.rawread('hpf.raw')   #arrs is the voltages'n'currents
    if arrs == None:
        return (None,None)

    arrs = arrs[0]
    types = arrs.dtype

    k = len(arrs[0])
    array = np.empty((0,k))
    for line in arrs:
        this_row = []
        for term in line:
            this_row.append(float(term))
        array = np.vstack((array, this_row))

    return array, types

''' the function evaluate_solution is meant to assess the fitness
of a particular circuit simulation via its output.  The function takes
three arguments. "array" contains the simulation result data. Its first column
is time; its other columns are voltage and current data. "function" represents
the fitness function: the function that the system output should emulate. Finally,
"k" is the number of the column in which the output voltage data is stored.
evaluate_solution returns the sum-squared error between the data and the fitness
function as the fitness value. Obviously, lower fitness values are preferred.'''

def fitness_example(freqs):
    val = []
    for i in freqs:
        if i < 25000:
            val.append(1)
        if i > 25000:
            val.append(0)
    return val

def evaluate_solution(array, function, k):
    # k is the column in which the correct simulation voltage is kept
    freqs = array[:,0]   # first column of data is always time
    data = array[:,k]
    func = function(freqs)
    fitness_val = 0
    for i in range(len(data)):
        fitness_val += (func[i]-data[i])**2
    return fitness_val

def build_hpf():
    hpf = cir.Circuit()
    node = hpf.add_component_series('R1', '1', '50k')
    hpf.add_component_parallel('C1', node, '10p')
    hpf.serialize('R1')
    hpf = str(hpf)
    hpf = hpf.split(',')
    hpf = np.asarray(hpf)

    return hpf


''' maybe a good idea to build circuits up of subcircuits instead of directly of components?
I can recycle the methods of the circuit class by using them to build subcircuits. '''


if __name__ == '__main__':
    # circuit_collection = []
    # data_lists = []
    # for i in range(8):
    #     netlist = cross.build_random()
    #     circuit_collection.append(netlist)
    #     array = iterate(spicepath, netlist)
    generation = []
    gen_fit = []
    for i in range(8):
        new_circuit= cross.build_random()
        generation.append(new_circuit)
        netlist = new_circuit.netlist
        [array, types] = iterate(spicepath, netlist)
        if array == None:
            fitness = 1000
        else:
            fitness = evaluate_solution(array, fitness_example, 2)
        gen_fit.append(fitness)

    #print gen_fit
    minIndex1 = gen_fit.index(min(gen_fit))
    gen_fit.pop(minIndex1)
    cir1 = generation.pop(minIndex1)

    minIndex2 = gen_fit.index(min(gen_fit))
    gen_fit.pop(minIndex2)
    cir2 = generation.pop(minIndex2)

    #print cir1
    crossed_circs = cross.cross_funcs(cir1, cir2)
    #print a
    i = 0
    fits = []
    datasets = []
    for circuit in crossed_circs:
        netlist = circuit.netlist
        [array, types] = iterate(spicepath, netlist)
        if array == None:
            fitness = 1000
        else:
            fitness = evaluate_solution(array, fitness_example, 2)
        print "Circuit number", i
        print "Fitness", fitness
        print "Netlist", netlist
        fits.append(fitness)
        datasets.append(array)
        i +=1
    minIndex1 = fits.index(min(fits))
    best_soln = crossed_circs[minIndex1]
    array = datasets[minIndex1]
    time = array[:,0]
    #TODO select node to plot in an intelligent way pls
    plt.plot(time, array[:,2], time, fitness_example(time))
    plt.xlabel("Frequency")
    plt.ylabel("Output Voltage")
    plt.show()





    # if array != None:
    #     types = str(types)
        #voltages = re.search('v(\.d)',types)
        # outer = re.compile("v\((.+)\)")
        # m = outer.search(types)
        # res = m.group(1)

    #
    # while len(circuit_collection) > 0:
    #     cir1 = circuit_collection.pop()
    #     cir2 = circuit_collection.pop()
    #     [a, b] = cross.cross_funcs(cir1, cir2)
    #     new_gen.append(a)
    #     new_gen.append(b)
    #     print len(new_gen)

    #create a high pass filter at

    # array = iterate(spicepath, netlist)
    #print 'THIS IS THE FITNESS', fitness

    # if array != None:
    #     time = array[:,0]
    #     #TODO select node to plot in an intelligent way pls
    #     plt.plot(time, array[:,2])
    #     plt.show()


''' standard netlist for a HPF:
* another example circuit
* this one's a high pass filter


.tran 10n 1u

.control
save all
run
write
.endc



V1 in 0 sin(0 1 1e6)
R1 in out 50k
C1 out 0 10p

.END
'''
