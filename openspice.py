
# path: in root--- Applications/ngspice/bin/ngspice

import subprocess as sp

spicepath = r'/Applications/ngspice/bin/ngspice'

p = sp.Popen(["%s" % (spicepath), "-b", "-r", "rawfile.raw", "xspice_c1.cir"])
#p.communicate()
