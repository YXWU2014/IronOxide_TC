import csv
from tc_python import *

"""
Exports the line data of a phase diagram into a CSV-file that can be imported into other plotting software for creating
customized plots for example. It is easy to adapt the code to generate a different format of the CSV-file or to
use a completely different output file format.
The system Fe-C-Cr is used as an example.
"""


database = "FEDEMO"
dependent_element = "Fe"
composition = {"C": 0.03, "Cr": 10.0}  # in wt-%
temp_ref = 1000  # temperature for the initial equilibrium, in K
varied_element = "Cr"
varied_element_range = {"min": 0, "max": 1.0}  # in weight fraction
varied_temp_range = {"min": 500, "max": 3000}  # in K
csv_file_path = "Fe_C_Cr_phase_diagram.csv"

elements = list(composition.keys())

with TCPython() as session:
    session.set_cache_folder(os.path.basename(__file__) + "_cache")
    system = session.select_database_and_elements(database, [dependent_element] + elements).get_system()

    calculator = system.with_phase_diagram_calculation()
    calculator.set_condition(ThermodynamicQuantity.temperature(), temp_ref)

    for element in composition:
        calculator.set_condition(ThermodynamicQuantity.mass_fraction_of_a_component(element),
                                 composition[element] / 100)

    result = (calculator.
              with_first_axis(CalculationAxis(ThermodynamicQuantity.mass_fraction_of_a_component(varied_element)).
                              set_min(varied_element_range["min"]).
                              set_max(varied_element_range["max"])).
              with_second_axis(CalculationAxis(ThermodynamicQuantity.temperature()).
                               set_min(varied_temp_range["min"]).
                               set_max(varied_temp_range["max"])).
              calculate())

    phase_diagram = result. \
        get_values_grouped_by_quantity_of(ThermodynamicQuantity.mass_fraction_of_a_component(varied_element),
                                          ThermodynamicQuantity.temperature())

    phase_boundaries = phase_diagram.get_lines()
    invariants = phase_diagram.get_invariants()

    # the CSV-file will contain all data within two columns:
    #   * between each separate line (a phase boundary or invariant section) there is a row containing NaN-values
    #   * no details about the phase regions are stored
    #   * it is assumed that this format is suitable for the importing program
    with open(csv_file_path, "w", newline="") as file:
        csv_file_writer = csv.writer(file)
        csv_file_writer.writerow(["{} [wt-%]".format(varied_element), "Temperature [K]"])

        data = phase_boundaries[varied_element.upper()]  # the only label is the varied element due to group by quantity
        for x, y in zip(data.x, data.y):
            csv_file_writer.writerow([x, y])

        csv_file_writer.writerow([float("NaN"), float("NaN")])
        for x, y in zip(invariants.x, invariants.y):
            csv_file_writer.writerow([x, y])
