import numpy as np
from matplotlib import pyplot as plt
from tc_python import *

"""
Calculates the microsegregation profile in a solidified Ni-based superalloy using the Scheil-method.
The plot is normalized relative to the nominal composition and shows the composition of the matrix phase (FCC).
A model alloy in the system Ni-Al-Cr is used as an example.
"""


database = "NIDEMO"
dependent_element = "Ni"
composition = {"Al": 7.0, "Cr": 7.0}  # in wt-%
relevant_phase = "FCC_L12"

elements = list(composition.keys())

with TCPython() as session:
    session.set_cache_folder(os.path.basename(__file__) + "_cache")
    system = (session.
              select_database_and_elements(database, [dependent_element] + elements).
              get_system())

    # convert the nominal composition of the alloy to atomic fractions - takes elements in camel-case
    atomic_frac = system.convert_composition(composition, ConversionUnit.WEIGHT_PERCENT, ConversionUnit.MOLE_FRACTION,
                                             dependent_component=dependent_element)

    # perform the Scheil calculation for the same system
    scheil_calculator = (system.
                         with_scheil_calculation().
                         set_composition_unit(CompositionUnit.MASS_PERCENT))

    for element in composition:
        scheil_calculator.set_composition(element, composition[element])
    scheil_result = scheil_calculator.calculate()
    scheil_result_data = \
        scheil_result.get_values_grouped_by_quantity_of(ScheilQuantity.mole_fraction_of_all_solid_phases(),
                                                        ScheilQuantity.composition_of_phase_as_mole_fraction(
                                                            relevant_phase, "All"))

    # analyze and plot the result data contained for all components at once
    for label in scheil_result_data.keys():
        # the format of the label is (here) always "EL in PHASE"
        label_content = [x.strip().title() for x in label.split("in")]
        element = label_content[0]
        if element != dependent_element:
            total_solid_frac = scheil_result_data[label].x
            element_frac_composition = scheil_result_data[label].y
            normalized_element_composition = np.array(element_frac_composition) / atomic_frac[element]
            plt.plot(100 * np.array(total_solid_frac), normalized_element_composition, label=element)

    plt.legend()
    plt.title("Microsegregation in NiAl7Cr7")
    plt.xlabel("Percentage of solidified material [-]")
    plt.ylabel("Normalized composition of the FCC phase [-]")
    plt.show()
