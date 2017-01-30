
# path: in root--- Applications/ngspice/bin/ngspice
import subprocess as sp
import raw_reader as rr

spicepath = r'/Applications/ngspice/bin/ngspice'
filepath = r'/Desktop/CircuitreeOfLife/highpass.cir'

'''I need to rewrite the netlist in highpass.cir, save it, simulate it, read the rawfile with raw_reader.py,
get the resulting vout/vin ratio, compare the ratio to my desired ratio, and rewrite
the netlist accordingly'''

def write_netlist(rval):
    #rval will be varied
    # deletes all the old stuff out of highpass.cir every time
    with open("highpass.cir", "w") as fo:
        fo.write('Vsource vin AC sin(0 1m 10k 0 0)')
        fo.write('\nC1 vin vout .23u')
        fo.write('\nR1 vout 0 {}'.format(rval))
        fo.write('\n.control')
        fo.write('\ntran .5s 1s')
        fo.write('\n.endc')
        fo.write('\n.end')
    return
for i in range(4):
    rval = 1000*(i+1)
    write_netlist(rval)
    p = sp.Popen(["%s" % (spicepath), "-b", "-r", "hpf.raw", "highpass.cir"])
    rr.rawread('hpf.raw')
    #^not sure exactly what this line will produce. I think it just reads into the terminal
    # right now---need to read into file and compare final vout/vin values

''' standard netlist for a HPF:
* another example circuit
* this one's a high pass filter

Vsource vin AC sin(0 1m 10k 0 0)
C1 vin vout .23u
R1 vout 0 1k

.control
tran .5s 1s
.endc
.end     '''
