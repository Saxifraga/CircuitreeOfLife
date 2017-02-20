import subprocess as sp
import raw_reader as rr
import numpy as np
import matplotlib.pyplot as plt
import circuit_class_prototype as cir

spicepath = r'/Applications/ngspice/bin/ngspice'
filepath = r'/Desktop/CircuitreeOfLife/highpass.cir'


def write_netlist(netlist):
    #rval will be varied
    # deletes all the old stuff out of highpass.cir every time
    with open("highpass.cir", "w") as fo:
        #always put in the control loop
        fo.write('.tran 10n 1u\n')
        fo.write('.control\n')
        fo.write('save all\n')
        fo.write('run\n')
        fo.write('write\n')
        fo.write('.endc\n')
        #netlist = netlist.split(',')
        print netlist
        for line in netlist:
            #TODO make sure I've converted netlist to strings
            # line = str(line) #(???)
            fo.write(line)
            fo.write('\n')
        fo.write('.END')
    return

def iterate(spicepath, netlist):
    for i in range(1):
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
    hpf = str(hpf)
    hpf = hpf.split(',')
    hpf = np.asarray(hpf)
    return hpf

if __name__ == '__main__':
    # array = iterate(spicepath)
    # time = array[:,0]
    # plt.plot(time, array[:,1])
    # plt.show()
    netlist = build_hpf()
    iterate(spicepath, netlist)
    #netlist = np.asarray(build_hpf())


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
