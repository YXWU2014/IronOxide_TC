from tc_python import *
import matplotlib.pyplot as plt
import concurrent.futures

"""
This example shows how to set up multiple precipitation calculations with different parameter settings
and send them to four processors for concurrent execution.
"""


def calc_precipitation(parameters):
    """
    Run a precipitation simulation for a Al3Sc precipitate from a FCC_A1 matrix.
    Simulation time is fixed to 1e9 seconds and interfacial energy is calculated.
    Alloy composition, isothermal holding temperature and interfacial energy prefactor
    is given as input parameters.

    Args:
        parameters: a dictionary with values:
            Sc: Scandium content in mole-percent
            temperature: Isothermal holding temperature in Kelvin
            interfacial_energy_prefactor: Prefactor for the calculated interfacial energy

    Returns:
        time: list of times, unit seconds
        mean_radius: list of average radius of the Al3Sc precipiates, unit meters.
    """

    with TCPython():

        elements = ["Al", "Sc"]
        sim_results = (SetUp()
                       .set_cache_folder(os.path.basename(__file__) + "_cache")
                       .select_thermodynamic_and_kinetic_databases_with_elements("ALDEMO", "MALDEMO", elements)
                       .get_system()
                       .with_isothermal_precipitation_calculation()
                       .set_composition_unit(CompositionUnit.MOLE_PERCENT)
                       .set_composition("Sc", parameters['Sc'])
                       .set_temperature(parameters['temperature'])
                       .set_simulation_time(1e9)
                       .with_matrix_phase(MatrixPhase("FCC_A1")
                                          .add_precipitate_phase(PrecipitatePhase("AL3SC")
                                                                 .set_interfacial_energy_estimation_prefactor(parameters['interfacial_energy_prefactor'])
                                                                 )
                                          )
                       .calculate()
                       )

        time, mean_radius = sim_results.get_mean_radius_of("AL3SC")
    return time, mean_radius


if __name__ == "__main__":

    list_of_parameters = [{'index': 0, 'temperature': 623.0, 'interfacial_energy_prefactor': 1.0, 'Sc': 0.18},
                          {'index': 1, 'temperature': 623.0, 'interfacial_energy_prefactor': 0.9, 'Sc': 0.18},
                          {'index': 2, 'temperature': 623.0, 'interfacial_energy_prefactor': 1.1, 'Sc': 0.18},
                          {'index': 3, 'temperature': 623.0, 'interfacial_energy_prefactor': 1.0, 'Sc': 0.18},
                          {'index': 4, 'temperature': 623.0, 'interfacial_energy_prefactor': 1.0, 'Sc': 0.19},
                          {'index': 5, 'temperature': 600.0, 'interfacial_energy_prefactor': 0.9, 'Sc': 0.18},
                          {'index': 6, 'temperature': 630.0, 'interfacial_energy_prefactor': 1.1, 'Sc': 0.18},
                          {'index': 7, 'temperature': 640.0, 'interfacial_energy_prefactor': 1.0, 'Sc': 0.18}
                          ]

    list_of_results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        for result in zip(list_of_parameters, executor.map(calc_precipitation, list_of_parameters)):
            parameters, [time, mean_radius] = result
            list_of_results.append({'parameters': parameters, 'time': time, 'mean_radius': mean_radius})

    # Plot the results from all simulations
    fig, ax = plt.subplots()
    fig.suptitle('Precipitation of Al3Sc', fontsize=14, fontweight='bold')
    for result in list_of_results:
        parameters = result['parameters']
        legend = ('T=' + str(parameters['temperature']) + ', '
                   + 'sigma=' + str(parameters['interfacial_energy_prefactor']) + ', '
                   + 'Sc=' + str(parameters['Sc'])
                 )
        ax.loglog(result['time'], result['mean_radius'], label=legend)
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Radius [m]')
    legend = ax.legend(loc='upper left', shadow=True)
    plt.show()
