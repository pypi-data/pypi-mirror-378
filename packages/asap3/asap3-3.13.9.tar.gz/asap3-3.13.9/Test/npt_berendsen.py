import numpy as np
from npt_module import main, bulkmodulus, MDLogger
from asap3.md.nptberendsen import NPTBerendsen

def berdynmaker(atoms, T0, p0, dt, *, taut, taup, rng, logint):
    dyn = NPTBerendsen(atoms, timestep=dt, temperature_K=T0, pressure_au=p0, 
                       taut=taut, taup=taup, compressibility_au=1 / bulkmodulus)
    log = MDLogger(dyn, atoms, '-', peratom=True, stress=True)
    dyn.attach(log, interval=logint)
    return dyn

rng = np.random.default_rng(2718281828459045)   # Use a fixed seed for reproducability
main(berdynmaker, rng, failfluct=True)
