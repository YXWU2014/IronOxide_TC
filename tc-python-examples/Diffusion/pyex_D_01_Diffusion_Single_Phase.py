from tc_python import *
import matplotlib.pyplot as plt

"""
Diffusion within a Single Phase Austenitic Region of an Fe-Ni Alloy

This example simulates diffusion within a single phase austenitic region of an Fe-Ni alloy. The  
initial condition is a linear gradient from 10 wt-% - 50 wt-% Ni at 1400 K. 

The example uses a minimum number of required settings. Default values are used for any unspecified settings.
"""


with TCPython() as session:
    system = (session
        .set_cache_folder(os.path.basename(__file__) + "_cache")
        .select_thermodynamic_and_kinetic_databases_with_elements("FEDEMO", "MFEDEMO", ["Fe", "Ni"])
        .get_system())

    calculator = (system
                    .with_isothermal_diffusion_calculation()
                    .set_temperature(1400.0)
                    .set_simulation_time(108000.0)
                    .add_region(Region("Austenite")
                        .set_width(1E-4)
                        .with_grid(CalculatedGrid.linear()
                            .set_no_of_points(50))
                            .with_composition_profile(CompositionProfile()
                                .add("Ni", ElementProfile.linear(10.0, 50.0)))
                        .add_phase("FCC_A1")))
    results = calculator.calculate()

    distance, mass_frac_ni = results.get_mass_fraction_of_component_at_time("Ni", SimulationTime.LAST)


fig, ax = plt.subplots()
fig.suptitle('Single region Fe-Ni', fontsize=14, fontweight='bold')
ax.set_xlabel('Distance [m]')
ax.set_ylabel('Mass fraction of Ni')
plt.plot(distance, mass_frac_ni)
plt.show()
