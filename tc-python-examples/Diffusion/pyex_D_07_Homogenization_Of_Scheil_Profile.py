from itertools import cycle

import numpy as np
from matplotlib import pyplot as plt

from tc_python import *

"""
This example models the homogenization of a cast Ni-Cr steel and compares predictions with the experimental data
collated by Fuchs and Roósz (1). 

As a first step, the microsegregation after solidification is simulated using a Scheil-calculation, then
as a second step the homogenization is simulated using a diffusion simulation.

The conditions studied have a dendritic half spacing of 200 µm and are heat treated at 1120 °C. 
The data has been de-normalized to allow comparison using weight percent composition values.
The composition of the steel is 0.4C, 0.65Mn, 0.35Si, 0.015S, 0.01P, 1.9Ni, 0.95Cr and 0.3 Mo (wt.%). 
The diffusion of Cr and Ni are modelled using a simplified chemistry of 0.4C, 0.65Mn, 1.9Ni, and 0.95Cr using the
FEDEMO thermodynamic and MFEDEMO mobility databases.

References
1. Homogenization of Iron-Base Cast Alloys. Fuchs, E. G., and A. Roósz. 1975, Metal Science, pp. 111-118.

"""

thermodynamic_database = "FEDEMO"
mobility_database = "MFEDEMO"
dependent_element = "Fe"
composition_wt_pct = {"Ni": 1.9, "Cr": 0.95, "C": 0.4, "Mn": 0.65}  # in wt-%
fast_diffusers = ["C"]
num_interp_points = 100
alloy = "Fuchs and Roosz (1975)"
dendrite_arm_spacing = 400  # in micrometers
homogenization_temperature = 1120  # in degree C
homogenization_time = 72.0  # in hours
FIRST_TIMEPOINT_WITH_PHASES = 1e-5  # to get the initial phase distribution close to t=0


def interpolate_scheil_composition_profiles(grid_original, composition_original, grid_interpolated, elements):
    """
    The constant composition_wt_pct during the Scheil-steps should be kept also when interpolating to a new grid.
    Otherwise, it could be errors in the mass balance.
    E.g. the mass balance is rather off if one interpolates with a linear function between previous and final Scheil
    step in a case that a large fraction solidifies with eutectic composition_wt_pct at the last Scheil step.
    """
    interpolated_composition = {}
    for element in elements:
        interpolated_composition[element] = np.ones(len(grid_interpolated))

    for i_interp, gp_interp in enumerate(grid_interpolated):
        for i_orig, gp_orig in enumerate(grid_original):
            if gp_interp < grid_original[0]:
                # Use composition_wt_pct of first Scheil step
                for element in elements:
                    interpolated_composition[element][i_interp] = composition_original[element][i_orig]
                break
            elif gp_interp > grid_original[-1]:
                # Use composition_wt_pct of last Scheil step
                for element in elements:
                    interpolated_composition[element][i_interp] = composition_original[element][-1]
                break
            elif gp_orig <= gp_interp < grid_original[i_orig + 1]:
                # Use the Scheil-step composition_wt_pct for intermediate values
                for element in elements:
                    interpolated_composition[element][i_interp] = composition_original[element][i_orig + 1]
                break

    return interpolated_composition


