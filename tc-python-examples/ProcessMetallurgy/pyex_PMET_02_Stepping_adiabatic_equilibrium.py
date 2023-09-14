from tc_python import *
import matplotlib.pyplot as plt

"""
This example shows how to create adiabatic equilibrium calculations for
varied pressure. The equilibrium between a steel and slag melt
and oxygen is calculated.            
"""

temp_in_c = 1700
min_pressure_in_bar = 1.0
max_pressure_in_bar = 2.0
pressure_step_in_bar = 0.1

with TCPython() as session:
    session.set_cache_folder(os.path.basename(__file__) + '_cache')

    calc = session.with_metallurgy().with_adiabatic_equilibrium_calculation(ProcessDatabase.OXDEMO)

    steel = EquilibriumAddition({'Fe': None, 'C': 4}, amount=100.0e3, temperature=temp_in_c + 273.15)
    slag = EquilibriumAddition({'CaO': 70, 'SiO2': 30}, amount=3.0e3, temperature=temp_in_c + 273.15)
    gas = EquilibriumGasAddition({'O2': 100}, amount=1000)

    (calc
     .add_addition(steel)
     .add_addition(slag)
     .add_addition(gas))

    pressure_range_in_bar = []
    c_in_steel = []
    slag_property = []

    pressure_in_bar = min_pressure_in_bar
    num_steps = 1 + int((max_pressure_in_bar - min_pressure_in_bar) / pressure_step_in_bar)
    for index in range(num_steps):
        pressure_in_bar = min_pressure_in_bar + index * pressure_step_in_bar
        calc.set_pressure(pressure_in_bar * 1e5)
        result = calc.calculate()

        c_in_steel.append(result.get_composition_of_phase_group(PhaseGroup.ALL_METAL)['C'])
        slag_property.append(result.get_slag_property(SlagProperty.B2, SlagType.ALL))
        pressure_range_in_bar.append(pressure_in_bar)
        print(f"{pressure_in_bar:.1f} bar, stable phases: {result.get_stable_phases()}")

    plt.figure()
    plt.plot(pressure_range_in_bar, c_in_steel)
    plt.title("100 t Fe-4 wt-% C / 3 t 70 wt-% CaO-30 wt-% SiO2 / 1000 Nm**3 O2")
    plt.xlabel('pressure / bar')
    plt.ylabel('C-content in steel / wt-%')

    plt.figure()
    plt.plot(pressure_range_in_bar, slag_property)
    plt.title("Slag property B2 (CaO / SiO2)")
    plt.xlabel('pressure / bar')
    plt.ylabel('slag property')
    plt.show()
