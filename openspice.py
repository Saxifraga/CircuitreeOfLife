
# path: in root--- Applications/ngspice/bin/ngspice

import subprocess as sp

spicepath = r'/Applications/ngspice/bin/ngspice'

#p = sp.Popen(["%s" % (spicepath), "-b", "-r", "rawfile.raw", "xspice_c1.cir"])
p = sp.Popen(["%s" % (spicepath), "-s", "parameter_sweep.cir"])

p.communicate() #this line causes to ngspice to close after it's done simulating
