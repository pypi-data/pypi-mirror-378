from typing import TypeAlias
import numpy as np
from numpy.typing import NDArray


NDArrayType: TypeAlias = NDArray[np.floating]


#################
### Constants ###
#################

# Small value to avoid division by zero
EPS = 1e-40

# Avogadro's number (mol^-1)
NA = 6.022e23

# Gas constants
R_J = 8.314  # J/mol/K
R_cal = 1.9872036  # cal/mol/K
