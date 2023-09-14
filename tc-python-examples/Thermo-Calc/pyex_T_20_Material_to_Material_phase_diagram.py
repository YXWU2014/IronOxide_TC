import numpy as np
from matplotlib import pyplot as plt
from tc_python import *

"""
Calculates a "phase diagram" for a material mixture, in this case for a mixture of a martensitic stainless steel with
Alloy 800.
This type of calculation is for example useful for understanding effects when welding dissimilar materials - without
the need to perform diffusion calculations.
"""


def add_phase_diagram_data_to_axes(ax, plot_data, xlabel, ylabel):
    """Plot the phase diagram with degree Celsius on the y-axis"""
    for group in plot_data.get_lines().values():
        ax.plot(group.x, np.array(group.y) - 273.15, label=group.label)

    ax.plot(plot_data.get_tie_lines().x, np.array(plot_data.get_tie_lines().y) - 273.15, "g", linewidth=0.5)

    ax.plot(plot_data.get_invariants().x, np.array(plot_data.get_invariants().y) - 273.15, "r")

    for phase_label in plot_data.get_phase_labels():
        ax.text(1.01 * phase_label.x, 1.01 * (phase_label.y - 273.15), phase_label.text)
        ax.scatter(phase_label.x, phase_label.y - 273.15, s=3, color="k", marker="o")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim([0, 1])
    ax.legend(loc='best')


def add_composition_plot_data_to_axes(ax, plot_data, xlabel, ylabel):
    """Plot the composition percentages vs. fraction of material B data"""
    for group in plot_data.get_lines().values():
        ax.plot(group.x, 100 * np.array(group.y), label=group.label)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim([0, 1])
    ax.legend(loc='best')


with TCPython() as session:
    session.set_cache_folder(os.path.basename(__file__) + "_cache")
    system = session.select_database_and_elements("FEDEMO", ["Fe", "Cr", "Ni"]).get_system()

    calc = system.with_material_to_material().with_phase_diagram_calculation()

    (calc
     .set_material_a({"Cr": 17.0, "Ni": 2.0}, dependent_component="Fe")
     .set_material_b({"Cr": 19.0, "Ni": 35.0}, dependent_component="Fe")
     .set_composition_unit(CompositionUnit.MASS_PERCENT)
     .with_first_axis(MaterialToMaterialCalculationAxis.fraction_of_material_b())
     .with_second_axis(MaterialToMaterialCalculationAxis.temperature(from_temperature=300 + 273.15,
                                                                     to_temperature=800 + 273.15,
                                                                     start_temperature=600 + 273.15)))
    result = calc.calculate()

    (result
     .add_coordinate_for_phase_label(0.5, 780 + 273.15)
     .add_coordinate_for_phase_label(0.58, 600 + 273.15)
     .add_coordinate_for_phase_label(0.2, 530 + 273.15)
     .add_coordinate_for_phase_label(0.37, 410 + 273.15)
     .add_coordinate_for_phase_label(0.335, 310 + 273.15)
     .add_coordinate_for_phase_label(0.05, 740 + 273.15)
     .add_coordinate_for_phase_label(0.01, 360 + 273.15)
     .add_coordinate_for_phase_label(0.01, 560 + 273.15)
     .add_coordinate_for_phase_label(0.87, 440 + 273.15)
     .add_coordinate_for_phase_label(0.03, 490 + 273.15))

    plot_data_phase_diagram = (result.get_values_grouped_by_stable_phases_of(
        MATERIAL_B_FRACTION,
        ThermodynamicQuantity.temperature())
    )

    result.remove_phase_labels()

    plot_data_compositions = result.get_values_grouped_by_quantity_of(
        MATERIAL_B_FRACTION,
        ThermodynamicQuantity.mass_fraction_of_a_component(ALL_COMPONENTS))

    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1.set_title("Martensitic stainless steel - Alloy 800")
    add_phase_diagram_data_to_axes(ax1, plot_data_phase_diagram,
                                   "Fraction of Alloy 800", "Temperature [\N{DEGREE SIGN}C]")
    add_composition_plot_data_to_axes(ax2, plot_data_compositions,
                                      "Fraction of Alloy 800", "Composition [wt-%]")
    fig.set_size_inches(7, 10)
    plt.show()
