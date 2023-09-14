from tc_python import *
import matplotlib.pyplot as plt
import numpy as np

"""
Diffusion with an Inactive Phase Forming in the Presence of a Driving Force

This example simulates a moving boundary problem that is initially a one-phase austenite region. 
Due to the available driving force, a new ferrite region is starting to grow at the left interface 
of the austenite region. 

Initially a constant concentration profile is defined within the single-phase region.

The example uses a minimum number of required settings. Default values are used for any 
unspecified settings.
"""


with TCPython() as session:
    system = (session
                .set_cache_folder(os.path.basename(__file__) + "_cache")
                .select_thermodynamic_and_kinetic_databases_with_elements("FEDEMO", "MFEDEMO", ["Fe", "C"])
                .without_default_phases()
                .select_phase("FCC_A1")
                .select_phase("BCC_A2")
                .get_system())

    calculator = (system
                    .with_non_isothermal_diffusion_calculation()
                    .with_temperature_profile(TemperatureProfile()
                                                .add_time_temperature(0, 1173)
                                                .add_time_temperature(773, 1050)
                                                .add_time_temperature(1000, 1050))
                    .set_simulation_time(1000)
                    .add_region(Region("Austenite")
                                    .set_width(2000e-6)
                                    .with_grid(CalculatedGrid.geometric()
                                                .set_no_of_points(50)
                                                .set_geometrical_factor(1.05))
                                    .with_composition_profile(CompositionProfile(Unit.MASS_PERCENT)
                                                                .add("C", ElementProfile.constant(0.15)))
                                    .add_phase("FCC_A1")
                                    .add_phase_allowed_to_form_at_left_interface("BCC_A2")))

    result = calculator.calculate()

    fig, ax = plt.subplots()
    fig.suptitle('Mass fraction of C', fontsize=14, fontweight='bold')
    ax.set_xlabel(u'Distance [\u03BCm]')
    ax.set_ylabel('C-content [wt-%]')
    plt.xlim(0, 150)

    distance, c = result.get_mass_fraction_of_component_at_time("C", 400.0)
    plt.plot(np.array(distance) * 1e6, np.array(c) * 100, label="400 s")
    distance, c = result.get_mass_fraction_of_component_at_time("C", 600.0)
    plt.plot(np.array(distance) * 1e6, np.array(c) * 100, label="600 s")
    distance, c = result.get_mass_fraction_of_component_at_time("C", 800.0)
    plt.plot(np.array(distance) * 1e6, np.array(c) * 100, label="800 s")
    distance, c = result.get_mass_fraction_of_component_at_time("C", SimulationTime.LAST)
    plt.plot(np.array(distance) * 1e6, np.array(c) * 100, label="1000 s")
    legend = ax.legend(loc='upper right')
    plt.show()
