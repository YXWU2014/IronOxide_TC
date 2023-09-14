import matplotlib.pyplot as plt
from tc_python import *
import numpy as np

"""
Carburization of an alloy in a two-step procedure with different boundary conditions in each step.
This example requires the commercial databases TCFE and MOBFE     

As a first step, the carburization is simulated using a activity-flux boundary condition, then
as a second step the homogenization is simulated using a diffusion simulation with closed boundaries.
"""

alloy_mass_pct = {"Cr": 13.0, "Co": 5.0, "Ni": 3.0, "Mo": 2.0, "C": 0.07}
surface_activity = 0.8
temperature = 1243.0
boost_time = 2.0 * 3600.0
diffusion_time = 4.0 * 3600.0
width = 3e-3
carbide_phases = ["M7C3_D101", "M23C6_D84", "CEMENTITE_D011"]
phases_in_diffusion_calc = ["FCC_A1"] + carbide_phases

# Experimental data from T. Turpin et al., Metallurgical and Materials Transactions A, 36(10) (2005) 2751-2760,
# https://doi.org/10.1007/s11661-005-0271-4
exp_distance_boost = [15.2, 64.3, 115.5, 165.8, 216.3, 265.8, 316.5, 365.3, 416.9, 514.6, 614.2, 715.7]
exp_wp_c_boost = [4.2, 3.1, 2.3, 1.6, 1.1, 0.6, 0.4, 0.4, 0.2, 0.1, 0.1, 0.1]
exp_distance_diffusion = [14.8, 65.6, 114.3, 166.0, 214.6, 265.2, 314.9, 365.5, 415.3, 465.0, 513.8, 612.3, 715.8]
exp_wp_c_diffusion = [2.2, 2.1, 2.0, 1.8, 1.5, 1.1, 1.0, 0.7, 0.6, 0.4, 0.3, 0.2, 0.1]


def get_system(session, thermodynamic_database, kinetic_database):
    elements = ["Fe"] + list(alloy_mass_pct.keys())
    system_setup = (session.select_database_and_elements(thermodynamic_database, elements)
                    .without_default_phases()
                    .select_phase("GRAPHITE"))

    for phase in phases_in_diffusion_calc:
        system_setup.select_phase(phase)

    system_setup = system_setup.select_database_and_elements(kinetic_database, elements)
    for phase in phases_in_diffusion_calc:
        system_setup.select_phase(phase)

    return system_setup.get_system()


def get_property_diagram():
    calc = system.with_property_diagram_calculation()
    calc.set_condition('T', temperature)
    for element, comp in alloy_mass_pct.items():
        calc.set_condition('w({})'.format(element), 1e-2 * comp)
    calc.with_axis(CalculationAxis('w(c)').set_min(0.0).set_max(5e-2))
    calc.with_reference_state("C", "GRAPHITE")
    result = calc.calculate()
    return result


