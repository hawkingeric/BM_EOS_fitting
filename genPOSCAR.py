#!/usr/bin/env python
# Fit equations of state (EOS) to energy vs volume curves and optionally plot the results
# Davide Ceresoli <dceresoli@gmail.com>, 03/22/2011
# Inspired by ase.utils.eosase2
# TODO: Keane

import sys, numpy, math, os
from scipy.optimize import leastsq

# Murnaghan equation of state
def eos_murnaghan(params, vol):
    'From Phys. Rev. B 28, 5480 (1983)'
    E0, B0, Bp, V0 = params 
    E = E0 + B0/Bp * vol * ((V0/vol)**Bp/(Bp-1.0)+1.0) - V0*B0/(Bp-1.0)
    return E

# Birch-Murnaghan equation of state
def eos_birch_murnaghan(params, vol):
    'From Phys. Rev. B 70, 224107'
    E0, B0, Bp, V0 = params 
    eta = (vol/V0)**(1.0/3.0)
    E = E0 + 9.0*B0*V0/16.0 * (eta**2-1.0)**2 * (6.0 + Bp*(eta**2-1.0) - 4.0*eta**2)
    return E

# Birch equation of state
def eos_birch(params, vol):
    '''
    From Intermetallic compounds: Principles and Practice, Vol. I: Princples
    Chapter 9 pages 195-210 by M. Mehl. B. Klein, D. Papaconstantopoulos
    '''
    E0, B0, Bp, V0 = params 
    E = (E0 + 9.0/8.0*B0*V0*((V0/vol)**(2.0/3.0) - 1.0)**2
            + 9.0/16.0*B0*V0*(Bp-4.)*((V0/vol)**(2.0/3.0) - 1.0)**3)
    return E

# Vinet equation of state
def eos_vinet(params, vol):
    'From Phys. Rev. B 70, 224107'
    E0, B0, Bp, V0 = params 
    eta = (vol/V0)**(1.0/3.0)
    E = E0 + 2.0*B0*V0/(Bp-1.0)**2 * \
        (2.0 - (5.0 + 3.0*Bp*(eta-1.0) - 3.0*eta)*numpy.exp(-3.0*(Bp-1.0)*(eta-1.0)/2.0))
    return E


# Customized input with default and accepted values
def myinput(prompt, default, accepted):
    while True:
        res = input(prompt + " [default=%s]: " % (default))
        if res == '': res = default
        if res in accepted:
            break
        else:
            print("accepted values:", accepted)
    return res



print("Welcome to genPOSCAR.py")
print
#fname = input("Filename containing energy vs volume [volume.dat]: ")
#if fname == '': fname = 'volume.dat'

#try:
#    f = open(fname, 'rt')
#except IOError:
#    sys.stderr.write("Error opening or reading file %s\n" % (fname))
#    sys.exit(1)

# read data from file
#print
#print("Data read from file:")
#vol = []
#ene = []
#while True:
#    line = f.readline().strip()
#    if line == '': break
#    if line[0] == '#' or line[0] == '!': continue
#    v, e = [float(x) for x in line.split()[:2]]
#    vol.append(v)
#    ene.append(e)
#    print(v, e)
#print
#f.close()

# transform to numpy arrays
#vol = numpy.array(vol)
#ene = numpy.array(ene)

# further questions
#is_fitting = True
commentline = input("System name:")
latt_para = float(input("Lattice parameter:"))
vol_unit = myinput("Volume units (ang3/bohr3):", "ang3", ["ang3", "bohr3"])    
latt_type = myinput("Lattice type (sc/fcc/bcc/hex/hcp):", "sc", ["sc", "bcc", "fcc", "hex", "hcp"])
is_primitive = myinput("Is primitive unit cell? (yes/no):", "yes", ["yes", "no"])
is_fitting = myinput("A series of lattice parameters? (yes/no):", "no", ["yes", "no"])
a1 = []
a2 = []
a3 = []

if latt_type == "sc":
    a1 = [1.0, 0.0, 0.0]
    a2 = [0.0, 1.0, 0.0]
    a3 = [0.0, 0.0, 1.0]
elif latt_type == "fcc":
    a1 = [0.5, 0.5, 0.0]
    a2 = [0.0, 0.5, 0.5]
    a3 = [0.5, 0.0, 0.5]
elif latt_type == "bcc": 
    a1 = [0.5, 0.5, -0.5]
    a2 = [-0.5, 0.5, 0.5]
    a3 = [0.5, -0.5, 0.5]
elif latt_type == "hex" :
    interlayer_spacing = input("Interlayer spacing:")
    number_of_layer = input("Number of layers:")
    slab_thick = interlayer_spacing*number_of_layers
    vacuum_thick = input("Vacuum region:")
    cell_thick = slab_thick + vacuum_thick
    a1 = [1.0, 0.0, 0.0]
    a2 = [0.5, sqrt(3)/2, 0.0]
    a3 = [0.0, 0.0, cell_thick/latt_para]
