import matplotlib.pyplot as plt
from tc_python import *

"""
This example shows how to create a property (step) diagram using TC-Python.
The alloy system Fe-Ni is used as an example. 
"""


with TCPython() as start:
    start.set_cache_folder(os.path.basename(__file__) + "_cache")
    start.set_ges_version(6)
    calculation = (
        start.select_database_and_elements("FEDEMO", ["Fe", "Ni"]).get_system().
            with_property_diagram_calculation().
            with_axis(CalculationAxis(ThermodynamicQuantity.temperature()).
                      set_min(500).
                      set_max(3000).
                      with_axis_type(Linear().set_min_nr_of_steps(50))).
            set_condition(ThermodynamicQuantity.temperature(), 1000).
            set_condition("W(Ni)", 0.1)
    )

    property_diagram = calculation.calculate()
    property_diagram.set_phase_name_style(PhaseNameStyle.ALL)
    groups = \
        property_diagram.get_values_grouped_by_quantity_of(ThermodynamicQuantity.temperature(),
                                                           ThermodynamicQuantity.volume_fraction_of_a_phase(ALL_PHASES))

for group in groups.values():
    plt.plot(group.x, group.y, label=group.label)

plt.xlabel("Temperature [K]")
plt.ylabel("Volume fraction of phases [-]")
plt.legend(loc="center right")
plt.title("Fe-10Ni")
plt.show()
