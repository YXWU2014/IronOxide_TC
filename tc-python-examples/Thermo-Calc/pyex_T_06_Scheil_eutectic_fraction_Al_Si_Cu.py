import numpy as np
from matplotlib import pyplot as plt
from tc_python import *

"""
Calculates the eutectic fraction using Scheil-solidification for varied alloying element content.
The alloy system Al-Si-Cu is used as an example.
"""

dependent_element = "Al"
database = "ALDEMO"
reference_composition = {"Si": 9, "Cu": 3}  # in wt-%
varied_element = "Cu"
variation = {"min": 1.0, "max": 5.0, "num_steps": 10}  # in wt-%
primary_solid_phase = "FCC_A1"
liquid_phase = "LIQUID"
t_step = 1.0  # in K, use smaller temperature steps for more accurate results

with TCPython() as session:
    session.set_cache_folder(os.path.basename(__file__) + "_cache")
    elements = list(reference_composition.keys())
    system = (session.
              select_database_and_elements(database, [dependent_element] + elements).
              get_system())

    calculator = (system.
                  with_scheil_calculation().
                  with_options(ScheilOptions().set_temperature_step(t_step)).
                  set_composition_unit(CompositionUnit.MASS_PERCENT))

    for element in reference_composition:
        calculator.set_composition(element, reference_composition[element])

    # vary the composition
    eutectic_fracs = []
    varied_composition = np.linspace(variation["min"], variation["max"], variation["num_steps"])

    for varied_element_content in varied_composition:
        calculator.set_composition(varied_element, varied_element_content)
        result = calculator.calculate()

        result_data = result.get_values_grouped_by_stable_phases_of(ScheilQuantity.mole_fraction_of_all_liquid(),
                                                                    ScheilQuantity.temperature())
        stable_phase_region_labels = result_data.keys()

        region_with_first_eutectic = None
        for stable_phases_str in stable_phase_region_labels:
            # split the string which is in the format "PHASE_1 + PHASE_2 + ..."
            stable_phases = [x.strip() for x in stable_phases_str.split("+")]
            if liquid_phase in stable_phases and primary_solid_phase in stable_phases:
                if len(stable_phases) - 2 == 1:
                    # region contains liquid, primary solid and one secondary solid phase (i.e. first eutectic forming)
                    region_with_first_eutectic = stable_phases_str
                    break

        if region_with_first_eutectic:
            mole_fraction_of_liquid = result_data[region_with_first_eutectic].x
            temp = result_data[region_with_first_eutectic].y
            # the liquid fraction at the beginning of the eutectic formation is equivalent to the eutectic fraction
            max_t_index = np.argmax(temp)
            eutectic_fracs.append(mole_fraction_of_liquid[max_t_index])
        else:
            eutectic_fracs.append(float("NaN"))

    # plot the results
    plt.plot(varied_composition, eutectic_fracs)
    plt.xlabel("{}-content [wt-%]".format(varied_element))
    plt.ylabel("Eutectic fraction [-]")
    plt.title("Eutectic fraction in AlSi9Cu3")
    plt.show()
