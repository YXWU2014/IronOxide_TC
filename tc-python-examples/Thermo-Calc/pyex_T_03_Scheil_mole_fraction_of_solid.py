import numpy as np
import matplotlib.pyplot as plt
from tc_python import *

"""
Shows the basic usage of Scheil-calculations in TC-Python and mixing them with equilibrium calculations.
"""

database = "ALDEMO"
dependent_element = "Al"
elements = ["Si"]
wt_pct_si = 1.0  # in wt-%
delta_temp = 1.0  # in K, only used for the equilibrium line

with TCPython() as session:
    system = (session.
              set_cache_folder(os.path.basename(__file__) + "_cache").
              select_database_and_elements(database, [dependent_element] + elements).
              get_system())

    scheil_calculation = (system.
                          with_scheil_calculation().
                          set_composition_unit(CompositionUnit.MASS_PERCENT).
                          set_composition("Si", wt_pct_si))

    solidification = scheil_calculation.calculate()

    # 1. Plot the solidification curve (mole fraction solid phases vs. T) including the equilibrium
    scheil_curve = solidification.get_values_grouped_by_stable_phases_of(
        ScheilQuantity.mole_fraction_of_all_solid_phases(),
        ScheilQuantity.temperature())

    temp_min = 1e6
    temp_max = -1e6
    fig, (ax_1, ax_2) = plt.subplots(2)
    for label in scheil_curve:
        section = scheil_curve[label]
        temp_min = min(np.min(section.y), temp_min)
        temp_max = max(np.max(section.y), temp_max)
        ax_1.plot(section.x, np.array(section.y) - 273.15, label=label)

    # calculate the equilibrium solidification line (starting at the liquidus temperature)
    prop_calculation = system.with_property_diagram_calculation()
    result = (prop_calculation.
              with_axis(CalculationAxis(ThermodynamicQuantity.temperature()).
                        set_min(temp_min).
                        set_max(temp_max)).
              set_condition("W(Si)", wt_pct_si / 100).
              calculate())

    temp_eq_frac, liquid_eq_frac = result.get_values_of(ThermodynamicQuantity.temperature(),
                                                        ThermodynamicQuantity.mole_fraction_of_a_phase("LIQUID"))
    solid_eq_frac = 1 - np.array(liquid_eq_frac)
    temp_eq_frac = np.array(temp_eq_frac) - 273.15
    valid_indices = np.where(solid_eq_frac < 1.0)  # cutting off all values with 100% solid

    ax_1.plot(solid_eq_frac[valid_indices], temp_eq_frac[valid_indices], '--', label="Equilibrium")
    ax_1.set_xlabel("Mole fraction of all solid phases [-]")
    ax_1.set_ylabel("Temperature [\N{DEGREE SIGN} C]")

    ax_1.legend(loc="lower left")
    ax_1.set_title("Solidification of AlSi1")

    # 2. Plot the mole fraction of the solid phases separated for each
    groups = \
        solidification.get_values_grouped_by_stable_phases_of(ScheilQuantity.mole_fraction_of_a_solid_phase(ALL_PHASES),
                                                              ScheilQuantity.temperature())

    for group in groups.values():
        ax_2.plot(group.x, np.array(group.y) - 273.15, label=group.label)

    ax_2.set_xlabel("Mole fraction of each solid phase [-]")
    ax_2.set_ylabel("Temperature  [\N{DEGREE SIGN} C]")
    ax_2.legend(loc="lower center")

    fig.set_size_inches(5, 7)
    plt.show()
