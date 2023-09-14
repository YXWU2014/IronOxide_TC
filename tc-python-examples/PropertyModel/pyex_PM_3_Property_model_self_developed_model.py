from tc_python import *
import matplotlib.pyplot as plt
import numpy as np

"""
This example shows how to develop and run your own Property Model. 
An example model is provided in the folder PropertyModels/FreezeInEquilibriumPython.
It is a simplified version of the FreezeInEquilibrium model that is installed with Thermo-Calc. 

To use the example model, simply run this script.

Any changes made to the main model file (FreezeInEquilibriumPythonModel.py), 
will take effect the next time you run this script.
"""


with TCPython() as session:
    system = (session.select_database_and_elements("ALDEMO", ["Al", "Sc"])
                     .get_system()
              )

    calculation = system.with_property_model_calculation("Simplified equilibrium with freeze-in temperature", "PropertyModels")
    calculation.set_composition_unit(CompositionUnit.MASS_PERCENT)
    calculation.set_composition('Sc', 1.0)
    freeze_in_celsius = 350
    calculation.set_argument('Freeze-in-temperature', freeze_in_celsius + 273.15)

    temperatures_celsius = np.linspace(20, freeze_in_celsius, 30)
    conductivities = []
    for temp in temperatures_celsius:
        calculation.set_temperature(temp + 273.15)
        result = calculation.calculate()
        electric_conductivity = result.get_value_of('Electric conductivity (S/m)')
        conductivities.append(electric_conductivity)
        print('Electric conductivity at temperature {:.0f}(C) = {:.2e}(S/m)'.format(temp, electric_conductivity))

    plt.plot(temperatures_celsius, conductivities)
    plt.xlabel("Temperature [\N{DEGREE SIGN} C]")
    plt.ylabel("Electric conductivity (S/m)")
    plt.title("Electric conductivity vs Temperature")
    plt.show()


