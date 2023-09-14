import concurrent.futures
from matplotlib import pyplot as plt
from tc_python import *

"""
This example shows how to run multiple property (step) diagram calculations in parallel. TC-Python supports
parallel computation only by using multi-processing.
The alloy system Fe-C-Cr is used as an example.
"""


def do_step(param):
    elements = ["Fe", "C", "Cr"]

    with TCPython() as start:
        start.set_cache_folder(os.path.basename(__file__) + "_cache")
        calculation = (start.select_database_and_elements("FEDEMO", elements).
                       get_system().
                       with_property_diagram_calculation().
                       with_axis(CalculationAxis(ThermodynamicQuantity.temperature()).
                                 set_min(500.0).
                                 set_max(3000.0).
                                 with_axis_type(Linear().set_min_nr_of_steps(10))).
                       set_condition(ThermodynamicQuantity.temperature(), 1000.0).
                       set_condition(ThermodynamicQuantity.mole_fraction_of_a_component("C"), 0.1 / 100).
                       set_condition(ThermodynamicQuantity.mole_fraction_of_a_component("Cr"), param["cr"] / 100.0))
        r = (calculation.
             calculate().
             get_values_grouped_by_quantity_of(ThermodynamicQuantity.temperature(),
                                               ThermodynamicQuantity.mole_fraction_of_a_phase(ALL_PHASES)))
    return r


if __name__ == "__main__":
    parameters = [
        {"index": 0, "cr": 0},
        {"index": 1, "cr": 2},
        {"index": 2, "cr": 4},
        {"index": 3, "cr": 6},
        {"index": 4, "cr": 8},
        {"index": 5, "cr": 10},
        {"index": 6, "cr": 12},
        {"index": 7, "cr": 14},
        {"index": 8, "cr": 16}
    ]

    results = []
    processes = 8

    with concurrent.futures.ProcessPoolExecutor(processes) as executor:
        for property_diagram in zip(parameters, executor.map(do_step, parameters)):
            params, calc_results = property_diagram
            results.append([params["index"], calc_results])

    number_of_subplots = len(parameters)
    number_of_columns = 3
    number_of_rows = number_of_subplots // number_of_columns
    number_of_rows += number_of_subplots % number_of_columns

    fig, axs = plt.subplots(number_of_rows, number_of_columns)
    axs = axs.flat

    fig.suptitle("Phase fractions in Fe-0.1C-xCr", fontsize=14, fontweight="bold")
    for index, groups in results:
        axs[index].set_title("{} mol-% Cr, ".format(parameters[index]["cr"]))
        axs[index].set_xlabel("Temperature [K]")

        for group in groups.values():
            axs[index].plot(group.x, group.y, label=group.label)

        axs[index].legend()

    plt.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)
    plt.show()
