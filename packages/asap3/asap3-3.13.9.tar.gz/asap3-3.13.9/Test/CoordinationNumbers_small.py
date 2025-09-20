from asap3 import EMT, print_version
from asap3.analysis import CoordinationNumbers
from ase.lattice.cubic import FaceCenteredCubic
from asap3.testtools import *
import numpy as np
import ase.data


print_version(1)

element = "Cu"
latconst = ase.data.reference_states[ase.data.atomic_numbers[element]]['a']
nndist = latconst / np.sqrt(2)

sizes = [(3,3,3), (2, 2, 2), (1, 1, 1)]
shells = (1, 2, 3, 4)
expected = (12, 18, 42, 54)
withpotential = (False, True)

for size in sizes:
    for usepot in withpotential:
        print(f'Size: {size}  -  use potential: {usepot}')
        atoms = FaceCenteredCubic(
            directions=[[1,0,0],[0,1,1],[0,0,1]], 
            size=size,
            symbol=element
        )
        
        if usepot:
            atoms.calc = EMT()
            epot = atoms.get_potential_energy()

        for shell, expect in zip(shells, expected):
            cutoff = nndist * (np.sqrt(shell) + np.sqrt(shell + 1)) / 2
            cn = CoordinationNumbers(atoms, cutoff)
            print(cn)
            assert np.equal(cn, expect).all()

