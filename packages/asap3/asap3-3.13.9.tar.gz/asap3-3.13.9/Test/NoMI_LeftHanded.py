#!/usr/bin/env python
"""
Tests that EMT works with a twisted, left-hand unit cell when
minimimum-image convention is turned off.
"""

import sys
from numpy import *
from asap3 import *
from asap3.optimize.mdmin import MDMin
from asap3.analysis import CNA, CoordinationNumbers
from asap3.testtools import ReportTest
from ase.lattice.cubic import *


def testFCC(atoms, n, name):
    print("Test '%s': %d atoms" % (name, len(atoms)))
    ReportTest((f"Number of atoms ({name})"), len(atoms), n, 0)
    atoms.calc = EMT(minimum_image=False)
    cn = CoordinationNumbers(atoms)
    ReportTest((f"Coordination number is 12 ({name})"),
               sum(equal(cn, 12)), len(atoms), 0)
    cna = CNA(atoms)
    ReportTest((f"CNA says FCC ({name})"),
               sum(equal(cna, 0)), len(atoms), 0)
    epot = atoms.get_potential_energy()/len(atoms)
    ReportTest((f"Potential energy ({name})"), epot, 0.0, 1e-3)

directions = [[5,1,3], [3,5,1], [2,2,-7]]
a = FaceCenteredCubic(directions=directions, size=(2,2,2), symbol="Cu")
print(a.get_cell())
testFCC(a, 5568, "FCC")


ReportTest.Summary()
