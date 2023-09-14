from tc_python import *
import matplotlib.pyplot as plt

"""
In this isothermal calculation example, the precipitation of the Cu4Ti phase in a Cu-Ti binary alloy is calculated.
To make a comparison, two separate simulations are performed:
(1) one assuming spherical morphology without elastic strain energy, and
(2) one assuming needle morphology whose shape, determined by competition between interfacial energy and elastic
    strain energy, is changed during the simulation.
"""

with TCPython():
    config = (SetUp()
              .set_cache_folder(os.path.basename(__file__) + "_cache")
              .select_thermodynamic_and_kinetic_databases_with_elements("CUDEMO", "MCUDEMO", ["Cu", "Ti"])
              .select_phase("FCC_L12")
              .select_phase("CU4TI1")
              .get_system()
              .with_isothermal_precipitation_calculation()
              .set_composition_unit(CompositionUnit.MOLE_PERCENT)
              .set_composition("Ti", 1.9)
              .set_temperature(623.15)
              .set_simulation_time(1.e5)
              )
    precip_sphere = PrecipitatePhase("CU4TI1")
    precip_needle = (PrecipitatePhase("CU4TI1")
                     .set_precipitate_morphology(PrecipitateMorphology.NEEDLE)
                     .enable_calculate_aspect_ratio_from_elastic_energy()
                     .set_transformation_strain_calculation_option(TransformationStrainCalculationOption.USER_DEFINED)
                     .with_elastic_properties(PrecipitateElasticProperties()
                                              .set_e11(0.022)
                                              .set_e22(0.022)
                                              .set_e33(0.003)
                                              )
                     )
    matrix_w_sphere = (MatrixPhase("FCC_L12")
                       .set_mobility_adjustment(element="all", prefactor=100.0)
                       .add_precipitate_phase(precip_sphere))
    matrix_w_needle = (MatrixPhase("FCC_L12")
                       .set_mobility_adjustment(element="all", prefactor=100.0)
                       .with_elastic_properties_cubic(168.4, 121.4, 75.4)
                       .add_precipitate_phase(precip_needle)
                       )

    result_sphere = config.with_matrix_phase(matrix_w_sphere).calculate()
    result_needle = config.with_matrix_phase(matrix_w_needle).calculate()

    time_2, mean_aspect_ratio_2 = result_needle.get_mean_aspect_ratio_of("CU4TI1")

    time_1, number_density_1 = result_sphere.get_number_density_of("CU4TI1")
    time_2, number_density_2 = result_needle.get_number_density_of("CU4TI1")

    length_1, f_1 = result_needle.get_size_distribution_for_radius_of("CU4TI1",1e5)
    length_2, f_2 = result_needle.get_aspect_ratio_distribution_for_radius_of("CU4TI1", 1e5)

    time_1, mean_radius_1 = result_sphere.get_mean_radius_of("CU4TI1")
    time_2, mean_radius_2 = result_needle.get_mean_radius_of("CU4TI1")

# Plot results
fig, ax = plt.subplots()
fig.suptitle('Cu4Ti1', fontsize=14, fontweight='bold')
ax.set_xlabel('Time [s]')
ax.set_ylabel('Mean aspect ratio')
ax.semilogx(time_2, mean_aspect_ratio_2, 'r-', label="Mean aspect ratio of CU4TI1 (Bulk) (Needle)")
ax.legend()

fig, ax = plt.subplots()
ax.set_xlabel('Time [s]')
ax.set_ylabel('Number density [m^-3]')
ax.loglog(time_1, number_density_1, 'b-', label="Number density of CU4TI1 (Bulk) (Sphere)")
ax.loglog(time_2, number_density_2, 'r-', label="Number density of CU4TI1 (Bulk) (Needle)")
ax.legend()

fig, ax = plt.subplots()
ax_twin = ax.twinx()
ax.set_xlabel('Length [m]')
ax.set_ylabel('Size distribution [m^-4]')
ax_twin.set_ylabel('Aspect ratio distribution')
ax.plot(length_1, f_1, 'b-', label="Size distribution of CU4TI1 (Bulk) (Needle)")
ax_twin.plot(length_2, f_2, 'r-', label="Aspect ratio distribution of CU4TI1 (Bulk) (Needle)")
ax.legend()

fig, ax = plt.subplots()
ax.set_xlabel('Time [s]')
ax.set_ylabel('Length [m]')
ax.loglog(time_1, mean_radius_1, 'b-', label="Mean radius of CU4TI1 (Bulk) (Sphere)")
ax.loglog(time_2, mean_radius_2, 'r-', label="Mean radius of CU4TI1 (Bulk) (Needle)")
ax.legend()
plt.show()
