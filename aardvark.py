# DO NOT EDIT
# This is the last version that worked

import subprocess as sp
import raw_reader as rr
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import matplotlib.pyplot as plt
import circuit_class_prototype as cir
import crossover as cross
import re
import copy

spicepath = r'/Applications/ngspice/bin/ngspice'
hickspath = r'~/Desktop/ngspice-26/src/ngspice'
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
    k=3
    try:
        k = len(arrs[0])
    except:
        print arrs
    array = np.empty((0,k))
    for line in arrs:
        this_row = []
        for term in line:
            this_row.append(np.absolute(complex(term)))
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
    # # LPF example:
    # for i in freqs:
    #     if i < 5000:
    #         val.append(0)
    #     if i >= 5000:
    #         val.append(1)

###########################
    # # Band pass example:
    for i in freqs:
        if i >= 150 and i <= 600:
            val.append(1)
        else:
            val.append(0)
    return val

''' evaluate_solution takes the simulation data (array), the fitness
function ()'''

def evaluate_solution(array, function, k):
    # k is the column in which the correct simulation voltage is kept
    freqs = array[:,0]   # first column of data is always time
    try:
        data = array[:,k]
    except:
        fitness_val = 1000
        return fitness_val
    func = function(freqs)
    fitness_val = 0

    # for bpf above, important zones 100-200, 550-650

    high_freq_weight = 10
    low_freq_weight = 10
    med_freq_weight = 1
    for i in range(len(data)):
        #experimental: want to get rid of zigzags
        # if data[i] < 0:
        #     fitness_val = 100000
        #     return fitness_val
        ############################
        gap = abs(func[i] - data[i])
        ############################
        # CASE 1:
        # important zone, large gap
        # weight: 100
        if (i <= 100) or (i< 650 and i>100) or (i>99000):
        #if (i<=100) or (i>4800 and i<5200) or (i>99000):
            if gap > .4:
                weight = 100
            elif gap <= .4 and gap > .1:
                weight = 40
            else:
                weight = 5
        else:
            if gap > .4:
                weight = 60
            elif gap <= .4 and gap > .1:
                weight = 10
            else:
                weight = 1
        fitness_val += weight*(func[i]-data[i])**2
        # CASE 2:
        # important zone, small gap
        # weight: 50
        # CASE 3:
        # unimportant zone, large gap
        # weight:
        # CASE 4:
        # unimportant zone, small gap

         ###########################
        #
        # if gap > .1 and gap < .4:
        #     fitness_val += 10*(func[i]-data[i])**2
        # elif gap >=.4:
        #     fitness_val += 100*(func[i]-data[i])**2
        # else:
        #     fitness_val += (func[i]-data[i])**2

        # This one's a decent standard
        # if i < 100 or i>99900: #bottom hundred, top thousand
        #     fitness_val += 25*(func[i]-data[i])**2
        # elif i >=100 and i<=650:
        #     fitness_val += 40*(func[i]-data[i])**2
        # else:
        #     fitness_val += (func[i]-data[i])**2

        # Something complicated I tried for 150-600 Hz BPF (not good)
        #
        # if i < 75:
        #     fitness_val += (11-(10*i/75))*(func[i]-data[i])**2
        # elif i>=75 and i<170:
        #     fitness_val += (10/75)*(i-75)*(func[i]-data[i])**2
        # elif i>= 170 and i<580:
        #     fitness_val += 5
        # elif i>=580 and i<650:
        #     fitness_val += (-10/75)*(i-580)*(func[i]-data[i])**2
        # elif i>=650 and i<99000:
        #     fitness_val += (func[i]-data[i])**2
        # elif i >= 99000:
        #     fitness_val += (10/750)*(i-99000)*(func[i]-data[i])**2

        #Standard evaluation for HPF, LPF

        # if i < len(data)/10:
        #     fitness_val += low_freq_weight*(func[i]-data[i])**2
        # elif i > (9/10)*len(data):
        #     fitness_val += high_freq_weight*(func[i]-data[i])**2
        # else:
        #     fitness_val += med_freq_weight*(func[i]-data[i])**2
    diff = max(data) - min(data)
    fitness_val = fitness_val/(diff)
    return fitness_val

def generation(gen):
    # evaluate the last set of circuits
    gen_size = len(gen)
    gen_fit = []
    for i in gen:
        [array, types] = iterate(spicepath, i.netlist)
        if array == None:
            fitness = 1000
        else:
            fitness = evaluate_solution(array, fitness_example, i.max_node())
        gen_fit.append(fitness)
    # choose the best to keep
    next_gen = []
    best_fit = min(gen_fit)
    where_is = gen_fit.index(best_fit)
    best_cir = gen[where_is]
    [best_data, nah] = iterate(spicepath, best_cir.netlist)
    best_node = int(best_cir.max_node())
    print best_fit
    # # METHOD 2: probabilistic with elitism
    ordered = []
    for i in range(len(gen_fit)):
        minIndex = gen_fit.index(min(gen_fit))
        gen_fit.pop(minIndex)
        bestest_boy = gen.pop(minIndex)
        if i < 3:   #here's our elitism --- save the 3 best circuits
            next_gen.append(bestest_boy)
        ordered.append(bestest_boy) #store all but the best 3 in order here
        #'ordered' is an ordered list of all circuits, most to least fit
    a = (gen_size+1)*(gen_size/2)  #gauss formula

    weights = {}
    jmax = 0
    for i in range(gen_size):
        for j in range(gen_size-i):
            #weights[i].append(j + jmax)
            weights[j+jmax] = i
        jmax += (j+1)
    for i in range((gen_size/4)-3):  #  next_gen should contain 3 top of ordered[]
        k = np.random.randint(0,a)
        index = weights.get(k)
        next_gen.append(ordered[index])
        #############################
        # Method 1: choose the top n/4 circuits
    # for i in range(len(gen)/4):
    #     minIndex = gen_fit.index(min(gen_fit))
    #     gen_fit.pop(minIndex)   #don't care about fitness score anymore
    #     next_gen.append(gen.pop(minIndex))
        #############################
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
    return finals, best_fit, best_data, best_node

