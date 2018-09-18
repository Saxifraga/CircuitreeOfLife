'''circuit_evolver written by Rachel Sassella for E90 senior design project, Spring 2017

This module writes .cir files for Ngspice, interfaces with Ngspice to run simulations,
deploys rawreader.py to decode simulation data, evaluates the data, and controls the genetic
algorithm.
'''
import subprocess as sp
import raw_reader as rr
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import matplotlib.pyplot as plt
import circuit_class as cir
import crossover as cross
import copy

spicepath = r'/Applications/ngspice/bin/ngspice'    #location of ngspice terminal on computer
filepath = r'/Desktop/CircuitreeOfLife/highpass.cir'    #location of source file on computer

# clean_line takes care of removing brackets and quotes from netlists when they are read in
# from their circuits. These characters need to be deleted in order for the netlist to be read
# properly for simulation

def clean_line(line):
    line = str(line)
    line = line.replace('[', '')
    line = line.replace(']', '')
    line = line.replace('\'', '')
    line = line.replace('\"', '')
    return line

'''write_netlist takes a circuit netlist and writes it to a .cir file with the appropriate
control loop for an AC analysis'''
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
        #get rid of garbage characters in netlist
        for line in netlist:
            line = clean_line(line)
            fo.write(line)
            fo.write('\n')
        fo.write('.END')
    return

'''iterate() takes the location of ngspice and a circuit netlist as arguments, instructs
Ngspice to perform the simulation, '''
def iterate(spicepath, netlist):
    write_netlist(netlist) #write netlist and control loop to highpass.cir
    # write commands to the Ngspice command line, simulate the netlist in highpass.cir,
    # and write the simulation results to hpf.raw
    p = sp.Popen(["%s" % (spicepath), "-b", "-r", "hpf.raw", "highpass.cir"])
    p.communicate()
    # translate the binary .raw file to something we can read
    [arrs, plots] = rr.rawread('hpf.raw')   #arrs is the voltages'n'currents
    if arrs == None:
        return (None,None)
    #parse the data a bit
    arrs = arrs[0]
    types = arrs.dtype  #types is meant to be the labels on each data column
    k=3
    try:
        k = len(arrs[0])
    except:
        print arrs
    array = np.empty((0,k))
    for line in arrs:
        this_row = []
        for term in line:
            #get magnitude of complex values so we can graph properly
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
    # # # LPF example:
    # for i in freqs:
    #     if i < 5000:
    #         val.append(1)
    #     if i >= 5000:
    #         val.append(0)

###########################
    # # Band pass example:
    for i in freqs:
        if i >= 150 and i <= 600:
            val.append(1)
        else:
            val.append(0)

    return val

''' evaluate_solution takes the simulation data (array), the desired frequency response
(function), and the value of the maximum node, k. K also corrresponds to the column number
in which the maximum node's voltage is stored.'''

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
    for i in range(len(data)):
        gap = abs(func[i] - data[i])
        ############################
        # CASE 1:
        # important zone, large gap
        # weight: 100
        if (i <= 100) or (i< 650 and i>100) or (i>99000):   #uncomment this line for a BPF
        #if (i<=100) or (i>4800 and i<5200) or (i>99000):   #uncomment this line for HPF, LPF
            if gap > .4:
                weight = 100
        # CASE 2:
        # important zone, medium gap
        # weight: 40
            elif gap <= .4 and gap > .1:
                weight = 40
        # CASE 3:
        # important zone, small gap
        # weight: 5
            else:
                weight = 5
        else:
        # CASE 4:
        # unimportant zone, large gap
        # weight: 60
            if gap > .4:
                weight = 60
        # CASE 5:
        # unimportant zone, medium gap
        # weight: 10
            elif gap <= .4 and gap > .1:
                weight = 10
        # CASE 6:
        #unimportant zone, small gap
        #weight: 1
            else:
                weight = 1
        fitness_val += weight*(func[i]-data[i])**2

    diff = max(data) - min(data)
    fitness_val = fitness_val/(diff)
    return fitness_val

