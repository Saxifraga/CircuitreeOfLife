import subprocess as sp
import raw_reader as rr
import numpy as np
import matplotlib.pyplot as plt
import circuit_class_prototype as cir

spicepath = r'/Applications/ngspice/bin/ngspice'
filepath = r'/Desktop/CircuitreeOfLife/highpass.cir'

def clean_line(line):
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
        fo.write('.tran 10n 1u\n')
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

    arrs = arrs[0]
    k = len(arrs[0])
    array = np.empty((0,k))
    for line in arrs:
        this_row = []
        for term in line:
            this_row.append(float(term))
        array = np.vstack((array, this_row))
    return array

''' the function evaluate_solution is meant to assess the fitness
of a particular circuit simulation via its output.  The function takes
three arguments. "array" contains the simulation result data. Its first column
is time; its other columns are voltage and current data. "function" represents
the fitness function: the function that the system output should emulate. Finally,
"k" is the number of the column in which the output voltage data is stored.
evaluate_solution returns the sum-squared error between the data and the fitness
function as the fitness value. Obviously, lower fitness values are preferred.'''

def evaluate_solution(array, function, k):
    # k is the column in which the correct simulation voltage is kept
    time = array[:,0]   # first column of data is always time
    data = array[:,k]
    func = function(time)
    fitness_val = sum((func-data)**2)
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

# TODO implement crossover
''' would like to take two high fitness circuits, identify chunks of them (subcircuits? pieces of
distinct topology? How to identify circuit topology?), pull '''

''' maybe a good idea to build circuits up of subcircuits instead of directly of components?
I can recycle the methods of the circuit class by using them to build subcircuits. '''
# def crossover(cir1, cir2):
#     # a circuit object returns its netlist as strings
#     # say I want to take the first two components of
#     for component in cir1:
#         component.bottomnode
#
#     return cir1, cir2

if __name__ == '__main__':

    netlist = build_hpf()
    print netlist
    # array = iterate(spicepath, netlist)
    # time = array[:,0]
    # plt.plot(time, array[:,1])
    # plt.show()


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
