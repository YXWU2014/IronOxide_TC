import matplotlib.pyplot as plt
from tc_python import *

"""
This example shows how to calculate and plot a phase diagram.
The system Fe-Cr is used as an example.
"""


with TCPython() as start:
    start.set_cache_folder(os.path.basename(__file__) + "_cache")
    calculation = (start.select_database_and_elements("FEDEMO", ["Fe", "Cr"]).
                   get_system().
                   with_phase_diagram_calculation().

                   with_first_axis(CalculationAxis(ThermodynamicQuantity.mole_fraction_of_a_component("Cr")).
                                   set_min(0).
                                   set_max(1.0).
                                   with_axis_type(Linear().set_max_step_size(.025))).
                   with_second_axis(CalculationAxis(ThermodynamicQuantity.temperature()).
                                     set_min(500).
                                     set_max(3000.0).
                                     with_axis_type(AxisType.linear().set_min_nr_of_steps(60))).
                   enable_global_minimization().

                   set_condition(ThermodynamicQuantity.temperature(), 1000).
                   set_condition(ThermodynamicQuantity.mole_fraction_of_a_component("Cr"), 10 / 100))

    simulation_results = (calculation.
                          calculate().
                          add_coordinate_for_phase_label(0.5, 2000).
                          get_values_grouped_by_stable_phases_of(ThermodynamicQuantity.
                                                                 mole_fraction_of_a_component("Cr"),
                                                                 ThermodynamicQuantity.temperature()))

fig, ax = plt.subplots(1)
for group in simulation_results.get_lines().values():
    plt.plot(group.x, group.y, label=group.label)

plt.plot(simulation_results.get_tie_lines().x, simulation_results.get_tie_lines().y, "g", linewidth=0.5)

plt.plot(simulation_results.get_invariants().x, simulation_results.get_invariants().y, "r")

for phase_label in simulation_results.get_phase_labels():
    ax.text(1.01 * phase_label.x, 1.01 * phase_label.y, phase_label.text)
    ax.scatter(phase_label.x, phase_label.y, s=3, color="k", marker="o")

ax.set_xlabel("Mole fraction Cr [-]")
ax.set_ylabel("Temperature [K]")
ax.set_title("Phase diagram Fe-Cr")
ax.set_xlim([0, 1.0])
ax.set_ylim([500, 2250])
plt.legend(loc="center right")
plt.show()
