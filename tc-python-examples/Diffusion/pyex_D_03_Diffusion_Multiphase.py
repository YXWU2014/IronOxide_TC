from tc_python import *
import matplotlib.pyplot as plt

"""
Diffusion in a Single Region with Multiple Phases

This example simulates diffusion in a single region having multiple phases. Initially a 
step concentration profile is defined within the single region. Due to the multiple phases,
the default `AutomaticSolver` uses the 'homogenization mode'. 

The example uses a minimum number of required settings. Default values are used for any 
unspecified settings.
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
                    .with_solver(Solver.homogenization()
                        .with_function(HomogenizationFunctions.general_lower_hashin_shtrikman()))
                    .set_temperature(1100 + 273.15)
                    .set_simulation_time(100.0 * 3600)
                    .add_region(Region("Diffcouple")
                        .set_width(0.003)
                            .with_grid(CalculatedGrid.double_geometric()
                            .set_no_of_points(60)
                            .set_lower_geometrical_factor(0.85)
                            .set_upper_geometrical_factor(1.15))
                        .with_composition_profile(CompositionProfile(Unit.MOLE_PERCENT)
                            .add("Cr", ElementProfile.step(25.7, 42.3, 0.0015))
                            .add("Ni", ElementProfile.step(6.47, 27.5, 0.0015)))
                        .add_phase("FCC_A1")
                        .add_phase("BCC_A2")))

    result = calculator.calculate()

    # this is the most general option to plot diffusion results, if possible instead the specialized methods
    # should be used
    distance, mole_frac_fcc = result.get_values_of(DiffusionQuantity.distance(),
                                                   DiffusionQuantity.mole_fraction_of_a_phase("FCC"),
                                                   PlotCondition.time(100.0 * 3600))

fig, ax = plt.subplots()
fig.suptitle('Multiphase diffusion couple', fontsize=14, fontweight='bold')
ax.set_xlabel('Distance [m]')
ax.set_ylabel('Phase fraction of FCC')
plt.plot(distance, mole_frac_fcc)
plt.show()
