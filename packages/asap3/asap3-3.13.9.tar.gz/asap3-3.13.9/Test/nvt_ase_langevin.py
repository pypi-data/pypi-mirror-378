import numpy as np
from nvt_module import main
from ase.md.langevin import Langevin


def lgvdynmaker(atoms, T0, dt, tau, rng, logint):
    # tau is the energy relaxation time.  The velocity relaxation time
    # should be the double.

    return Langevin(atoms, dt, temperature_K=T0, friction=1/(2*tau), logfile='-', loginterval=logint, rng=rng)

rng = np.random.default_rng(271828182845904523)   # Use a fixed seed for reproducability
main(lgvdynmaker, rng, sloppytime=True)
