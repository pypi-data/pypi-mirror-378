import numpy as np
from nvt_module import main
try:
    from asap3.md.bussi import Bussi
except ImportError:
    Bussi = None

def busdynmaker(atoms, T0, dt, tau, rng, logint):
    # tau is the energy relaxation time.  The velocity relaxation time
    # should be the double.
    return Bussi(atoms, dt, temperature_K=T0, taut=tau, logfile='-', loginterval=logint, rng=rng)

rng = np.random.default_rng(2718281828459045)   # Use a fixed seed for reproducability
#rng = np.random.default_rng()

if Bussi is not None:
    main(busdynmaker, rng, sloppytime=True)
else:
    print('Test skipped - ASE is too old.')
