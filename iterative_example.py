import subprocess as sp
import raw_reader as rr
import numpy as np
import matplotlib.pyplot as plt
import circuit_class_prototype as cir
import crossover as cross
import re
import copy

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
    # LPF example:
    # for i in freqs:
    #     if i < 5000:
    #         val.append(1)
    #     if i > 5000:
    #         val.append(0)

###########################
    # Band pass example:
    for i in freqs:
        if i > 5000 and i < 20000:
            val.append(1)
        else:
            val.append(0)

    return val

def evaluate_solution(array, function, k):
    # k is the column in which the correct simulation voltage is kept
    freqs = array[:,0]   # first column of data is always time
    data = array[:,k]
    func = function(freqs)
    fitness_val = 0

    high_freq_weight = 10
    low_freq_weight = 10
    med_freq_weight = 10
    for i in range(len(data)):
        if i < len(data)/10:
            fitness_val += low_freq_weight*(func[i]-data[i])**2
        elif i > (9/10)*len(data):
            fitness_val += high_freq_weight*(func[i]-data[i])**2
        else:
            fitness_val += med_freq_weight*(func[i]-data[i])**2
    diff = max(data) - min(data)
    fitness_val = fitness_val/(diff)
    return fitness_val

def generation(gen):
    # evaluate the last set of circuits

    gen_fit = []
    for i in gen:
        netlist = i.netlist
        [array, types] = iterate(spicepath, netlist)
        if array == None:
            fitness = 1000
        else:
            fitness = evaluate_solution(array, fitness_example, 2)
        gen_fit.append(fitness)
    # choose the best to keep
    next_gen = []
    best_fit = min(gen_fit)
    for i in range(len(gen)/4):
        minIndex = gen_fit.index(min(gen_fit))
        gen_fit.pop(minIndex)   #don't care about fitness score anymore
        next_gen.append(gen.pop(minIndex))
    #print 'length of originals', len(next_gen)
    # mate the best circuits together
    for i in range(len(next_gen)):
        if i%2 != 0:
            pass
        else:
            [spawn1, spawn2] = cross.cross_funcs(next_gen[i], next_gen[i+1])
            next_gen.append(spawn1)
            next_gen.append(spawn2)
    # now mutate em
    finals = []
    for circuit in next_gen:
        finals.append(circuit)
        babby = copy.deepcopy(circuit)
        babby.mutate()
        finals.append(babby)
    #print 'finals', finals

    return finals, best_fit

# def build_hpf():
#     hpf = cir.Circuit()
#     node = hpf.add_component_series('R1', '1', '50k')
#     hpf.add_component_parallel('C1', node, '10p')
#     hpf.serialize('R1')
#     # hpf = str(hpf)
#     # hpf = hpf.split(',')
#     # hpf = np.asarray(hpf)
#
#     return hpf


''' maybe a good idea to build circuits up of subcircuits instead of directly of components?
I can recycle the methods of the circuit class by using them to build subcircuits. '''


if __name__ == '__main__':
    gen = []
    number_of_generations = 50
    for i in range(40):
        gen.append(cross.build_random())
    for i in range(number_of_generations):
        print 'GENERATION', i
        [gen, best_fit] = generation(gen)   #this *should* work

    # best_fit = 1000
    # num_gen = 0
    # while best_fit > 8.0:
    #     [gen, best_fit] = generation(gen)
    #     num_gen +=1
    #     print 'GENERATION', num_gen, 'fitness', best_fit

    cream_of_crop = gen #the last values you get out will be best
    gen_fit = []
    data = []
    for i in cream_of_crop:
        [array, types] = iterate(spicepath, i.netlist)
        if array == None:
            fitness = 1000
        else:
            fitness = evaluate_solution(array, fitness_example, 2)
        data.append(array)
        gen_fit.append(fitness)
    minIndex = gen_fit.index(min(gen_fit))
    print 'fitness', gen_fit.pop(minIndex)   #don't care about fitness score anymore
    mySolution = cream_of_crop.pop(minIndex)
    myData = data.pop(minIndex)
    freqs = myData[:,0]
    #TODO select node to plot in an intelligent way pls
    plt.plot(freqs, myData[:,2], freqs, fitness_example(freqs))
    plt.xscale('log')
    plt.show()

###################################

    #
    #
    #
    # if array != None:
    #     types = str(types)
    #     voltages = re.search('v(\.d)',types)
    #     outer = re.compile("v\((.+)\)")
    #     m = outer.search(types)
    #     res = m.group(1)
    #
    #
    # while len(circuit_collection) > 0:
    #     cir1 = circuit_collection.pop()
    #     cir2 = circuit_collection.pop()
    #     [a, b] = cross.cross_funcs(cir1, cir2)
    #     new_gen.append(a)
    #     new_gen.append(b)
    #     print len(new_gen)
    #
    # create a high pass filter at
    #
    # array = iterate(spicepath, netlist)
    # print 'THIS IS THE FITNESS', fitness
    #
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
