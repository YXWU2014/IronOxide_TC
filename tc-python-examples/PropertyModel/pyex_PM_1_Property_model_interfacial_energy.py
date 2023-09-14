from tc_python import *

"""
Calculating Interfacial Energy with a Property Model

This example shows how to run a (Jython) Property Model from TC-Python to calculate the interfacial 
energy. The Thermo-Calc Property Model uses a broken-bond approach. Any other pre-installed or 
user-defined Property Model created in Thermo-Calc can be loaded and used in the same way as in this 
example. Search the Thermo-Calc Help (in Thermo-Calc press F1) for more information about the Property
Models and the Property Model Development Framework. 


The details of a Property Model (arguments, result quantities, and so forth) are defined in the Thermo-Calc Property 
Model and are not known to TC-Python in advance. Therefore, when using the TC-Python property models, the 
workflow differs compared to other TC-Python modules. The available arguments need to be queried by using 
the respective `get_...()`- method. This requires some interactive development style until a first working
version of the code is set up.

.. note::

    When TC-Python refers to the term "arguments", in the "Property Model Development Framework" it refer to "UI Panel
    Components". This refers to the same elements of the Property Model but differs in the same because TC-Python does not
    have a user interface (UI).
"""


temp = 800  # in degree C
dependent_element = "Ni"
composition = {"Al": 5.0, "Cr": 10.0}  # in wt-%

with TCPython() as session:
    system = (session
        .set_cache_folder(os.path.basename(__file__) + "_cache")
        .select_database_and_elements("NIDEMO", [dependent_element] + list(composition.keys()))
        .without_default_phases()
        .select_phase("FCC_L12#1")
        .select_phase("FCC_L12#2")
        .get_system())

    # asking at first for the available property models and their name
    print("Available property models in the default Property Model directory: {}".format(session.get_property_models()))
    calc = system.with_property_model_calculation("Interfacial energy")

    (calc
        .set_temperature(temp + 273.15)  # if unchanged, the temperature is set to 1000 K by default
        .set_composition_unit(CompositionUnit.MASS_PERCENT))

    for element in composition:
        calc.set_composition(element, composition[element])

    # asking for the available arguments, if we do not change them, they will be set to the default defined in the model
    print("Available arguments: {}".format(calc.get_arguments()))
    print("Description of '{}': {}".format("matrix", calc.get_argument_description("matrix")))
    print("Default value of '{}': {}".format("matrix", calc.get_argument_default("matrix")))

    result = (calc
        .set_argument("matrix", "FCC_L12")
        .set_argument("precipitate", "FCC_L12#2")
        .calculate())

    # asking for the available result quantities
    print("Available result quantities: {}".format(result.get_result_quantities()))
    print("Description of '{}': {}".format("interfacialEnergy",
                                           result.get_result_quantity_description("interfacialEnergy")))

    interfacial_energy = result.get_value_of("interfacialEnergy")
    print("Interfacial energy at {} \N{DEGREE SIGN}C: {} mJ/m**2".format(temp, 1000 * interfacial_energy))