elif latt_type == "hcp" : 
    interlayer_spacing = input("Interlayer spacing:")
    number_of_layer = input("Number of layers:")
    slab_thick = interlayer_spacing*number_of_layers
    vacuum_thick = input("Vacuum region:")
    cell_thick = slab_thick + vacuum_thick  
    a1 = [1.0, 0.0, 0.0]
    a2 = [0.5, sqrt(3)/2, 0.0]
    a3 = [0.0, 0.0, cell_thick/latt_para]
speciesline = input("Species name:")
coordinate_type = myinput("Coordinate type? (c/d):", "d", ["c", "d"]) 
ion_position = [0.0, 0.0, 0.0]
str_a1 = ' '.join(map(str, a1))
str_a2 = ' '.join(map(str, a2))
str_a3 = ' '.join(map(str, a3))
str_ion_position = ' '.join(map(str, ion_position))
if is_fitting == "yes":    
    print("here")
    number_of_points = int(input("Number of fitting points:"))
    points_spacing = float(input("Spacing between fitting points:"))
    print((-1)*float(number_of_points))
    for i in range((-1)*number_of_points, number_of_points):
        latt_para_var = str(latt_para+i*points_spacing)
        cmd = "mkdir "+latt_para_var 
        os.system(cmd) 
        poscar = open(latt_para_var+"/POSCAR", "w")
        poscar.write(commentline+"\n")
        poscar.write(latt_para_var+"\n")
        poscar.write(str_a1+"\n")
        poscar.write(str_a2+"\n")
        poscar.write(str_a3+"\n")
        poscar.write(speciesline+"\n")
        poscar.write(coordinate_type+"\n")
        poscar.write(str_ion_position+"\n")
        poscar.close()
        cmd = "cp KPOINTS "+latt_para_var
        os.system(cmd)
        cmd = "cp POTCAR "+latt_para_var
        os.system(cmd)
        cmd = "cp INCAR "+latt_para_var
        os.system(cmd)


        




quit()

#else:
#    vol_unit = myinput("Lattice units (ang/bohr)", "ang", ["ang", "bohr"])    
#    if vol_unit == "bohr": vol *= 0.52917721     # convert to angstrom
#    fact = 1.0
    # lattice to volume
#    vol = fact * vol**3

ene_unit = myinput("Energy units (eV/Ry/Ha)", "eV", ["eV", "Ry", "Ha"])
if ene_unit == "Ry": ene *= 13.605692            # convert to eV
if ene_unit == "Ha": ene *= 27.211383            # convert to eV
print

# fit a parabola to the data and get inital guess for equilibirum volume
# and bulk modulus
a, b, c = numpy.polyfit(vol, ene, 2)
if latt == "2d":
    a, b, c = numpy.polyfit(latt_const, ene, 2)
V0 = -b/(2*a)
E0 = a*V0**2 + b*V0 + c
B0 = 2*a*V0
Bp = 4.0
if latt == "2d":
    print("a0 = ", V0)
    quit()

# initial guesses in the same order used in the Murnaghan function
x0 = [E0, B0, Bp, V0]

def print_params(label, params):
    E0, B0, Bp, V0 = params
    print(label, ": E0 = %f eV" % (E0))
    print(label, ": B0 = %f GPa" % (B0*160.21765))
    print(label, ": Bp = %f" % (Bp))
    print(label, ": V0 = %f angstrom^3" % (V0))
    print

# fit the equations of state
target = lambda params, y, x: y - eos_murnaghan(params, x)
murn, ier = leastsq(target, x0, args=(ene,vol))
print_params("Murnaghan", murn)

target = lambda params, y, x: y - eos_birch_murnaghan(params, x)
birch_murn, ier = leastsq(target, x0, args=(ene,vol))
print_params("Birch-Murnaghan", birch_murn)

target = lambda params, y, x: y - eos_birch(params, x)
birch, ier = leastsq(target, x0, args=(ene,vol))
print_params("Birch", birch)

target = lambda params, y, x: y - eos_vinet(params, x)
vinet, ier = leastsq(target, x0, args=(ene,vol))
print_params("Vinet", vinet)


try:
    import pylab
except ImportError:
    sys.stderr.write("pylab module non available, skipping plot")
    sys.exit(0)

# plotting
ans = myinput("Do you want to plot the result (yes/no)", "yes", ["yes", "no"])
if ans == "no": sys.exit(0)

import pylab
vfit = numpy.linspace(min(vol),max(vol),100)

pylab.plot(vol, ene-E0, 'ro')
pylab.plot(vfit, eos_murnaghan(murn,vfit)-E0, label='Murnaghan')
pylab.plot(vfit, eos_birch_murnaghan(birch_murn,vfit)-E0, label='Birch-Murnaghan')
pylab.plot(vfit, eos_birch(birch,vfit)-E0, label='Birch')
pylab.plot(vfit, eos_vinet(vinet,vfit)-E0, label='Vinet')
pylab.xlabel('Volume ($\AA^3$)')
pylab.ylabel('Energy (eV)')
pylab.legend(loc='best')
pylab.show()
quit()
