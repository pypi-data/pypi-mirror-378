import sys
sys.path.append("..")
import numpy as np
from nvt_module import main
from asap3.md.nvtberendsen import NVTBerendsen


def berdynmaker(atoms, T0, dt, tau, rng, logint):
    return NVTBerendsen(atoms, timestep=dt, temperature_K=T0, taut=tau, logfile='-', loginterval=logint)

#rng = np.random.default_rng(2718281828459045)   # Use a fixed seed for reproducability
rng = np.random.default_rng()
main(berdynmaker, rng, failfluct=True,  parallel=True)
