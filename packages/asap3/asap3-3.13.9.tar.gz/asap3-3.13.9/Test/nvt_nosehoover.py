import numpy as np
from nvt_module import main
from asap3.md.nvtberendsen import NVTBerendsen
import ase
if ase.__version__ >= '3.25.0':
    from asap3.md.nose_hoover_chain import NoseHooverChainNVT
else:
    NoseHooverChainNVT = None

def nhdynmaker(atoms, T0, dt, tau, rng, logint):
    return NoseHooverChainNVT(atoms, dt, temperature_K=T0, tdamp=tau, logfile='-', loginterval=logint)

def berdynmaker(atoms, T0, dt, tau, rng, logint):
    return NVTBerendsen(atoms, timestep=dt, temperature_K=T0, taut=tau, logfile='-', loginterval=logint)

rng = np.random.default_rng(2718281828459045)   # Use a fixed seed for reproducability
#rng = np.random.default_rng()

if NoseHooverChainNVT is not None:
    main(nhdynmaker, rng, initdyn=berdynmaker)
else:
    print('Test skipped - ASE is too old.')
