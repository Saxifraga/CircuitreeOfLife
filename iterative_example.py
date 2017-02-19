
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
        fo.write('Vsource vin 0 DC 6')
        fo.write('\nC1 vin vout .23u')
        fo.write('\nR1 vout 0 {}'.format(rval))
        fo.write('\n.tran .5s 4s UIC')
        fo.write('\n')
        fo.write('\n.control')
        fo.write('\nsave all')
        fo.write('\nrun')
        fo.write('\nwrite')
        fo.write('\n.endc')
        fo.write('\n')
        fo.write('\n.end')
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

if __name__ == '__main__':
    array = iterate(spicepath)
    plt.plot(array[:,0], array[:,1])
    plt.show()




''' standard netlist for a HPF:
* another example circuit
* this one's a high pass filter

Vsource vin 0 DC 6
*need to figure out ac sources :/
C1 vin vout .23u
R1 vout 0 1000
.tran .5s 1s UIC

.control
save all
run
write
.endc

.end    '''
