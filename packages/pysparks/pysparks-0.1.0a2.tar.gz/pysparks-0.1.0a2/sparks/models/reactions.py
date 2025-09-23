from typing import Callable, Dict, Type, TypeAlias, Generic, TypeVar
from enum import Enum
from dataclasses import dataclass

import numpy as np

from sparks.core import NDArrayType
from .state import StateType

# Type variables for generic types
RateType = TypeVar("RateType")
RxnIDType = TypeVar("RxnIDType", bound=Enum)


@dataclass
class Reaction(Generic[RateType, StateType]):
    """
    Represents a single chemical reaction with reactants, products, and a rate law.

    Args:
        reactants: Dict mapping species names to their stoichiometric coefficients.
        products: Dict mapping species names to their stoichiometric coefficients.
        rate: Function that calculates the rate of the reaction given the rate coefficients and state.
            def rate_fn(k: RateType, state: StateType) -> NDArrayType:
                pass
    """

    reactants: Dict[str, float]
    products: Dict[str, float]
    rate: Callable[[RateType, StateType], NDArrayType]


def make_reaction(rate_cls: Type[RateType], state_cls: Type[StateType]):
    """Factory function that returns a properly typed Reaction constructor"""

    def typed_reaction(
        reactants: Dict[str, float],
        products: Dict[str, float],
        rate: Callable[[RateType, StateType], NDArrayType],
    ) -> Reaction[RateType, StateType]:
        return Reaction(reactants=reactants, products=products, rate=rate)

    return typed_reaction


# Type alias for a reaction network definition
ReactionNetworkDef: TypeAlias = Dict[RxnIDType, Reaction[RateType, StateType]]


def calculate_rates(
    state: StateType,
    k: RateType,
    reactions: ReactionNetworkDef,
) -> Dict[RxnIDType, NDArrayType]:
    """
    Calculate the rate of each reaction in the system.

    Args:
        state: Current system state.
        k: Rate coefficients.
        reactions: Reaction network definition.

    Returns:
        Dict mapping reaction IDs to their rates.
    """
    return {rxn_id: rxn.rate(k, state) for rxn_id, rxn in reactions.items()}


def calculate_probabilities(
    state: StateType,
    k: RateType,
    reactions: ReactionNetworkDef,
) -> Dict[RxnIDType, NDArrayType]:
    """
    Calculate the probability of each reaction occurring.

    Probabilities are normalized such that they sum to 100%.

    Args:
        state: Current system state.
        k: Rate coefficients
        reactions: Reaction network definition.

    Returns:
        Dict mapping reaction IDs to their probabilities (0-100%).
    """
    rates = calculate_rates(state, k, reactions)

    total_rate = np.zeros_like(next(iter(rates.values())), dtype=float)
    for rate in rates.values():
        total_rate += rate

    # Convert to probabilities
    return {
        rxn_id: np.where(total_rate > 0, 100 * rate / total_rate, 0.0)
        for rxn_id, rate in rates.items()
    }


def validate_reaction_network(
    state_class: Type[StateType],
    reactions: ReactionNetworkDef,
) -> None:
    """
    Validate that all species in reactions exist in the state class.

    Args:
        state_class: State class with species as fields.
        reactions: Reaction network to validate.

    Raises:
        ValueError: If any species in reactions don't exist in the state class.
    """

    valid_species = set(state_class.get_species_names())

    for rxn_id, reaction in reactions.items():

        # Check reactants
        invalid_reactants = set(reaction.reactants.keys()) - valid_species
        if invalid_reactants:
            raise ValueError(
                f"Reaction {rxn_id} has invalid reactants: {invalid_reactants}. "
                f"Valid species are: {valid_species}."
            )

        # Check products
        invalid_products = set(reaction.products.keys()) - valid_species
        if invalid_products:
            raise ValueError(
                f"Reaction {rxn_id} has invalid products: {invalid_products}. "
                f"Valid species are: {valid_species}."
            )
