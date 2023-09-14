import csv
import numpy as np
from scipy.interpolate import interp1d
from tc_python import *

"""
Calculates the characteristic properties of the solidification of a range of alloys using Scheil-solidification and
saves the data into a CSV-file that can be imported by other software.
Such data is typically used as an input into other simulation software, e.g. for casting simulation.
The alloy system Al-Si-Cu is used as an example.
"""


database = "ALDEMO"
dependent_element = "Al"
composition = {"Si": 9.0, "Cu": 3.0}  # in wt-%
varied_element = "Cu"
variation = {"min": 1.0, "max": 5.0, "num_steps": 10}  # in wt-%
liquid_frac_solidification_start = 0.01  # assumed start of solidification
liquid_frac_solidification_end = 0.99  # assumed end of solidification
liquid_frac_phase_change = 0.5  # 50% of liquid is transformed to solid (at the "phase change temperature")
csv_file_path = "Al_Si_Cu_scheil_solidification.csv"

elements = list(composition.keys())

with TCPython() as session:
    session.set_cache_folder(os.path.basename(__file__) + "_cache")
    system = (session.
              select_database_and_elements(database, [dependent_element] + elements).
              get_system())

    calculator = (system.
                  with_scheil_calculation().
                  set_composition_unit(CompositionUnit.MASS_PERCENT))

    calculator.enable_global_minimization()

    for element in composition:
        calculator.set_composition(element, composition[element])

    # vary the composition
    varied_composition = np.linspace(variation["min"], variation["max"], variation["num_steps"])

    # open the CSV-file and keep it open
    with open(csv_file_path, "w", newline="") as file:
        csv_file_writer = csv.writer(file)
        csv_file_writer.writerow(["{} [wt-%]".format(varied_element),
                                  "Phase change temperature [K]",
                                  "Transition interval [K]",
                                  "Latent heat [kJ/kg]"])

        for varied_element_content in varied_composition:
            calculator.set_composition(varied_element, varied_element_content)

            result = calculator.calculate()
            t_latent_heat, latent_heat = result.get_values_of(ScheilQuantity.temperature(),
                                                              ScheilQuantity.latent_heat_per_gram())
            t, liquid_frac = result.get_values_of(ScheilQuantity.temperature(),
                                                  ScheilQuantity.mole_fraction_of_all_liquid())

            # determine the characteristic properties of the solidification
            total_latent_heat = np.max(np.abs(latent_heat))

            liquid_frac_curve = interp1d(liquid_frac, t)
            phase_change_t = liquid_frac_curve(liquid_frac_phase_change)

            start_t = liquid_frac_curve(liquid_frac_solidification_start)
            end_t = liquid_frac_curve(liquid_frac_solidification_end)
            transition_interval = end_t - start_t

            # save the results to file, the data can later be imported into other simulation software
            csv_file_writer.writerow([varied_element_content, phase_change_t, transition_interval, total_latent_heat])

            print("{}-content: {} wt-%".format(varied_element, varied_element_content))
            print("---------------------")
            print("Phase change temperature: {} K".format(phase_change_t))
            print("Transition interval: {} K".format(transition_interval))
            print("Latent heat: {} kJ/kg\n".format(total_latent_heat))
