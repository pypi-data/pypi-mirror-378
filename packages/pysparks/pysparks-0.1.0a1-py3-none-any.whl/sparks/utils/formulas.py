import numpy as np
from .constants import R_J


def arrhenius_eqn(A, Ea, R=R_J):
    def arrhenius(T_K):
        return A * np.exp(-Ea / (R * T_K))

    return arrhenius


def ln_arrhenius_eqn(A, Ea, R=R_J):
    def ln_arrhenius(T_K):
        return np.exp(A - Ea / (R * T_K))

    return ln_arrhenius


def get_arrhenius_const(Ea_J_mol, k, T_K):
    return k / np.exp(-Ea_J_mol / (R_J * T_K))


def calculate_K(T, deltaH, deltaS):
    return np.exp(deltaH / (R_J * T) - deltaS / R_J)


def cal_to_J(cal):
    return cal * 4.184


def kcal_to_J(kcal):
    return kcal * 4184


def C_to_K(C):
    return C + 273.15


def K_to_C(K):
    return K - 273.15
