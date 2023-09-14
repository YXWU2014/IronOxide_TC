from matplotlib import pyplot as plt

from tc_python import *

"""
Calculates and plots the single phase FCC_A1 region of Al-Si-Cu alloys and compares them for different Cu-contents.
For simplicity only FCC_A1 and DIAMOND_A4 are enabled as solid phases.
"""


database = "ALDEMO"
dependent_element = "Al"
composition = {"Si": 9.0, "Cu": 3.0}  # in wt-%
x_axis_element = "Si"
x_axis_range = {"min": 0, "max": 2.5}  # wt-%
temp_axis_range = {"min": 300, "max": 1000}  # in K
varied_element = "Cu"
variations = [1.0, 2.0, 3.0]  # in wt-%
plot_colors = ['red', 'green', 'blue']
temp_ref = 1000  # temperature for the initial equilibrium, in K

# needs to be determined in advanced by checking the labels in the result data
relevant_labels = ["DIAMOND_A4",
                   "LIQUID"]

elements = list(composition.keys())

with TCPython() as session:
    session.set_cache_folder(os.path.basename(__file__) + "_cache")
    system = (session.
              select_database_and_elements(database, [dependent_element] + elements).
              without_default_phases().
              select_phase("FCC_A1").
              select_phase("DIAMOND_A4").
              select_phase("LIQUID").
              get_system())

    calculator = system.with_phase_diagram_calculation()

    calculator.set_condition(ThermodynamicQuantity.temperature(), temp_ref)

    for element in composition:
        calculator.set_condition(ThermodynamicQuantity.mass_fraction_of_a_component(element),
                                 composition[element] / 100)

    for variation_index, varied_element_content in enumerate(variations):
        calculator.set_condition(ThermodynamicQuantity.mass_fraction_of_a_component(varied_element),
                                 varied_element_content / 100)

        phase_diagram = (calculator.
                         with_first_axis(CalculationAxis(ThermodynamicQuantity.
                                                         mass_fraction_of_a_component(x_axis_element)).
                                         set_min(x_axis_range["min"] / 100).
                                         set_max(x_axis_range["max"] / 100)).
                         with_second_axis(CalculationAxis(ThermodynamicQuantity.temperature()).
                                          set_min(temp_axis_range["min"]).
                                          set_max(temp_axis_range["max"])).
                         calculate())

        # add labels for better readability
        phase_diagram.add_coordinate_for_phase_label(0.3, 790.0)  # in the single FCC_A1 region for all variations
        phase_diagram.add_coordinate_for_phase_label(1.2, 755)  # in the DIAMOND_A4 + FCC_A1 region for all variations
        phase_diagram.add_coordinate_for_phase_label(0.5, 900.0)  # in the FCC_A1 + LIQUID region for all variations

        result_data = phase_diagram.get_values_grouped_by_stable_phases_of("M-P {}".format(x_axis_element),
                                                                           ThermodynamicQuantity.temperature())

        for line_index, label in enumerate(relevant_labels):
            line = result_data.get_lines()[label]
            if line_index != 0:
                plt.plot(line.x, line.y, color=plot_colors[variation_index])
            else:
                plt.plot(line.x, line.y,
                         color=plot_colors[variation_index],
                         label="{}={} wt-%".format(varied_element, varied_element_content))

        phase_region_labels = result_data.get_phase_labels()
        for label in phase_region_labels:
            plt.text(label.x, label.y, label.text)

    # configure the plot
    plt.xlabel("{} [wt-%]".format(x_axis_element))
    plt.xlim([x_axis_range["min"], x_axis_range["max"]])
    plt.ylabel("T [K]")
    plt.ylim([temp_axis_range["min"], temp_axis_range["max"]])
    plt.title("Al-Si9-Cu3 system")
    plt.legend()
    plt.show()