with TCPython() as session:
    elements = list(composition_wt_pct.keys())
    system = (session
              .set_cache_folder(os.path.basename(__file__) + "_cache")
              .select_thermodynamic_and_kinetic_databases_with_elements(thermodynamic_database, mobility_database,
                                                                        [dependent_element] + elements)
              .get_system())

    scheil_calc = (system.with_scheil_calculation()
                   .with_calculation_type(ScheilCalculationType
                                          .scheil_classic()
                                          .set_fast_diffusing_elements(fast_diffusers))
                   .set_composition_unit(CompositionUnit.MASS_PERCENT))

    for element in composition_wt_pct:
        scheil_calc.set_composition(element, composition_wt_pct[element])

    result = scheil_calc.calculate()

    scheil_curve = result.get_values_grouped_by_stable_phases_of(ScheilQuantity.mole_fraction_of_all_solid_phases(),
                                                                 ScheilQuantity.temperature())
    phases_in_calc = result.get_stable_phases()

    # Get the solid concentration along the solidification
    average_solid_compo_in_slice = {}
    for element in elements:
        (total_solid_fracs, average_solid_compo_in_slice[element]) = result.get_values_of(
            ScheilQuantity.mole_fraction_of_all_solid_phases(),
            ScheilQuantity.average_composition_of_solid_phases_as_mass_fraction(element)
        )

    # Homogenization simulation

    # Interpolate to new grid
    sec_dendrite_arm_spacing = dendrite_arm_spacing * 1e-6 / 2
    grid_in_dendrite_from_scheil = np.array(total_solid_fracs) * sec_dendrite_arm_spacing
    grid_in_dendrite_interpolated = np.linspace(0, sec_dendrite_arm_spacing, num_interp_points)
    average_solid_compo_in_slice_interpolated = interpolate_scheil_composition_profiles(grid_in_dendrite_from_scheil,
                                                                                        average_solid_compo_in_slice,
                                                                                        grid_in_dendrite_interpolated,
                                                                                        elements)

    # Composition profiles for fast diffusers are not available, use average alloy composition instead
    for element in elements:
        if element in fast_diffusers:
            average_solid_compo_in_slice_interpolated[element] = np.ones(len(grid_in_dendrite_interpolated)) * \
                                                                 composition_wt_pct[element] * 1e-2

    concentration_profiles = PointByPointGrid(unit_enum=Unit.MASS_FRACTION)
    for i in range(0, num_interp_points):
        gridpoint = GridPoint(grid_in_dendrite_interpolated[i])
        for element in elements:
            gridpoint.add_composition(element, average_solid_compo_in_slice_interpolated[element][i])
        concentration_profiles.add_point(gridpoint)

    dendrite_region = (Region("Solid").with_point_by_point_grid_containing_compositions(concentration_profiles))

    for phase in phases_in_calc:
        if not system.get_phase_object(phase).is_liquid():
            dendrite_region.add_phase(phase)

    dictra = (system.with_isothermal_diffusion_calculation()
              .set_temperature(homogenization_temperature + 273.15)
              .set_simulation_time(homogenization_time * 3600)
              .add_region(dendrite_region)
              .with_solver(Solver.automatic()))

    homo_results = dictra.calculate()

    # Plot results
    plt.figure(1)
    plt.title("Alloy: {}".format(alloy) + ", Dendrite arm spacing = {} \N{MICRO SIGN}m".
              format(dendrite_arm_spacing))
    for (label, scheil_stable_phases) in scheil_curve.items():
        plt.plot(scheil_stable_phases.x, scheil_stable_phases.y, label=label)
    plt.xlabel("Fraction solid phase")
    plt.ylabel("Temperature (K)")
    plt.legend(loc="best")

    plt.figure(2)
    plt.title("Alloy: {}".format(alloy) + ", Dendrite arm spacing = {} \N{MICRO SIGN}m, {} \N{DEGREE SIGN}C".
              format(dendrite_arm_spacing, homogenization_temperature))
    linestyles = cycle(['-', '--', '-.', ':'])
    for time in [FIRST_TIMEPOINT_WITH_PHASES, homogenization_time / 2, homogenization_time]:
        linestyle = next(linestyles)
        colors = cycle(["b", "r", "g", "m"])
        for element in elements:
            color = next(colors)
            distance, w_solid_homogenized = homo_results.get_mass_fraction_of_component_at_time(element, time * 3600)
            if time == FIRST_TIMEPOINT_WITH_PHASES:
                time_label = 0
            else:
                time_label = time
            plt.plot(np.array(distance) * 1e6, np.array(w_solid_homogenized) * 100.0,
                     ls=linestyle, label="{} after {} h".format(element, time_label), color=color)

    plt.xlabel("distance (\N{MICRO SIGN}m)")
    plt.ylabel("Concentration (mass-percent)")
    plt.legend(loc="best")

    plt.figure(3)
    # Experimental data from Fuchs and Roósz (1975)
    cr_1120C_exp = [1.4924789, 1.3224482, 1.1038373]
    ni_1120C_exp = [2.8543548, 2.8041256, 2.4525212]
    time_exp_h = [8.0, 24, 72]

    plt.title("Alloy: {}".format(alloy) + ", Dendrite arm spacing = {} \N{MICRO SIGN}m, {} \N{DEGREE SIGN}C".
              format(dendrite_arm_spacing, homogenization_temperature))

    time, w_f_cr = homo_results.get_mass_fraction_at_upper_interface("Solid", "Cr")
    plt.plot(np.array(time) / 3600.0, np.array(w_f_cr) * 100, label="Cr", color="r")
    plt.plot(time_exp_h, cr_1120C_exp, 's', color="r")

    time, w_f_ni = homo_results.get_mass_fraction_at_upper_interface("Solid", "Ni")
    plt.plot(np.array(time) / 3600.0, np.array(w_f_ni) * 100, label="Ni", color="b")
    plt.plot(time_exp_h, ni_1120C_exp, '.', color="b")

    plt.ylim(0, 4)
    plt.xlabel("time (hours)")
    plt.ylabel("Concentration (mass-percent)")
    plt.legend(loc="best")
    plt.show()
