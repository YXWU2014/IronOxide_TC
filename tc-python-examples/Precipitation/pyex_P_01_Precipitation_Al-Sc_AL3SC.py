from tc_python import *
import matplotlib.pyplot as plt

"""
This example simulates the kinetics of precipitation of Al3Sc from an FCC_A1 solution phase and shows some results,
with minimally required settings. Default values are used for unspecified settings.
"""

with TCPython():
    sim_results = (SetUp()
                   .set_cache_folder(os.path.basename(__file__) + "_cache")
                   .select_thermodynamic_and_kinetic_databases_with_elements("ALDEMO", "MALDEMO", ["Al", "Sc"])
                   .get_system()
                   .with_isothermal_precipitation_calculation()
                   .set_composition_unit(CompositionUnit.MOLE_PERCENT)
                   .set_composition("Sc", 0.18)
                   .set_temperature(623.15)
                   .set_simulation_time(1e7)
                   .with_matrix_phase(MatrixPhase("FCC_A1")
                                     .add_precipitate_phase(PrecipitatePhase("AL3SC"))
                                      )
                   .calculate()
                   )
    time, mean_radius = sim_results.get_mean_radius_of("AL3SC")

# Plot result
fig, ax = plt.subplots()
fig.suptitle('Al3Sc precipitation', fontsize=14, fontweight='bold')
ax.set_xlabel('Time [s]')
ax.set_ylabel('Mean radius [m]')
ax.loglog(time, mean_radius)
plt.show()
