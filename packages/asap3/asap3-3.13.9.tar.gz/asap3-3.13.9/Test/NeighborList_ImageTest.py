from asap3 import *
from ase.lattice.cubic import FaceCenteredCubic
from asap3.testtools import *
from numpy import *
import ase.data

print_version(1)

element = "Cu"
latconst = ase.data.reference_states[ase.data.atomic_numbers[element]]['a']

atoms = FaceCenteredCubic(directions=[[1,0,0],[0,1,1],[0,0,1]], size=(1,1,1),
                          symbol=element, debug=0)

r = atoms.get_positions()
#r += (0.001, 0.001, 0.001)
#atoms.set_positions(r)

print(r)

atoms.calc = EMT(minimum_image=False)
epot = atoms.get_potential_energy()
print("Potential energy:", epot/len(atoms))

nblist = atoms.calc.get_neighborlist()

for i, lst in enumerate(nblist):
    n = len(lst)
    print(f'Atom {i} has {n} neighbors:')
    print('  ', str(lst))
    
