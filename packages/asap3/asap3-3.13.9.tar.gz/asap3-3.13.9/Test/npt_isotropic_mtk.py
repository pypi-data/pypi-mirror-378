import numpy as np
from npt_module import main, bulkmodulus, MDLogger
try:
    from asap3.md.nose_hoover_chain import IsotropicMTKNPT
except ImportError:
    IsotropicMTKNPT = None
from asap3.md.nptberendsen import NPTBerendsen

def mktdynmaker(atoms, T0, p0, dt, *, taut, taup, rng, logint):
    dyn = IsotropicMTKNPT(atoms, timestep=dt, temperature_K=T0, pressure_au=p0, 
                          tdamp=taut, pdamp=taup)
    log = MDLogger(dyn, atoms, '-', peratom=True, stress=True)
    dyn.attach(log, interval=logint)
    return dyn

def berdynmaker(atoms, T0, p0, dt, *, taut, taup, rng, logint):
    dyn = NPTBerendsen(atoms, timestep=dt, temperature_K=T0, pressure_au=p0, 
                       taut=taut, taup=taup, compressibility_au=1 / bulkmodulus)
    log = MDLogger(dyn, atoms, '-', peratom=True, stress=True)
    dyn.attach(log, interval=logint)
    return dyn

if IsotropicMTKNPT is not None:
    rng = np.random.default_rng(3141592)
    main(mktdynmaker, rng, initdyn=berdynmaker, failfluct=False)
else:
    print('Skipping test of IsotropicMTKNPT - ASE is too old.')

# Notes regarding IsotropicMKT
#
# Take pressure in a.u.