'''generation() is where generation i is evaluated, selected, and turned into generation i+1.
Evaluation, selection, crossover, and mutation are all controlled from here. The function takes
the last generation of circuits, gen, and returns the next generation (finals), as well as
the best fitness score from the generation, the simulation data from the corresponding circuit,
and the maximum node value in that circuit.'''
def generation(gen):
    # evaluate the last generations of circuits
    gen_size = len(gen)
    gen_fit = []
    for i in gen:
        [array, types] = iterate(spicepath, i.netlist)
        if array == None:
            fitness = 1000
        else:
            fitness = evaluate_solution(array, fitness_example, i.max_node())
        gen_fit.append(fitness) #save all the fitnesses to an array
    # choose the best to keep
    next_gen = []
    # The following code is primarily useful for saving and generating images of the best
    # of generation individuals over time.
    # The data will be output and can be plotted for every (other) generation, which is cool if
    # you want to make a gif
    best_fit = min(gen_fit) #lowest fitness score is the best
    where_is = gen_fit.index(best_fit)  #save the best circuit
    best_cir = gen[where_is]
    [best_data, nah] = iterate(spicepath, best_cir.netlist) #generate data from the best circuit
    best_node = int(best_cir.max_node())    # save the max_node from the best circuit
    #################
    print best_fit
    # Stochastic selection with elitism
    ordered = []    # rank circuits from best to worst
    for i in range(len(gen_fit)):
        minIndex = gen_fit.index(min(gen_fit))
        gen_fit.pop(minIndex)
        bestest_boy = gen.pop(minIndex)
        if i < 3:   #here's our elitism --- save the 3 best circuits
            next_gen.append(bestest_boy)
        ordered.append(bestest_boy)
        #'ordered' is an ordered list of all circuits, most to least fit
    a = (gen_size+1)*(gen_size/2)  #sum of all numbers from 1 to n
    weights = {}    #create a dictionary of weights
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
        # Method 1: choose the top n/4 circuits (non stochastic; only elitism)
    # for i in range(len(gen)/4):
    #     minIndex = gen_fit.index(min(gen_fit))
    #     gen_fit.pop(minIndex)   #don't care about fitness score anymore
    #     next_gen.append(gen.pop(minIndex))
        #############################
    # mate the selected circuits together
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
    return finals, best_fit, best_data, best_node

'''Below are a couple of commmented-out examples of how to build specific circuits'''
# def build_lpf():
#     lpf = cir.Circuit()
#     node = lpf.add_component_series('R1', '1', '1k')
#     lpf.add_component_parallel('C1', node, '.1u')
#     #lpf.serialize('R1')
#     # lpf = str(lpf)
#     # lpf = lpf.split(',')
#     # lpf = np.asarray(lpf)
#
#     return lpf
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


if __name__ == '__main__':
    gen = []
    flag = False
    number_of_generations = 100
    #randomly generate the first population of circuits
    for i in range(80):
        gen.append(cross.build_random())
    fit_val = []
    for i in range(number_of_generations):
        print 'GENERATION', i
        [gen, best_fit, best_data, best_node] = generation(gen)   #this *should* work
        fit_val.append(best_fit)    # so we can explore convergence over generations
        # Uncomment the following code if you want to save a plot every two generations
        # if i%2 ==0: #every other generation
        #     plt.clf()
        #     picname = ['gen',str(i),'.png']
        #     picname = ''.join(picname)
        #     title = ['Generation ', str(i)]
        #     if best_data == None:
        #         plt.plot((0,0), (5, 5), 'k-')
        #     else:
        #
        #         freqs = best_data[:,0]
        #         plt.plot(freqs, best_data[:,best_node], freqs, fitness_example(freqs))
        #     try:
        #         plt.xscale('log')
        #     except:
        #         pass
        #     axes = plt.gca()
        #     axes.set_ylim([0, 2.0])
        #     plt.title('Filter Output')
        #     plt.xlabel('Frequency')
        #     plt.savefig(picname,bbox_inches='tight')

####################################
## While loop code: run this if you only care about converging on a certain fitness value
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
    #The entire population of the final generation:
    cream_of_crop = gen #the last values you get out will be best
    data = []
    gen_fit = []
    # find the best circuit in the last generation
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
    node = int(i.max_node())

    #if flag:
    #    print "Failed to Converge :("
    # Generate a PDF with the frequency response of the solution and a plot of best
    # fit in generation over time
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
        plt.clf()

##################################