# def build_hpf():
#     hpf = cir.Circuit()
#     node = hpf.add_component_series('R1', '1', '1k')
#     hpf.add_component_parallel('C1', node, '.1u')
#     #hpf.serialize('R1')
#     # hpf = str(hpf)
#     # hpf = hpf.split(',')
#     # hpf = np.asarray(hpf)
#
#     return hpf
#
# def build_bpf():
#     bpf = cir.Circuit()
#     # node = bpf.add_component_series('C1', '1', '.531u')
#     # bpf.add_component_parallel('R1', '2', '1k')
#     # bpf.add_component_series('R2', '2', '1k')
#     # bpf.add_component_parallel('C2', '3', '.212u')
#     node = bpf.add_component_series('C1', '1', '.1u')
#     bpf.add_component_series('L1', '2', '.001')
#     bpf.add_component_parallel('R1', '3', '10')
#     return bpf
#
# def deliberate_trash():
#     trash = cir.Circuit()
#     trash.add_component_series('L1', '1', '1.2272399053u')
#     trash.add_component_parallel('C1', '2', '1.09334749846u')
#     trash.add_component_series('C2', '2', '1.06260342265u')
#     trash.add_component_parallel('L2', '3', '1.06482722528u')
#     return trash

''' maybe a good idea to build circuits up of subcircuits instead of directly of components?
I can recycle the methods of the circuit class by using them to build subcircuits. '''


if __name__ == '__main__':
    # for i in range(4):
    #     print 'Circuit', i, '\n'
    #     print cross.build_random()
    # hpf = build_hpf()
    # bpf = build_bpf()
    # print bpf
    # trash = deliberate_trash()
    # print trash
    # [array, types] = iterate(spicepath, trash.netlist)
    # #node = bpf.max_node()
    #
    # if array != None:
    #     time = array[:,0]
    #     #TODO select node to plot in an intelligent way pls
    #     plt.plot(time, array[:,3])
    #     plt.xscale('log')
    #     plt.show()


    gen = []
    flag = False
    number_of_generations = 500
    for i in range(500):
        gen.append(cross.build_random())
    # print "FIRST", gen
    fit_val = []
    for i in range(number_of_generations):
        print 'GENERATION', i
        [gen, best_fit, best_data, best_node] = generation(gen)   #this *should* work
        print 'LOBSTER', len(gen)
        fit_val.append(best_fit)
        if i%2 ==0: #every other generation
            plt.clf()
            picname = ['gen',str(i),'.png']
            picname = ''.join(picname)
            if best_data == None:
                plt.plot((0,0), (5, 5), 'k-')
            else:

                freqs = best_data[:,0]
                plt.plot(freqs, best_data[:,best_node], freqs, fitness_example(freqs))
            try:
                plt.xscale('log')
            except:
                pass
            plt.title('Filter Output')
            plt.xlabel('Frequency')
            plt.savefig(picname,bbox_inches='tight')

####################################
## While loop code
    # best_fit = 1000
    # num_gen = 0
    # flag = False
    # while best_fit > 300.0:
    #     [gen, best_fit] = generation(gen)
    #     num_gen +=1
    #     fit_val.append(best_fit)
    #     print 'GENERATION', num_gen, 'fitness', best_fit
    #     if num_gen > 70:   # if it takes too long, wipe everything
    #         flag = True
    #         break
########################################
    print best_fit
    cream_of_crop = gen #the last values you get out will be best
    data = []
    gen_fit = []
    for i in cream_of_crop:
        [array, types] = iterate(spicepath, i.netlist)
        if array == None:
            fitness = 1000
        else:
            fitness = evaluate_solution(array, fitness_example, i.max_node())
        data.append(array)
        gen_fit.append(fitness)
    print 'fitnesses', gen_fit
    minIndex = gen_fit.index(min(gen_fit))
    best_val = gen_fit.pop(minIndex)
    print 'fitness', best_val   #don't care about fitness score anymore
    fit_val.append(best_val)
    mySolution = cream_of_crop.pop(minIndex)
    print mySolution
    myData = data.pop(minIndex)
    freqs = myData[:,0]
    #TODO select node to plot in an intelligent way pls
    node = int(i.max_node())

    if flag:
        print "Failed to Converge :("
    with PdfPages('e90output.pdf') as pdf:
        plt.plot(freqs, myData[:,node], freqs, fitness_example(freqs))
        plt.xscale('log')
        plt.title('Filter Output')
        pdf.savefig()
        plt.close()
        plt.clf()

        plt.plot(fit_val, 'ro')
        plt.title('Fitness across generations')
        plt.xlabel('Generation number')
        plt.ylabel('Lowest fitness score')
        axes = plt.gca()
        axes.set_ylim([0, 1000])
        pdf.savefig()
        plt.close()

        plt.plot(fit_val, 'ro')
        plt.title('Close-up')
        plt.xlabel('Generation number')
        plt.ylabel('Lowest fitness score')
        axes = plt.gca()
        axes.set_ylim([0, 150])
        pdf.savefig()
        plt.close()



    # plt.plot(freqs, myData[:,node], freqs, fitness_example(freqs))
    # plt.xscale('log')
    # plt.show()

##################################
