
# path: in root--- Applications/ngspice/bin/ngspice
import subprocess as sp
import raw_reader as rr
import numpy as np
import matplotlib.pyplot as plt

spicepath = r'/Applications/ngspice/bin/ngspice'
filepath = r'/Desktop/CircuitreeOfLife/highpass.cir'

'''I need to rewrite the netlist in highpass.cir, save it, simulate it, read the rawfile with raw_reader.py,
get the resulting vout/vin ratio, compare the ratio to my desired ratio, and rewrite
the netlist accordingly'''

def write_netlist(rval):
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
        for line in netlist:
            #TODO make sure I've converted netlist to strings
            fo.write(line)
            fo.write('\n')
        fo.write('.END')
    return

def iterate(spicepath):
    for i in range(1):
        rval = 1000
        write_netlist(rval) #this definitely should write a new highpass.cir
        #p = sp.Popen(["%s" % (spicepath), "-b", "-r", "hpf.raw", "hp1.cir"])
        p = sp.Popen(["%s" % (spicepath), "-b", "-r", "hpf.raw", "functioning_hpf.cir"])
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

def evaluate_solution(array, function, k):
    # k is the column in which the correct simulation voltage is kept
    time = array[:,0]   # first column of data is always time
    data = array[:,k]
    func = function(time)
    fitness_val = sum((func-data)**2)
    return fitness_val

if __name__ == '__main__':
    array = iterate(spicepath)
    time = array[:,0]
    plt.plot(time, array[:,1])
    plt.show()



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
