from tc_python import *
import os
import numpy as np
import matplotlib.pyplot as plt

"""
Calculates solidification using Scheil with backdiffusion in the primary phase, and compares the result to other
calculation types.
"""

thermodynamic_database = "ALDEMO"
kinetic_database = "MALDEMO"
dependent_element = "Al"
composition = {"Cu": 0.021, "Si": 0.01}  # in mole percent
elements = list(composition.keys())


def get_equilibrium_line(system, liq_temp, temperature_stop, composition):
    """Calculates the equilibrium line using step calculation"""
    temp_step = 1.0
    step_calculator = (system.with_property_diagram_calculation().
                       with_axis(CalculationAxis('T').
                                 set_min(temperature_stop).
                                 set_max(liq_temp).
                                 with_axis_type(AxisType.linear().set_max_step_size(temp_step))))

    for element in composition:
        step_calculator.set_condition(ThermodynamicQuantity.mole_fraction_of_a_component(element), composition[element])

    step_result = step_calculator.calculate()
    return step_result.get_values_grouped_by_quantity_of('NPM(LIQ)', 'T')


def calculate_solidification_curve_with_dictra(system, composition, liq_temp, temperature_stop, cooling_rate, sdas_c, sdas_n):
    """Calculates a solidification curve using the dictra diffusion module"""
    temp_lowest_dictra = 770.0
    time_lowest_dictra = (liq_temp - temp_lowest_dictra) / cooling_rate
    time_stop = (liq_temp - temperature_stop) / cooling_rate
    sim_time_dictra = min(time_stop, time_lowest_dictra)

    liq_phase = "LIQUID"
    dictra_primary_phase = "FCC_A1"

    secondary_dendrite_arm_spacing = sdas_c * cooling_rate ** (-sdas_n)
    composition_profile = CompositionProfile(Unit.MOLE_FRACTION)
    for element in composition:
        composition_profile.add(element, ElementProfile.constant(composition[element]))

    dictra_calc = (system.with_non_isothermal_diffusion_calculation().
                   with_temperature_profile(TemperatureProfile().
                                            add_time_temperature(0, liq_temp).
                                            add_time_temperature(time_stop, temperature_stop)).
                   set_simulation_time(sim_time_dictra).
                   with_timestep_control(TimestepControl().enable_check_interface_position()).
                   add_region(Region("Liquid").
                              set_width(secondary_dendrite_arm_spacing).
                              with_grid(CalculatedGrid.geometric().set_no_of_points(50).set_geometrical_factor(0.95)).
                              with_composition_profile(composition_profile).
                              add_phase(liq_phase).
                              add_phase_allowed_to_form_at_right_interface(dictra_primary_phase, 1e-5)))
    dictra_result = dictra_calc.calculate()

    temp_dictra, poi = dictra_result.get_values_of('T', "Position-Of-Interface Liquid upper", 'interface Liquid upper')

    fraction_solid_dictra = 1.0 - np.array(poi) / secondary_dendrite_arm_spacing

    return fraction_solid_dictra, temp_dictra


if __name__ == "__main__":
    with TCPython() as session:

        cooling_rate = 0.1  # in K/s
        sdas_c = 5.0e-5  # secondary dendrite arm spacing scaling factor in c*cooling_rate^-n (in meters)
        sdas_n = 0.33
        system = (session.
                  set_cache_folder(os.path.basename(__file__) + "_cache").
                  select_thermodynamic_and_kinetic_databases_with_elements(thermodynamic_database, kinetic_database,
                                                                           [dependent_element] + elements).
                  get_system())

        # setup and perform a regular Scheil calculation for comparison
        scheil_calculator = (system.with_scheil_calculation().
                             set_composition_unit(CompositionUnit.MOLE_FRACTION))
        for element in composition:
            scheil_calculator.set_composition(element, composition[element])

        result = scheil_calculator.calculate()
        fraction_solid_regular_scheil, temp_regular_scheil = result.get_values_of(
            ScheilQuantity.mole_fraction_of_all_solid_phases(),
            ScheilQuantity.temperature())

        # setup the back diffusion options and perform Scheil calculation with back diffusion
        scheil_back_diffusion_calculator = \
            scheil_calculator.with_calculation_type(ScheilCalculationType.
                                                  scheil_back_diffusion().
                                                  calculate_secondary_dendrite_arm_spacing().
                                                  set_cooling_rate(cooling_rate).
                                                  set_c(sdas_c).
                                                  set_n(sdas_n).
                                                  set_primary_phasename("AUTOMATIC"))

        result = scheil_back_diffusion_calculator.calculate()
        fraction_solid_back_diffusion, temp_back_diffusion = result.get_values_of(
            ScheilQuantity.mole_fraction_of_all_solid_phases(),
            ScheilQuantity.temperature())

        # calculate the equilbrium line using step calculation
        npm_liq_eq = get_equilibrium_line(system, temp_back_diffusion[0], temp_back_diffusion[-1], composition)

        # calculate solidification line also using Dictra
        fraction_solid_dictra, temp_dictra = calculate_solidification_curve_with_dictra(system, composition,
                                                                                        temp_back_diffusion[0],
                                                                                        temp_back_diffusion[-1],
                                                                                        cooling_rate,
                                                                                        sdas_c, sdas_n)

        # plot the results
        fig, ax1 = plt.subplots(1, figsize=(10, 10))
        plt.suptitle("Al-2.1Cu-1Si Mole%")
        ax1.plot(fraction_solid_back_diffusion, temp_back_diffusion, label='Scheil with back diffusion')
        ax1.plot(fraction_solid_dictra, temp_dictra, label='Dictra')
        ax1.plot(fraction_solid_regular_scheil, temp_regular_scheil, label='Scheil')
        for group in npm_liq_eq.values():
            fraction_solid_eq = 1.0 - np.array(group.x)
            ax1.plot(fraction_solid_eq, group.y, label='Equlibrium', linestyle='--')
        ax1.set_xlabel('Fraction solid phase')
        ax1.set_ylabel('Temperature (K)')
        ax1.legend(loc='best')

        plt.show()
