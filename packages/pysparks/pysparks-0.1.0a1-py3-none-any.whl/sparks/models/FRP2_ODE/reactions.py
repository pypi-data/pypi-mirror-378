from enum import Enum, auto

from sparks.models import ReactionNetworkDef, make_reaction


class RxnID(Enum):
    """All possible reactions in the copolymerization system"""

    INIT_DECOMP = auto()
    THERM_INIT_A = auto()
    THERM_INIT_B = auto()

    PROP_R_A = auto()
    PROP_R_B = auto()
    PROP_RA_A = auto()
    PROP_RA_B = auto()
    PROP_RB_A = auto()
    PROP_RB_B = auto()

    PROP_PAA_A = auto()
    PROP_PAA_B = auto()
    PROP_PAB_A = auto()
    PROP_PAB_B = auto()
    PROP_PBA_A = auto()
    PROP_PBA_B = auto()
    PROP_PBB_A = auto()
    PROP_PBB_B = auto()

    DEPROP_PAAA = auto()
    DEPROP_PAAB = auto()
    DEPROP_PABA = auto()
    DEPROP_PABB = auto()
    DEPROP_PBAA = auto()
    DEPROP_PBAB = auto()
    DEPROP_PBBA = auto()
    DEPROP_PBBB = auto()

    TERMC_PAA_PAA = auto()
    TERMC_PAA_PBA = auto()
    TERMC_PBA_PBA = auto()

    TERMC_PAA_PAB = auto()
    TERMC_PAA_PBB = auto()
    TERMC_PBA_PAB = auto()
    TERMC_PBA_PBB = auto()

    TERMC_PAB_PAB = auto()
    TERMC_PAB_PBB = auto()
    TERMC_PBB_PBB = auto()

    TERMD_PAA_PAA = auto()
    TERMD_PAA_PBA = auto()
    TERMD_PBA_PBA = auto()

    TERMD_PAA_PAB = auto()
    TERMD_PAA_PBB = auto()
    TERMD_PBA_PAB = auto()
    TERMD_PBA_PBB = auto()

    TERMD_PAB_PAB = auto()
    TERMD_PAB_PBB = auto()
    TERMD_PBB_PBB = auto()

    CTR_PAA_A = auto()
    CTR_PAA_B = auto()
    CTR_PAB_A = auto()
    CTR_PAB_B = auto()
    CTR_PBA_A = auto()
    CTR_PBA_B = auto()
    CTR_PBB_A = auto()
    CTR_PBB_B = auto()


def initiator_decomposition_rxn() -> ReactionNetworkDef:

    from .model import RateCoefficients, ModelState

    state = ModelState()
    Reaction = make_reaction(RateCoefficients, ModelState)

    return {
        # Initiation
        RxnID.INIT_DECOMP: Reaction(
            reactants={"I": 1},
            products={"R": 2 * 0.5},
            rate=lambda k, s: k.kd * s.I,
        ),
    }


def thermal_initiation_rxn() -> ReactionNetworkDef:

    from .model import RateCoefficients, ModelState

    state = ModelState()
    Reaction = make_reaction(RateCoefficients, ModelState)

    return {
        RxnID.THERM_INIT_A: Reaction(
            reactants={"A": 3},
            products={"RA": 2},
            rate=lambda k, s: k.kthA * (s.A**3),
        ),
        RxnID.THERM_INIT_B: Reaction(
            reactants={"B": 3},
            products={"RB": 2},
            rate=lambda k, s: k.kthB * (s.B**3),
        ),
    }


