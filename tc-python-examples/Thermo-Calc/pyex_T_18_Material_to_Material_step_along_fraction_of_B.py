from matplotlib import pyplot as plt
from tc_python import *

"""
Calculates the phases occurring during a gradual transition between two materials, in this case from a martensitic
stainless steel to Alloy 800.
This type of calculation is for example useful for understanding effects when welding dissimilar materials - without
the need to perform diffusion calculations.
"""


def add_data_to_axes(ax, plot_data, xlabel, ylabel):
    for group in plot_data.values():
        ax.plot(group.x, group.y, label=group.label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(loc='best')


with TCPython() as session:
    session.set_cache_folder(os.path.basename(__file__) + "_cache")
    system = session.select_database_and_elements("FEDEMO", ["Fe", "Cr", "Ni"]).get_system()

    calc = system.with_material_to_material().with_property_diagram_calculation()

    (calc
     .set_material_a({"Cr": 17.0, "Ni": 2.0}, dependent_component="Fe")
     .set_material_b({"Cr": 19.0, "Ni": 35.0}, dependent_component="Fe")
     .set_composition_unit(CompositionUnit.MASS_PERCENT)
     .with_axis(MaterialToMaterialCalculationAxis.fraction_of_material_b(from_fraction=0.0,
                                                                         to_fraction=1.0,
                                                                         start_fraction=0.5))
     .with_constant_condition(ConstantCondition.temperature(650 + 273.15)))
    result = calc.calculate()

    plot_data_step = result.get_values_grouped_by_quantity_of(
        MATERIAL_B_FRACTION,
        ThermodynamicQuantity.volume_fraction_of_a_phase(ALL_PHASES)
    )

    plot_data_compositions = result.get_values_grouped_by_quantity_of(
        MATERIAL_B_FRACTION,
        ThermodynamicQuantity.mass_fraction_of_a_component(ALL_COMPONENTS)
    )

    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1.set_title("Martensitic stainless steel - Alloy 800")
    add_data_to_axes(ax1, plot_data_step, "Fraction of Alloy 800", "Volume fraction of phases [-]")
    add_data_to_axes(ax2, plot_data_compositions, "Fraction of Alloy 800", "Mass-fraction components [-]")
    fig.set_size_inches(7, 10)
    plt.show()
