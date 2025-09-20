import sys
sys.path.append("..")
import numpy as np
from nvt_module import main
from asap3.md.nvtberendsen import NVTBerendsen
import ase
if ase.__version__ >= '3.25.0':
    from asap3.md.nose_hoover_chain import NoseHooverChainNVT
else:
    NoseHooverChainNVT = None
from asap3.mpi import world

def nhdynmaker(atoms, T0, dt, tau, rng, logint):
    return NoseHooverChainNVT(atoms, dt, temperature_K=T0, tdamp=tau, logfile='-', loginterval=logint)

def berdynmaker(atoms, T0, dt, tau, rng, logint):
    return NVTBerendsen(atoms, timestep=dt, temperature_K=T0, taut=tau, logfile='-', loginterval=logint)

seed = np.random.SeedSequence(2718281828459045)
seed = seed.spawn(world.size)[world.rank]
rng = np.random.default_rng(seed)   # Use a fixed seed for reproducability

if NoseHooverChainNVT is not None:
    main(nhdynmaker, rng, initdyn=berdynmaker, parallel=True, sloppytime=True, failfluct=True)
else:
    print('Test skipped: ASE too old for NoseHoverChainNVT in parallel.')
# Note: Fluctuation test always fail in parallel, as the boundaries
# are free in order to test the migration better.  But that changes the
# heat capacity, making the test fail.