def propagation_rxn() -> ReactionNetworkDef:

    from .model import RateCoefficients, ModelState

    state = ModelState()
    Reaction = make_reaction(RateCoefficients, ModelState)

    return {
        RxnID.PROP_R_A: Reaction(
            reactants={"R": 1, "A": 1},
            products={"RA": 1},
            rate=lambda k, s: k.kpAA * s.R * s.A,
        ),
        RxnID.PROP_R_B: Reaction(
            reactants={"R": 1, "B": 1},
            products={"RB": 1},
            rate=lambda k, s: k.kpBB * s.R * s.B,
        ),
        RxnID.PROP_RA_A: Reaction(
            reactants={"RA": 1, "A": 1},
            products={"PAA": 1},
            rate=lambda k, s: k.kpAA * s.RA * s.A,
        ),
        RxnID.PROP_RA_B: Reaction(
            reactants={"RA": 1, "B": 1},
            products={"PAB": 1},
            rate=lambda k, s: k.kpAB * s.RA * s.B,
        ),
        RxnID.PROP_RB_A: Reaction(
            reactants={"RB": 1, "A": 1},
            products={"PBA": 1},
            rate=lambda k, s: k.kpBA * s.RB * s.A,
        ),
        RxnID.PROP_RB_B: Reaction(
            reactants={"RB": 1, "B": 1},
            products={"PBB": 1},
            rate=lambda k, s: k.kpBB * s.RB * s.B,
        ),
        RxnID.PROP_PAA_A: Reaction(
            reactants={"PAA": 1, "A": 1},
            products={"PAA": 1},
            rate=lambda k, s: k.kpAA * s.PAA * s.A,
        ),
        RxnID.PROP_PAA_B: Reaction(
            reactants={"PAA": 1, "B": 1},
            products={"PAB": 1},
            rate=lambda k, s: k.kpAB * s.PAA * s.B,
        ),
        RxnID.PROP_PAB_A: Reaction(
            reactants={"PAB": 1, "A": 1},
            products={"PBA": 1},
            rate=lambda k, s: k.kpBA * s.PAB * s.A,
        ),
        RxnID.PROP_PAB_B: Reaction(
            reactants={"PAB": 1, "B": 1},
            products={"PBB": 1},
            rate=lambda k, s: k.kpBB * s.PAB * s.B,
        ),
        RxnID.PROP_PBA_A: Reaction(
            reactants={"PBA": 1, "A": 1},
            products={"PAA": 1},
            rate=lambda k, s: k.kpAA * s.PBA * s.A,
        ),
        RxnID.PROP_PBA_B: Reaction(
            reactants={"PBA": 1, "B": 1},
            products={"PAB": 1},
            rate=lambda k, s: k.kpAB * s.PBA * s.B,
        ),
        RxnID.PROP_PBB_A: Reaction(
            reactants={"PBB": 1, "A": 1},
            products={"PBA": 1},
            rate=lambda k, s: k.kpBA * s.PBB * s.A,
        ),
        RxnID.PROP_PBB_B: Reaction(
            reactants={"PBB": 1, "B": 1},
            products={"PBB": 1},
            rate=lambda k, s: k.kpBB * s.PBB * s.B,
        ),
    }


def depropagation_rxn() -> ReactionNetworkDef:

    from .model import RateCoefficients, ModelState

    state = ModelState()
    Reaction = make_reaction(RateCoefficients, ModelState)

    return {
        RxnID.DEPROP_PAAA: Reaction(
            reactants={"PAA": 1},
            products={"PAA": 1, "A": 1},
            rate=lambda k, s: k.kdAA * s.pAA * s.PAA,
        ),
        RxnID.DEPROP_PAAB: Reaction(
            reactants={"PAB": 1},
            products={"PAA": 1, "B": 1},
            rate=lambda k, s: k.kdAB * s.pAA * s.PAB,
        ),
        RxnID.DEPROP_PABA: Reaction(
            reactants={"PBA": 1},
            products={"PAB": 1, "A": 1},
            rate=lambda k, s: k.kdBA * s.pAB * s.PBA,
        ),
        RxnID.DEPROP_PABB: Reaction(
            reactants={"PBB": 1},
            products={"PAB": 1, "B": 1},
            rate=lambda k, s: k.kdBB * s.pAB * s.PBB,
        ),
        RxnID.DEPROP_PBAA: Reaction(
            reactants={"PAA": 1},
            products={"PBA": 1, "A": 1},
            rate=lambda k, s: k.kdAA * s.pBA * s.PAA,
        ),
        RxnID.DEPROP_PBAB: Reaction(
            reactants={"PAB": 1},
            products={"PBA": 1, "B": 1},
            rate=lambda k, s: k.kdAB * s.pBA * s.PAB,
        ),
        RxnID.DEPROP_PBBA: Reaction(
            reactants={"PBA": 1},
            products={"PBB": 1, "A": 1},
            rate=lambda k, s: k.kdBA * s.pBB * s.PBA,
        ),
        RxnID.DEPROP_PBBB: Reaction(
            reactants={"PBB": 1},
            products={"PBB": 1, "B": 1},
            rate=lambda k, s: k.kdBB * s.pBB * s.PBB,
        ),
    }


