from tc_python import *
from matplotlib import pyplot as plt

"""
Calculates the solidification with and without Solute Trapping.
Then compare the solidification in the two cases by plotting temperature vs. mole fraction of solid phase.
The alloy system Al-Si-Cu is used as an example.
"""


database = "ALDEMO"
dependent_element = "Al"
composition = {"Si": 7.5, "Cu": 0.2}  # in wt-%
step = 0.5
elements = list(composition.keys())

with TCPython() as session:
    session.set_cache_folder(os.path.basename(__file__) + "_cache")
    system = (session.
              select_database_and_elements(database, [dependent_element] + elements).
              get_system())

    scheilCalculator = (system.
                        with_scheil_calculation().
                        set_composition_unit(CompositionUnit.MASS_PERCENT).
                        with_options(ScheilOptions().set_temperature_step(0.5)))

    for element in composition:
        scheilCalculator.set_composition(element, composition.get(element))

    scheilCalculator.with_calculation_type(ScheilCalculationType.scheil_classic())
    scheilResult = scheilCalculator.calculate()

    solid_frac1, temp1 = scheilResult.get_values_of(x_quantity=ScheilQuantity.mole_fraction_of_all_solid_phases(),
                                                    y_quantity=ScheilQuantity.temperature())



    soluteTrappingCalculator = (system.
                  with_scheil_calculation().
                            set_composition_unit(CompositionUnit.MASS_PERCENT).
                            with_options(ScheilOptions().set_temperature_step(0.5)))

    for element in composition:
        soluteTrappingCalculator.set_composition(element, composition.get(element))

    soluteTrappingCalculator.with_calculation_type(ScheilCalculationType.scheil_solute_trapping()
                                     .set_primary_phasename("AUTOMATIC")
                                     .set_angle(45).set_scanning_speed(1))
    soluteTrappingresult = soluteTrappingCalculator.calculate()

    solid_frac2, temp2 = soluteTrappingresult.get_values_of(x_quantity=ScheilQuantity.mole_fraction_of_all_solid_phases(),
                                                    y_quantity=ScheilQuantity.temperature())





# plot the results
    plt.plot(solid_frac1,temp1,solid_frac2,temp2)
    plt.legend(["Classic Scheil", "Scheil with Solute Trapping"])
    plt.title("Solidification in Al- 7.5w% Si- 0.2w% Cu")
    plt.xlabel("Percentage of solidified material [%]")
    plt.ylabel("Temperature [K]")
    plt.show()