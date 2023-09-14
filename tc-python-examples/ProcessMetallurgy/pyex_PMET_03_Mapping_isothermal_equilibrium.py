from tc_python import *
import numpy as np
from matplotlib import pyplot as plt

"""
This example shows how to create isothermal equilibrium calculations with
varied composition of two steel components.

This example requires the database TCOX9 or higher.
"""

database = ProcessDatabase.TCOX12

mn_conc_range_in_wt_pct = np.arange(0.1, 2.3, 0.2)
cr_conc_range_in_wt_pct = np.arange(10.0, 21.0, 1.0)
material_temp_in_c = 1600

steel_composition = {'Fe': None, 'C': 0.03, 'Mn': 1.0, 'S': 0.02, 'Cr': 17.5, 'Ni': 7.9, 'O': 0.01}
steel_mass_in_t = 95

# note that this slag composition is not summing to 100%, such data is frequent in industrial context
# you can set the flag `do_scale` on the `EquilibriumAddition` to scale the composition automatically to 100%
slag_composition = {'CaO': 40, 'SiO2': 10, 'MgO': 8, 'MnO': 4, 'FeO': 3, 'Cr2O3': 25, 'Al2O3': 4}
slag_mass_in_t = 7

process_addition = {
    'ferro_silicon': {
        'composition': {'Fe': 20, 'Si': None},
        'amount_in_kg': 100
    },
    'aluminium': {
        'composition': {'Al': 100},
        'amount_in_kg': 500
    },
    'lime': {
        'composition': {'CaO': 100},
        'amount_in_kg': 500
    },
    'silica': {
        'composition': {'SiO2': 100},
        'amount_in_kg': 20
    }
}

with TCPython() as session:
    session.set_cache_folder(os.path.basename(__file__) + '_cache')

    steel = EquilibriumAddition(steel_composition, 1e3 * steel_mass_in_t, material_temp_in_c + 273.15)
    slag = EquilibriumAddition(slag_composition, 1e3 * slag_mass_in_t, material_temp_in_c + 273.15, do_scale=True)

    additions = []
    for addition in process_addition.values():
        additions.append(EquilibriumAddition(addition['composition'], addition['amount_in_kg'],
                                             material_temp_in_c + 273.15))

    calc = session.with_metallurgy().with_isothermal_equilibrium_calculation(database)
    (calc
     .add_addition(steel)
     .add_addition(slag)
     .set_temperature(material_temp_in_c + 273.15))

    for addition in additions:
        calc.add_addition(addition)

    cr2o3_content_in_slag = []
    for mn_conc in mn_conc_range_in_wt_pct:
        calc.update_addition(steel.set_component_composition(component='Mn', content=mn_conc))
        for cr_conc in cr_conc_range_in_wt_pct:
            print(f"Calculating for Mn={mn_conc:.1f} wt-%, Cr={cr_conc:.1f} wt-%")

            calc.update_addition(steel.set_component_composition(component='Cr', content=cr_conc))
            r = calc.calculate()

            cr2o3_content_in_slag.append(r.get_composition_of_phase_group(PhaseGroup.ALL_SLAG)['Cr2O3'])

    X, Y = np.meshgrid(cr_conc_range_in_wt_pct, mn_conc_range_in_wt_pct)
    Z = np.reshape(cr2o3_content_in_slag, (len(mn_conc_range_in_wt_pct), len(cr_conc_range_in_wt_pct)))
    CS = plt.contour(X, Y, Z)
    plt.xlabel("Cr-content / wt-%")
    plt.ylabel("Mn-content / wt-%")
    plt.title("Cr2O3-content in slag / wt-%")
    plt.clabel(CS, inline=True)
    plt.show()
