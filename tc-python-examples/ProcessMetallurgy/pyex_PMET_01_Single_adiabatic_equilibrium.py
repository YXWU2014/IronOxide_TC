from tc_python import *

"""
This example shows how to create an adiabatic equilibrium calculation for a
process metallurgical problem. The equilibrium between a steel and slag melt
and oxygen is calculated.            
"""

database = ProcessDatabase.OXDEMO
metal_composition = {"Fe": None, "C": 4.5, "Si": 1.0}  # in mass percent
total_metal_mass_in_t = 100
slag_composition = {"CaO": 75, "Al2O3": 25}  # in mass percent
total_slag_mass_in_t = 3
gas_composition = {"O2": 100}  # in wt-%
total_gas_volume = 600  # in nm**3
temp_in_c = 1650  # in degree C

with TCPython() as session:
    a = database.LATEST.get_name()

    session.set_cache_folder(os.path.basename(__file__) + "_cache")

    metal = EquilibriumAddition(metal_composition, amount=1e3 * total_metal_mass_in_t, temperature=temp_in_c + 273.15)
    slag = EquilibriumAddition(slag_composition, amount=1e3 * total_slag_mass_in_t, temperature=temp_in_c + 273.15)
    gas = EquilibriumGasAddition(gas_composition, amount=total_gas_volume)

    calc = session.with_metallurgy().with_adiabatic_equilibrium_calculation(database)

    (calc
     .add_addition(metal)
     .add_addition(slag)
     .add_addition(gas))

    result = calc.calculate()

    print(f"Stable phases: {result.get_stable_phases()}")
    print(f"Temperature: {result.get_temperature() - 273.15:.1f} \N{DEGREE SIGN}C")

    print(f"Slag phases: {result.get_stable_phases_in_phase_group(PhaseGroup.ALL_SLAG)}")
    print("Composition of the overall slag:")
    slag_composition = result.get_composition_of_phase_group(PhaseGroup.ALL_SLAG, CompositionUnit.MOLE_PERCENT)
    for component, content in slag_composition.items():
        print(f"{component} = {content:.2f} mol-%")
