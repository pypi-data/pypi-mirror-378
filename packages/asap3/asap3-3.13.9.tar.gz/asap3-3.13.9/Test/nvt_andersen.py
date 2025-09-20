import numpy as np
from nvt_module import main
from ase.md.andersen import Andersen
import ase

def anddynmaker(atoms, T0, dt, tau, rng, logint):
    # tau is the energy relaxation time.  The velocity relaxation time
    # should be the double.
    aprob = dt / tau
    return Andersen(atoms, dt, temperature_K=T0, andersen_prob=aprob, logfile='-', loginterval=logint, rng=rng)

if ase.__version__ >= '3.24.0':
    rng = np.random.default_rng(2718281828459045)   # Use a fixed seed for reproducability
    #rng = np.random.default_rng()
    main(anddynmaker, rng, sloppytime=True)
else:
    print('Test skipped - ASE too old.')
