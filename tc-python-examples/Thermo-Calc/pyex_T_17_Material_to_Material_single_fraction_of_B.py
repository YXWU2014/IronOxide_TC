from tc_python import *

"""
Calculates the phases occurring for a material mixture, in this case for a mixture of a martensitic stainless steel
with Alloy 800.
This type of calculation is for example useful for understanding effects when welding dissimilar materials - without
the need to perform diffusion calculations.
"""

with TCPython() as session:
    session.set_cache_folder(os.path.basename(__file__) + "_cache")
    system = session.select_database_and_elements("FEDEMO", ["Fe", "Cr", "Ni"]).get_system()

    calc = system.with_material_to_material().with_single_equilibrium_calculation()

    (calc
     .set_material_a({"Cr": 17.0, "Ni": 2.0}, dependent_component="Fe")
     .set_material_b({"Cr": 19.0, "Ni": 35.0}, dependent_component="Fe")
     .set_composition_unit(CompositionUnit.MASS_PERCENT)
     .with_first_constant_condition(ConstantCondition.fraction_of_material_b(fraction_of_material_b=0.4))
     .with_second_constant_condition(ConstantCondition.temperature(temperature=650 + 273.15)))
    result = calc.calculate()

    print("Stable phases at 650 \N{DEGREE SIGN}C, 40 wt-% Alloy 800: {}".format(result.get_stable_phases()))
    print("Molar fractions:")
    for phase in result.get_stable_phases():
        molar_frac_in_pct = 100 * result.get_value_of(ThermodynamicQuantity.mole_fraction_of_a_phase(phase))
        print("{}={:.1f}%".format(phase, molar_frac_in_pct))
