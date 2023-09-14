import matplotlib.pyplot as plt
from tc_python import *

"""
This example shows how to perform step calculations for a multi-material system. Such a calculation is not
possible using the Thermo-Calc Graphical User Interface.
"""


def add_data_to_axes(ax, plot_data, xlabel, ylabel):
    for group in plot_data.values():
        ax.plot(group.x, group.y, label=group.label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(loc="best")


if __name__ == "__main__":
    dependent_element = "Fe"
    elements_input = ["Cr", "Ni", "C", "Mn"]
    alloy_A_input = {"Cr": 0.1, "Ni": 0.02, "C": 0.023, "Mn": 0.11}
    alloy_B_input = {"Cr": 0.3, "Ni": 0.43, "C": 0.01, "Mn": 0.22}

    conditions = {"T": 1000.0}

    # Create new variables for elements, alloy A and B that skip elements that do no change in composition
    # between alloy A and B. Add the remaining elements as conditions directly.
    alloy_A = {}
    alloy_B = {}
    elements = []
    for element in elements_input:
        if alloy_A_input[element] == alloy_B_input[element]:
            condition = "w(" + element + ")"
            conditions[condition] = alloy_A_input[element]
        else:
            alloy_A[element] = alloy_A_input[element]
            alloy_B[element] = alloy_B_input[element]
            elements.append(element)

    # Always take the last element to be the one that we vary in step calculation
    axis_element = elements[-1]

    # the step/map variable always need to increase, swap the alloys if that is not the case.
    if alloy_A[axis_element] > alloy_B[axis_element]:
        temp = alloy_A
        alloy_A = alloy_B
        alloy_B = temp

    # Create the conditions for all dependent elements so they all linearly depend on the axis_element condition.
    # The conditions should be linear functions that go through alloy A and B. The intersection of the line
    # is evaluated at alloy A.
    # The axis_element is set to Alloy A composition.
    for index, element in enumerate(elements):
        if element == axis_element:
            condition = "w(" + element + ")"
            conditions[condition] = alloy_A_input[element]
        else:
            element_1 = element
            element_2 = elements[index + 1]
            slope = (alloy_B[element_1] - alloy_A[element_1]) / (alloy_B[element_2] - alloy_A[element_2])
            m = alloy_A[element_1] - slope * alloy_A[element_2]
            condition = "w(" + element_1 + ")" + "{:+f}".format(-slope) + "*w(" + element_2 + ")"
            conditions[condition] = m

    with TCPython() as start:
        start.set_cache_folder(os.path.basename(__file__) + "_cache")
        elements = [dependent_element] + elements_input
        database = "FEDEMO"

        axis_condition = "w(" + axis_element + ")"
        calculation = (start.select_database_and_elements(database, elements).get_system().
                       with_property_diagram_calculation().with_axis(CalculationAxis(axis_condition)
                                                                     .set_min(alloy_A[axis_element])
                                                                     .set_max(alloy_B[axis_element])
                                                                     .set_start_at(alloy_A[axis_element])))

        for condition, value in conditions.items():
            print(condition + '=' + "{0:.{1}f}".format(value, 4))
            calculation.set_condition(condition, value)

        calculated_results = calculation.calculate()
        plot_data_step = calculated_results.get_values_grouped_by_quantity_of("w(" + axis_element + ")", "VPV(*)")

        calculation_map = (SetUp().select_database_and_elements("FEDEMO", elements).
            get_system().
            with_phase_diagram_calculation().with_first_axis(
            CalculationAxis(axis_condition)
                .set_min(alloy_A[axis_element])
                .set_max(alloy_B[axis_element])
                .set_start_at(alloy_A[axis_element]))
            .with_second_axis(
            CalculationAxis("T")
                .set_min(500)
                .set_max(3000.0)))

        for condition, value in conditions.items():
            print(condition + '=' + "{0:.{1}f}".format(value, 4))
            calculation_map.set_condition(condition, value)

        calculated_results_map = calculation_map.calculate()
        plot_data_phase_diagram = calculated_results_map.get_values_grouped_by_stable_phases_of(
            ThermodynamicQuantity.mass_fraction_of_a_component(axis_element),
            ThermodynamicQuantity.temperature())
        plot_data_compositions = calculated_results.get_values_grouped_by_quantity_of(
            ThermodynamicQuantity.mass_fraction_of_a_component(axis_element),
            ThermodynamicQuantity.mass_fraction_of_a_component(ALL_PHASES))

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
        ax1.set_title("Fe-Cr-Ni-C-Mn")
        ax1.text(0.107, 0.02, "1000 K")
        add_data_to_axes(ax1, plot_data_step, axis_condition, "Volume fraction phases [-]")
        add_data_to_axes(ax2, plot_data_phase_diagram.get_lines(), axis_condition, "T [K]")
        add_data_to_axes(ax3, plot_data_compositions, axis_condition, "Weight-fraction elements [-]")
        fig.set_size_inches(7, 10)
        plt.show()
