from tc_python import *
import matplotlib.pyplot as plt

"""
This example simulates the kinetics of precipitation of both stable and metastable carbides from ferrite phase.
It demonstrates that metastable carbides (cementite and M7C3) may first emerge and then disappear and the stable phase
(M23C6) prevails.
"""

with TCPython():
    sim_results = (SetUp()
                   .set_cache_folder(os.path.basename(__file__) + "_cache")
                   .select_thermodynamic_and_kinetic_databases_with_elements("FEDEMO", "MFEDEMO", ["Fe", "C", "Cr"])
                   .get_system()
                   .with_isothermal_precipitation_calculation()
                   .set_composition_unit(CompositionUnit.MASS_PERCENT)
                   .set_composition("C", 0.1)
                   .set_composition("Cr", 12)
                   .with_matrix_phase(MatrixPhase("BCC_A2")
                                     .with_grain_growth_model(GrainGrowthModel.fixed_grain_size(1.0e-4))
                                     .add_precipitate_phase(PrecipitatePhase("CEMENTITE")
                                                           .set_interfacial_energy(0.167)
                                                           .set_nucleation_at_grain_boundaries()
                                                            )
                                     .add_precipitate_phase(PrecipitatePhase("M7C3")
                                                           .set_interfacial_energy(0.282)
                                                           .set_nucleation_at_grain_boundaries()
                                                            )
                                    .add_precipitate_phase(PrecipitatePhase("M23C6")
                                                            .set_interfacial_energy(0.252)
                                                            .set_nucleation_at_grain_boundaries()
                                                           )
                                     )
                   .set_temperature(1053)
                   .set_simulation_time(4e5)
                   .calculate()
                   )

    time_1, volume_fraction_1 = sim_results.get_volume_fraction_of("CEMENTITE")
    time_2, volume_fraction_2 = sim_results.get_volume_fraction_of("M7C3")
    time_3, volume_fraction_3 = sim_results.get_volume_fraction_of("M23C6")

# Plot result
fig, ax = plt.subplots()
fig.suptitle('Three carbides precipitation', fontsize=14, fontweight='bold')
ax.set_xlabel('Time [s]')
ax.set_ylabel('Volume Fraction')
ax.semilogx(time_1, volume_fraction_1, 'b-', label="Volume fraction of CEMENTITE (Grain boundaries)")
ax.semilogx(time_2, volume_fraction_2, 'r-', label="Volume fraction of M7C3 (Grain boundaries)")
ax.semilogx(time_3, volume_fraction_3, 'g-', label="Volume fraction of M23C6 (Grain boundaries)")
ax.legend()
plt.show()