with TCPython() as session:
    session.set_cache_folder(os.path.basename(__file__) + "_cache")
    system = get_system(session, "TCFE11", "MOBFE6")

    property_diagram = get_property_diagram()

    comp_profile = CompositionProfile(Unit.MASS_PERCENT)
    for element, comp in alloy_mass_pct.items():
        comp_profile.add(element, ElementProfile.constant(comp))

    region_austenite = (Region("Austenite").set_width(width)
                        .with_grid(CalculatedGrid.geometric()
                                   .set_no_of_points(100)
                                   .set_geometrical_factor(1.02))
                        .with_composition_profile(comp_profile))

    for phase in phases_in_diffusion_calc:
        region_austenite.add_phase(phase)

    calculation = (system.with_isothermal_diffusion_calculation()
                   .with_solver(Solver.homogenization().with_function(HomogenizationFunctions.labyrinth_factor_f2('FCC_A1#1')))
                   .with_reference_state("C", "GRAPHITE")
                   .set_temperature(temperature)
                   .add_region(region_austenite)
                   .with_left_boundary_condition(BoundaryCondition.activity_flux_function().set_flux_function(element_name="C", f="-5E-8", n=1.0, g=str(surface_activity)))
                   .with_right_boundary_condition(BoundaryCondition.closed_system())
                   .set_simulation_time(boost_time))

    sim_results_boost = calculation.calculate()

    calculation_diffusion = (sim_results_boost.with_continued_calculation()
                             .with_left_boundary_condition(BoundaryCondition.closed_system())
                             .set_simulation_time(diffusion_time))

    sim_results = calculation_diffusion.calculate()

    # Plot property diagram
    fig2, (ax2_1, ax2_2) = plt.subplots(2, 1, figsize=(10, 10))
    fig2.suptitle('Equilibrium property diagram T={:.2f}K'.format(temperature), fontsize=14, fontweight='bold')

    groups = property_diagram.get_values_grouped_by_quantity_of('W(C)', 'NPM(*)')
    for group in groups.values():
        ax2_1.plot(100 * np.array(group.x), group.y, label=group.label.split(', ', 1)[1])
    ax2_1.set_xlabel('Mass percent C')
    ax2_1.set_ylabel('Mole-fraction of phases')
    ax2_1.legend(loc='best')

    groups = property_diagram.get_values_grouped_by_quantity_of('ACR(C)', 'NPM(*)')
    for group in groups.values():
        ax2_2.plot(np.array(group.x), group.y, label=group.label.split(', ', 1)[1])
    ax2_2.set_xlabel('Activity of C (with Graphite reference)')
    ax2_2.set_ylabel('Mole-fraction of phases')
    ax2_2.legend(loc='best')

    # Plot Diffusion results
    fig1, (ax2_1, ax2_2, ax2_3) = plt.subplots(3, 1, figsize=(10, 10))
    fig1.suptitle('Carburization with 2h Boost and 2h Diffusion', fontsize=14, fontweight='bold')

    ax2_1.set_xlabel('Distance [micrometer]')
    ax2_1.set_ylabel('Mass percent C')
    d, wp_c_boost = sim_results.get_values_of(DiffusionQuantity.distance(), DiffusionQuantity.mass_fraction_of_a_component("C"), PlotCondition.time(boost_time))
    ax2_1.plot(1e6 * np.array(d), 100 * np.array(wp_c_boost), label="Simulated carbon profile after 2h boost")
    d, wp_c_diffusion = sim_results.get_values_of(DiffusionQuantity.distance(), DiffusionQuantity.mass_fraction_of_a_component("C"), PlotCondition.time(diffusion_time))
    ax2_1.plot(1e6 * np.array(d), 100 * np.array(wp_c_diffusion), label="Simulated carbon profile after 2h boost and 2h diffusion")
    ax2_1.plot(np.array(exp_distance_boost), 1 * np.array(exp_wp_c_boost), linestyle='None', label="Exp. C Boost - T.TURPIN Met. and Mat Trans A Vol 36A, October 2005-2751", marker='o',
               markerfacecolor='None', c='C0')
    ax2_1.plot(np.array(exp_distance_diffusion), 1 * np.array(exp_wp_c_diffusion), linestyle='None', label="Exp. C Diffusion - T.TURPIN et.al. Met. and Mat Trans A Vol 36A, October 2005-2751",
               marker='o', markerfacecolor='None', c='C1')
    ax2_1.legend(loc='upper center')
    ax2_1.set_xlim([0, 1000])

    ax2_2.set_xlabel('Distance [micrometer]')
    ax2_2.set_ylabel('Mole-fraction of carbides')
    ax2_2.set_xlim([0, 1000])

    for phase in carbide_phases:
        d, np_phase = sim_results.get_values_of(DiffusionQuantity.distance(), DiffusionQuantity.mole_fraction_of_a_phase(phase), PlotCondition.time(boost_time))
        ax2_2.plot(1e6 * np.array(d), np_phase, label='2h boost - ' + phase)

    for phase in carbide_phases:
        d, np_phase = sim_results.get_values_of(DiffusionQuantity.distance(), DiffusionQuantity.mole_fraction_of_a_phase(phase), PlotCondition.time(diffusion_time))
        ax2_2.plot(1e6 * np.array(d), np_phase, label='2h boost and 2h diffusion - ' + phase, linestyle='--')
    ax2_2.legend(loc='best')

    ax2_3.set_xlabel('Time [s]')
    ax2_3.set_ylabel('Activity of C at boundary')
    time, ac_c = sim_results.get_values_of(DiffusionQuantity.time(), DiffusionQuantity.activity_of_component("C"), PlotCondition.interface("Austenite", InterfacePosition.LOWER))
    ax2_3.plot(time, ac_c, label="Activity of carbon at left boundary")
    ax2_3.legend(loc='best')
    ax2_3.set_xlim([0, boost_time])

    plt.show()