def termination_rxn() -> ReactionNetworkDef:

    from .model import RateCoefficients, ModelState

    state = ModelState()
    Reaction = make_reaction(RateCoefficients, ModelState)

    return {
        # Termination (combination)
        RxnID.TERMC_PAA_PAA: Reaction(
            reactants={"PAA": 2},
            products={"PD": 1},
            rate=lambda k, s: 0.5 * k.ktcAA * s.PAA * s.PAA,
        ),
        RxnID.TERMC_PAA_PBA: Reaction(
            reactants={"PAA": 1, "PBA": 1},
            products={"PD": 1},
            rate=lambda k, s: 0.5 * k.ktcAA * s.PAA * s.PBA,
        ),
        RxnID.TERMC_PBA_PBA: Reaction(
            reactants={"PBA": 2},
            products={"PD": 1},
            rate=lambda k, s: 0.5 * k.ktcAA * s.PBA * s.PBA,
        ),
        RxnID.TERMC_PAA_PAB: Reaction(
            reactants={"PAA": 1, "PAB": 1},
            products={"PD": 1},
            rate=lambda k, s: 0.5 * k.ktcAB * s.PAA * s.PAB,
        ),
        RxnID.TERMC_PAA_PBB: Reaction(
            reactants={"PAA": 1, "PBB": 1},
            products={"PD": 1},
            rate=lambda k, s: 0.5 * k.ktcAB * s.PAA * s.PBB,
        ),
        RxnID.TERMC_PBA_PAB: Reaction(
            reactants={"PBA": 1, "PAB": 1},
            products={"PD": 1},
            rate=lambda k, s: 0.5 * k.ktcAB * s.PBA * s.PAB,
        ),
        RxnID.TERMC_PBA_PBB: Reaction(
            reactants={"PBA": 1, "PBB": 1},
            products={"PD": 1},
            rate=lambda k, s: 0.5 * k.ktcAB * s.PBA * s.PBB,
        ),
        RxnID.TERMC_PAB_PAB: Reaction(
            reactants={"PAB": 2},
            products={"PD": 1},
            rate=lambda k, s: 0.5 * k.ktcBB * s.PAB * s.PAB,
        ),
        RxnID.TERMC_PAB_PBB: Reaction(
            reactants={"PAB": 1, "PBB": 1},
            products={"PD": 1},
            rate=lambda k, s: 0.5 * k.ktcBB * s.PAB * s.PBB,
        ),
        RxnID.TERMC_PBB_PBB: Reaction(
            reactants={"PBB": 2},
            products={"PD": 1},
            rate=lambda k, s: 0.5 * k.ktcBB * s.PBB * s.PBB,
        ),
        # Termination (disproportionation)
        RxnID.TERMD_PAA_PAA: Reaction(
            reactants={"PAA": 2},
            products={"PD": 2},
            rate=lambda k, s: k.ktdAA * s.PAA * s.PAA,
        ),
        RxnID.TERMD_PAA_PBA: Reaction(
            reactants={"PAA": 1, "PBA": 1},
            products={"PD": 2},
            rate=lambda k, s: k.ktdAA * s.PAA * s.PBA,
        ),
        RxnID.TERMD_PBA_PBA: Reaction(
            reactants={"PBA": 2},
            products={"PD": 2},
            rate=lambda k, s: k.ktdAA * s.PBA * s.PBA,
        ),
        RxnID.TERMD_PAA_PAB: Reaction(
            reactants={"PAA": 1, "PAB": 1},
            products={"PD": 2},
            rate=lambda k, s: k.ktdAB * s.PAA * s.PAB,
        ),
        RxnID.TERMD_PAA_PBB: Reaction(
            reactants={"PAA": 1, "PBB": 1},
            products={"PD": 2},
            rate=lambda k, s: k.ktdAB * s.PAA * s.PBB,
        ),
        RxnID.TERMD_PBA_PAB: Reaction(
            reactants={"PBA": 1, "PAB": 1},
            products={"PD": 2},
            rate=lambda k, s: k.ktdAB * s.PBA * s.PAB,
        ),
        RxnID.TERMD_PBA_PBB: Reaction(
            reactants={"PBA": 1, "PBB": 1},
            products={"PD": 2},
            rate=lambda k, s: k.ktdAB * s.PBA * s.PBB,
        ),
        RxnID.TERMD_PAB_PAB: Reaction(
            reactants={"PAB": 2},
            products={"PD": 2},
            rate=lambda k, s: k.ktdBB * s.PAB * s.PAB,
        ),
        RxnID.TERMD_PAB_PBB: Reaction(
            reactants={"PAB": 1, "PBB": 1},
            products={"PD": 2},
            rate=lambda k, s: k.ktdBB * s.PAB * s.PBB,
        ),
        RxnID.TERMD_PBB_PBB: Reaction(
            reactants={"PBB": 2},
            products={"PD": 2},
            rate=lambda k, s: k.ktdBB * s.PBB * s.PBB,
        ),
    }


