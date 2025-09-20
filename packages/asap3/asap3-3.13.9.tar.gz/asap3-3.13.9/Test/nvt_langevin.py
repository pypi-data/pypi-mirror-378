import numpy as np
from nvt_module import main
from asap3.md.langevin import Langevin


def lgvdynmaker(atoms, T0, dt, tau, rng, logint):
    # tau is the energy relaxation time.  The velocity relaxation time
    # should be the double.

    # Cannot pass the rng to Asap's Langevin, instead use it to create a seed
    seed = rng.integers(0, 1 << 30)
    print(f'Seed: {seed}')
    return Langevin(atoms, dt, temperature_K=T0, friction=1/(2*tau), logfile='-', loginterval=logint, seed=seed)

rng = np.random.default_rng(2718281828459045)   # Use a fixed seed for reproducability
#rng = np.random.default_rng()
main(lgvdynmaker, rng, sloppytime=True)
