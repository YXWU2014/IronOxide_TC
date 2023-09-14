import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import lognorm
from tc_python import *

"""
This example simulates the kinetics of precipitation of CEMENTITE from a BCC_A2 solution phase and shows the grain growth results
for two cases: with and without Zener pining. A Hillert distribution is applied for the matrix grain size.
"""


def hillert_distribution(r):
    p = 2 ** 3
    p = p * math.exp(2.0)
    p = p * r
    p = p / ((2.0 - r) ** 4)
    pu = p * math.exp(-(4.0 / (2.0 - r)))
    return pu


def generate_hillert_distribution(mean_size):
    number_grid_points_per_magnitude = 200.0
    minimum_size = 1e-9
    max_size = 1.7 * mean_size
    r = minimum_size
    geo_factor = 10 ** (1 / number_grid_points_per_magnitude)
    i = 0
    grain_raidus = []
    gsd = []
    r_left = minimum_size
    while r < max_size:
        r_right = r_left * geo_factor
        r = 0.5 * (r_left + r_right)
        grain_raidus.append(r)
        gsd.append(hillert_distribution(r / mean_size))
        r_left = r_right

    return grain_raidus, gsd


sim_time = 126000

exp_one_x = [0.167, 0.583, 2.5, 4.5, 7.0, 11.0, 21.0, 35.0]
exp_one_y = [3.3, 3.6, 4.4, 4.8, 5.7, 5.4, 6.7, 7.1]


def simulate(system_input, has_pinner):
    grain_size_distribution = GrainSizeDistribution()

    grain_radius_hillert, pdf_hillert_normalized = generate_hillert_distribution(3.2e-6)
    for idx, val in enumerate(grain_radius_hillert):
        grain_size_distribution.add_radius_and_number_density(val, pdf_hillert_normalized[idx])

    grain_growth = GrainGrowth(grain_size_distribution)
    if has_pinner:
        grain_growth.enable_zener_pinning()
    else:
        grain_growth.disable_zener_pinning()

    grain_growth.set_grain_boundary_energy(0.5)
    grain_growth.set_grain_boundary_mobility_pre_factor(2.0e-15)
    grain_growth.set_grain_boundary_mobility_activation_energy(0.0)

    matrix_phase = (MatrixPhase("BCC_A2")
                    .with_grain_growth_model(grain_growth)
                    .set_mobility_adjustment("all", 0.08, 0.0)
                    .add_precipitate_phase(PrecipitatePhase("CEMENTITE")
                                           .set_nucleation_in_bulk()
                                           .set_zener_pinning_parameters(8e-7, 0.5, 0.93))
                    )
    calculation = (system_input.with_matrix_phase(matrix_phase))

    sim_results = calculation.calculate()
    return sim_results


def plot_results(no_pinning_res, with_pinning_res):
    fig, (ax1) = plt.subplots(1, 1)
    time_without_pining, mean_grain_size_without_pining = no_pinning_res.get_grain_mean_radius()
    time_with_pining, mean_grain_size_with_pining = with_pinning_res.get_grain_mean_radius()
    ax1.plot(np.array(time_without_pining) / 3600, 1e6 * np.array(mean_grain_size_without_pining),
             label='Mean radius of BCC_A2 (No pinning)')
    ax1.plot(np.array(time_with_pining) / 3600, 1e6 * np.array(mean_grain_size_with_pining),
             label='Mean radius of BCC_A2 (With pinning)')
    exp_one_x_simulated = []
    exp_one_y_simulated = []
    for idx, val in enumerate(exp_one_x):
        if val <= sim_time / 3600:
            exp_one_x_simulated.append(exp_one_x[idx])
            exp_one_y_simulated.append(exp_one_y[idx])
    if len(exp_one_x_simulated) > 0:
        ax1.plot(exp_one_x_simulated, exp_one_y_simulated, "^", label="Experiment")
    fig.suptitle('With/without Zener pinning', fontsize=16)
    ax1.set_xlabel('Time [h]')
    ax1.set_ylabel('Length [μm]')
    ax1.legend(loc='best')

    plt.show()


with TCPython() as start:
    start.set_cache_folder(os.path.basename(__file__) + "_cache")
    elements = ["Fe", "C"]
    system = (start.select_thermodynamic_and_kinetic_databases_with_elements("FEDEMO", "MFEDEMO", elements).get_system()
              .with_isothermal_precipitation_calculation()
              .set_composition_unit(CompositionUnit.MASS_PERCENT)
              .set_composition("C", 0.2)
              .set_temperature(995.15)
              .set_simulation_time(sim_time))

    with_pinning_results = simulate(system, True)
    no_pinning_results = simulate(system, False)

    plot_results(no_pinning_results, with_pinning_results)
