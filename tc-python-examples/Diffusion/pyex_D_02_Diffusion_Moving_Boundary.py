from tc_python import *
import matplotlib.pyplot as plt

"""
Diffusion with a Moving Boundary between a Ferrite and Austenite Region

This example simulates diffusion including a moving boundary between a ferrite and austenite 
region in an Fe-C steel. Initially the C-concentration is constant in each region, with a step
at the boundary. All units are in wt-%.

The example uses a minimum number of required settings. Default values are used for any 
unspecified settings.
"""


with TCPython() as session:
    system = (session
                .set_cache_folder(os.path.basename(__file__) + "_cache")
                .select_thermodynamic_and_kinetic_databases_with_elements("FEDEMO", "MFEDEMO", ["Fe", "C"])
                .without_default_phases()
                .select_phase("FCC_A1")
                .select_phase("BCC_A2")
                .get_system())

    calculator = (system
                    .with_isothermal_diffusion_calculation()
                    .set_temperature(1050.0)
                    .set_simulation_time(30*3600)

                    .add_region(Region("Ferrite")
                        .set_width(1.0E-9)
                        .with_grid(CalculatedGrid.linear()
                            .set_no_of_points(10))
                        .with_composition_profile(CompositionProfile()
                            .add("C", ElementProfile.constant(0.01)))
                        .add_phase("BCC_A2"))

                    .add_region(Region("Austenite")
                        .set_width(0.002)
                        .with_grid(CalculatedGrid.geometric()
                            .set_no_of_points(50)
                            .set_geometrical_factor(1.05))
                        .with_composition_profile(CompositionProfile()
                            .add("C", ElementProfile.constant(0.15)))
                        .add_phase("FCC_A1")))

    result = calculator.calculate()

    time, position_of_interface = result.get_position_of_upper_boundary_of_region("Ferrite")


fig, ax = plt.subplots()
fig.suptitle('Width of the Ferrite region', fontsize=14, fontweight='bold')
ax.set_xlabel('Time [s]')
ax.set_ylabel('Length of Ferrite [m]')
plt.plot(time, position_of_interface)
plt.show()
