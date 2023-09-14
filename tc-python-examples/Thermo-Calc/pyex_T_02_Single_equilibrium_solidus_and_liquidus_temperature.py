from tc_python import *

"""
This example shows how to create a single equilibrium calculation                
from a ternary system and configure it to calculate the solidus 
and liquidus temperature using fixed phase conditions for the 
liquid phase. 
 
There can be multiple solutions to a fixed phase condition and it is 
good practice to perform a regular equilibrium calculation close to 
where the phase transition is. This example starts with an equilibrium 
calculation at 1700K in order to get good start values.           
"""


def list_stable_phases(calc_result):
    """
    List the stable phases and their amount on screen.

    Args:
        calc_result: Calculation result from an equilibrium calculation
    """
    stable_phases = calc_result.get_stable_phases()
    for phase in stable_phases:
        print("Amount of " + phase + " = {0:.3f}".format(calc_result.get_value_of('NP(' + phase + ')')))


with TCPython() as session:
    # create equilibrium calculation object and set conditions
    eq_calculation = (
        session.
            set_cache_folder(os.path.basename(__file__) + "_cache").
            select_database_and_elements("FEDEMO", ["Fe", "Cr", "C"]).
            get_system().
            with_single_equilibrium_calculation().
            set_condition(ThermodynamicQuantity.temperature(), 1700.0).
            set_condition(ThermodynamicQuantity.mass_fraction_of_a_component("Cr"), 0.1).
            set_condition(ThermodynamicQuantity.mass_fraction_of_a_component("C"), 0.01)

    )

    # calculate equilibrium and list stable phases
    calc_result = eq_calculation.calculate()
    print("\nEquilibrium at temperature: {0:.2f} K".format(
        calc_result.get_value_of(ThermodynamicQuantity.temperature())) + ", stable phases:")
    list_stable_phases(calc_result)

    # calculate liquidus temperature and list stable phases
    calc_result = (eq_calculation
                   .remove_condition(ThermodynamicQuantity.temperature())
                   .set_phase_to_fixed("LIQUID", 1.0)
                   .calculate())
    print("\nLiquidus temperature: {0:.2f} K".format(calc_result.get_value_of(ThermodynamicQuantity.temperature())))
    list_stable_phases(calc_result)

    # calculate solidus temperature and list stable phases
    calc_result = (eq_calculation
                   .set_phase_to_fixed("LIQUID", 0.0)
                   .calculate())
    print("\nSolidus temperature: {0:.2f} K".format(calc_result.get_value_of(ThermodynamicQuantity.temperature())))
    list_stable_phases(calc_result)
