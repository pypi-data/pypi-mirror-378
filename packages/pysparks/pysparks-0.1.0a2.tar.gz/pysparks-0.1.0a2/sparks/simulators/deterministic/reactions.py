from __future__ import annotations
from typing import Type

import numpy as np

from sparks.core import NDArrayType
from sparks.models import (
    RateType,
    StateType,
    ReactionNetworkDef,
    calculate_rates,
    ODEFunction,
)


def optimized_reaction_odes(
    state_class: Type[StateType], reactions: ReactionNetworkDef
) -> ODEFunction:
    """
    Returns an optimized ODE function that pre-computes field mappings.
    """

    # Pre-compute mappings once (closure captures these)
    valid_fields = state_class._data_fields()
    field_map = {f.name: i for i, f in enumerate(valid_fields)}
    print(f"Field map: {field_map}")

    print(f"All possible fields: {list(field_map.keys())}")

    # Check which fields are actually used in reactions
    used_fields = set()
    for rxn_id, reaction in reactions.items():
        used_fields.update(reaction.reactants.keys())
        used_fields.update(reaction.products.keys())
    print(f"Fields used in reactions: {used_fields}")

    # Pre-process reactions for faster access
    reaction_data = []
    for rxn_id, reaction in reactions.items():
        reactant_indices = [
            (field_map[species], stoich)
            for species, stoich in reaction.reactants.items()
            if species in field_map
        ]

        product_indices = [
            (field_map[species], stoich)
            for species, stoich in reaction.products.items()
            if species in field_map
        ]

        reaction_data.append((rxn_id, reaction, reactant_indices, product_indices))

    def optimized_ode_function(
        k: RateType,
        t: NDArrayType,
        state: StateType,
    ) -> StateType:
        """The actual optimized ODE function."""
        # Initialize derivative array
        dydt_array = np.zeros(len(field_map))

        # Calculate rates
        rates = calculate_rates(state, k, reactions)

        # Apply stoichiometry using pre-computed indices
        for rxn_id, reaction, reactant_indices, product_indices in reaction_data:
            rate_value = rates[rxn_id]

            # Consumption
            for species_idx, stoich in reactant_indices:
                dydt_array[species_idx] -= stoich * rate_value

            # Formation
            for species_idx, stoich in product_indices:
                dydt_array[species_idx] += stoich * rate_value

        # Convert back to state object
        return state_class.from_array(dydt_array, t=t)

    return optimized_ode_function
