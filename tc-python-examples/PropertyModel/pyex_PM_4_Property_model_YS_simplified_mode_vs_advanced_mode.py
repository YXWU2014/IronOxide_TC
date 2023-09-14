"""
This script demonstrates how to call the Yield Strength model using TC-Python.
Starting from version 2023b, the Yield Strength model can be used in two different modes:
Simplified and Advanced, which is also demonstrated.

This example follows the GUI-example "PM_G_04_Yield_Strength"
"""

from tc_python import *
import matplotlib.pyplot as plt
import numpy as np

with TCPython() as start:
    # See pyex_PM_1_Property_model_interfacial_energy.py on how to list available arguments
    # The result quantity of interest
    quantity = 'Total precipitation strengthening'

    # Define the values for the precipitate radii to be used as stepping axis
    min_r, max_r, no_of_steps = 2e-10, 3e-8, 50
    radii = np.linspace(min_r, max_r, no_of_steps)

    # Set up the system, i.e. corresponding to the "System Definer" in the GUI version
    composition = {"AL": 99.7, "SC": 0.3}
    temperature = 623
    system = (start.
              select_database_and_elements("ALDEMO", composition.keys()).
              get_system())

    # Set up the Property Model calculator, calling the Yield Strength model.
    # Here the mode 'Simplified' is used.
    simplified_calculator = (system.
                             with_property_model_calculation("Yield Strength").
                             set_argument("Select mode", "Simplified").
                             set_argument("precip_str_selection_simplified_mode", True).
                             set_argument("precipitate_simplified_mode-1", "AL3SC").
                             set_temperature(temperature).
                             set_composition("SC", composition["SC"]).
                             set_composition_unit(CompositionUnit.MASS_PERCENT)
                             )

    # Set up another Property Model calculator, calling the Yield Strength model,
    # this time using the mode 'Advanced'. In Advanced mode a significantly larger
    # number of arguments can be set, including four different precipitation strengthening
    # models. Here we select the 'Deschamps model'.
    advanced_calculator = (system.
                           with_property_model_calculation("Yield Strength").
                           set_argument("Select mode", "Advanced").
                           set_argument("precip_str_selection", True).
                           set_argument("Precipitation model list-1", "Deschamps model").
                           set_argument("Precipitate-1", "AL3SC").
                           set_temperature(temperature).
                           set_composition("SC", composition["SC"]).
                           set_composition_unit(CompositionUnit.MASS_PERCENT)
                           )

    # Dictionaries to store the result
    result_dict_simplified = {}
    result_dict_advanced = {}

    for r in radii:
        simplified_calculator.set_argument("precipitate_radius_simplified_mode-1", r)
        result_simplified = simplified_calculator.calculate().get_value_of(quantity)
        result_dict_simplified.update({r: result_simplified})
        print("Simplified mode: Particle radius = {}, {} = {}".format(r, quantity, result_simplified))

        advanced_calculator.set_argument("Precipitate radius deschamps-1", r)
        result_advanced = advanced_calculator.calculate().get_value_of(quantity)
        result_dict_advanced.update({r: result_advanced})
        print("Advanced mode: Particle radius = {}, {} = {}".format(r, quantity, result_advanced))

    # Plot the results
    plt.figure(figsize=(8, 8))
    plt.plot(list(result_dict_simplified.keys()), list(result_dict_simplified.values()), 'o', label="Simplified mode")
    plt.xlabel("Particle radius (m)")
    plt.ylabel(quantity)
    plt.plot(list(result_dict_advanced.keys()), list(result_dict_advanced.values()), label="Advanced mode")
    plt.legend(loc="upper right")
    plt.title("pyex_PM_4_Property_model_YS_simplified_mode_vs_advanced_mode", fontweight='bold')

    plt.show()
