from tc_python import *
import matplotlib.pyplot as plt
import numpy as np

"""
Moving Boundary Diffusion Couple for an Fe-Ni-Cr Alloy

This example simulates the diffusion paths in a moving boundary problem between two multiphase regions. 
Due to the multiple phases, the default `AutomaticSolver` uses the 'homogenization mode'. Initially 
there is a concentration profile with a step between the regions.

The example uses a minimum number of required settings. Default values are used for any unspecified settings.
"""


with TCPython() as session:
    system = (session
                .set_cache_folder(os.path.basename(__file__) + "_cache")
                .select_thermodynamic_and_kinetic_databases_with_elements("FEDEMO", "MFEDEMO", ["Fe", "Cr", "Ni"])
                .without_default_phases()
                .select_phase("FCC_A1")
                .select_phase("BCC_A2")
                .get_system())

    calculator = (system
                    .with_isothermal_diffusion_calculation()
                    .set_temperature(1100 + 273.15)
                    .set_simulation_time(3600 * 1000)
                    .add_region(Region("alpha")
                                    .set_width(9.345E-5)
                                    .with_grid(CalculatedGrid.geometric()
                                                .set_no_of_points(50)
                                                .set_geometrical_factor(0.8))
                                    .with_composition_profile(CompositionProfile(Unit.MASS_FRACTION)
                                                                .add("Cr", ElementProfile.constant(0.38))
                                                                .add("Ni", ElementProfile.constant(1.0E-5)))
                                    .add_phase("BCC_A2"))
                    .add_region(Region("gamma")
                                    .set_width(5.0E-4)
                                    .with_grid(CalculatedGrid.geometric()
                                                .set_no_of_points(50)
                                                .set_geometrical_factor(1.05))
                                    .with_composition_profile(CompositionProfile(Unit.MASS_FRACTION)
                                                                .add("Cr", ElementProfile.constant(0.27))
                                                              .add("Ni", ElementProfile.constant(0.28)))
                                    .add_phase("FCC_A1")))

    result = calculator.calculate()

    # Plot result
    fig, ax = plt.subplots()
    fig.suptitle('Diffusion paths in a Fe-Cr-Ni diffusion couple', fontsize=14, fontweight='bold')
    ax.set_xlabel('Ni-content [wt-%]')
    ax.set_ylabel('Cr-content [wt-%]')
    plt.xlim(0, 40)
    plt.ylim(0, 40)

    ni, cr = result.get_values_of(DiffusionQuantity.mass_fraction_of_a_component("Ni"),
                                       DiffusionQuantity.mass_fraction_of_a_component("Cr"),
                                       PlotCondition.time(3600.0),
                                       IndependentVariable.distance())
    plt.plot(np.array(ni) * 100, np.array(cr) * 100, label="1 h")
    ni, cr = result.get_values_of(DiffusionQuantity.mass_fraction_of_a_component("Ni"),
                                       DiffusionQuantity.mass_fraction_of_a_component("Cr"),
                                       "time 36000.0",
                                       IndependentVariable.distance())
    plt.plot(np.array(ni) * 100, np.array(cr) * 100, label="10 h")
    ni, cr = result.get_values_of(DiffusionQuantity.mass_fraction_of_a_component("Ni"),
                                       DiffusionQuantity.mass_fraction_of_a_component("Cr"),
                                       PlotCondition.time(360000.0),
                                       IndependentVariable.distance())
    plt.plot(np.array(ni) * 100, np.array(cr) * 100, label="100 h")
    ni, cr = result.get_values_of(DiffusionQuantity.mass_fraction_of_a_component("Ni"),
                                       DiffusionQuantity.mass_fraction_of_a_component("Cr"),
                                       PlotCondition.time(3600000.0),
                                       IndependentVariable.distance())
    plt.plot(np.array(ni) * 100, np.array(cr) * 100, label="1000 h")
    legend = ax.legend(loc='upper right')
    plt.show()
