import sys
sys.path.append("..")
import numpy as np
from nvt_module import main
from asap3.md.bussi import Bussi
from asap3.mpi import world

def busdynmaker(atoms, T0, dt, tau, rng, logint):
    # tau is the energy relaxation time.  The velocity relaxation time
    # should be the double.
    dyn = Bussi(atoms, dt, temperature_K=T0, taut=tau, logfile='-', loginterval=logint, rng=rng)
    assert dyn.comm.size == world.size
    return dyn

seed = np.random.SeedSequence(2718281828459045)
seed = seed.spawn(world.size)[world.rank]
rng = np.random.default_rng(seed)   # Use a fixed seed for reproducability

main(busdynmaker, rng, parallel=True, sloppytime=True, failfluct=True)
# Note: Fluctuation test always fail in parallel, as the boundaries
# are free in order to test the migration better.  But that changes the
# heat capacity, making the test fail.