def chain_transfer_rxn() -> ReactionNetworkDef:

    from .model import RateCoefficients, ModelState

    state = ModelState()
    Reaction = make_reaction(RateCoefficients, ModelState)

    return {
        # Chain Transfer to Monomer
        RxnID.CTR_PAA_A: Reaction(
            reactants={"PAA": 1, "A": 1},
            products={"PD": 1, "RA": 1},
            rate=lambda k, s: k.ktrAA * s.PAA * s.A,
        ),
        RxnID.CTR_PAA_B: Reaction(
            reactants={"PAA": 1, "B": 1},
            products={"PD": 1, "RB": 1},
            rate=lambda k, s: k.ktrAB * s.PAA * s.B,
        ),
        RxnID.CTR_PAB_A: Reaction(
            reactants={"PAB": 1, "A": 1},
            products={"PD": 1, "RA": 1},
            rate=lambda k, s: k.ktrBA * s.PAB * s.A,
        ),
        RxnID.CTR_PAB_B: Reaction(
            reactants={"PAB": 1, "B": 1},
            products={"PD": 1, "RB": 1},
            rate=lambda k, s: k.ktrBB * s.PAB * s.B,
        ),
        RxnID.CTR_PBA_A: Reaction(
            reactants={"PBA": 1, "A": 1},
            products={"PD": 1, "RA": 1},
            rate=lambda k, s: k.ktrAA * s.PBA * s.A,
        ),
        RxnID.CTR_PBA_B: Reaction(
            reactants={"PBA": 1, "B": 1},
            products={"PD": 1, "RB": 1},
            rate=lambda k, s: k.ktrAB * s.PBA * s.B,
        ),
        RxnID.CTR_PBB_A: Reaction(
            reactants={"PBB": 1, "A": 1},
            products={"PD": 1, "RA": 1},
            rate=lambda k, s: k.ktrBA * s.PBB * s.A,
        ),
        RxnID.CTR_PBB_B: Reaction(
            reactants={"PBB": 1, "B": 1},
            products={"PD": 1, "RB": 1},
            rate=lambda k, s: k.ktrBB * s.PBB * s.B,
        ),
    }


def reactions() -> ReactionNetworkDef:
    """Combine all reaction definitions into a single network."""
    return {
        **initiator_decomposition_rxn(),
        **thermal_initiation_rxn(),
        **propagation_rxn(),
        **depropagation_rxn(),
        **termination_rxn(),
        **chain_transfer_rxn(),
    }
