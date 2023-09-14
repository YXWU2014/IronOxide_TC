from tc_python import *
import json
import numpy as np
from matplotlib import pyplot as plt

"""
This is example shows how a Vacuum Oxygen Decarburization (VOD) refining process could be modelled. It is inspired
by this paper: R. Ding, B. Blanpain, P.T. Jones, P. Wollants: Modeling of the Vacuum Oxygen
Decarburization Refining Process, Metallurgical and Materials Transactions 31B (2000) 197 - 206

The validation data has been derived from that paper as well.

This model is showing several features of process simulations, such as:
* time-dependent mass transfer coefficients
* time-dependent pressure
* inclusion flotation
* cooling due to heat losses
* heat transfer between the zones
* control of degassing

The calculation required the database TCOX9 or higher (slight model adjustments might be required based on the version).

A more detailed description of this model can be found here: https://thermocalc.com/content/uploads/Application_Examples/VOD_Vacuum_Oxygen_Decarburization/simulating-vacuum-oxygen-decarburization-kinetics-using-the-process-metallurgy-module.pdf
"""

database = ProcessDatabase.TCOX12

steel_mass_transfer_coeff_blowing = 2.0e-3  # in m/s
steel_mass_transfer_coeff_no_blowing = 6.0e-4  # in m/s
steel_density = 7800  # in kg/m**3

slag_mass_transfer_coeff_blowing = 4.0e-3  # in m/s
slag_mass_transfer_coeff_no_blowing = 1.2e-3  # in m/s
slag_density = 4500  # in kg/m**3
heat_transfer_coefficient = 5.0e3  # in W/(m**2 * K)
flotation_rate = 5.0  # in %/min
heat_loss_steel_in_mw = -3.0  # in MW

area = 10.0  # in m**2

blowing_pressure_in_bar = 0.15
time_blowing_in_min = 45
oxygen_flow = 33.333  # in Nm**3/min
degassing_pressure_in_pa = 200
degassing_time_in_min = 10
reduction_time_in_min = 40

reference_file_path = "ding_et_al_2000_measured_data_fig_3.json"

time_end_in_min = time_blowing_in_min + degassing_time_in_min + reduction_time_in_min

with TCPython() as session:
    session.set_cache_folder(os.path.basename(__file__) + "_cache")

    steel = SingleTimeAddition({"Fe": None, "C": 0.48, "Si": 0.20, "Mn": 0.55, "Cr": 16.45, "Ni": 10.49},
                               amount=121e3, temperature=1549 + 273.15)
    slag = SingleTimeAddition({"CaO": None, "SiO2": 12, "MgO": 28}, amount=1200, temperature=1549 + 273.15)
    oxygen = ContinuousGasAddition({"O2": 100}, rate=oxygen_flow / 60)

    # deduced the compositions by analysis of the data in Ding et al. (2000)
    metallic_reducer = SingleTimeAddition({"Fe": 0.09, "Si": 0.32, "Mn": 0.35, "Al": 0.12, "Cr": 0.12},
                                          amount=937.5, composition_unit=CompositionUnit.MASS_FRACTION)
    slag_reducer = SingleTimeAddition({"CaO": 80, "MgO": 20}, amount=2000 / 4)

    calc = session.with_metallurgy().with_adiabatic_process_calculation(database)

    steel_zone = MetalBulkZone(steel_density)
    slag_zone = SlagBulkZone(slag_density)

    steel_mass_transfer_coeff = MassTransferCoefficients()
    steel_mass_transfer_coeff.add(steel_mass_transfer_coeff_blowing, 0.0)
    steel_mass_transfer_coeff.add(steel_mass_transfer_coeff_no_blowing, time_blowing_in_min * 60)

    slag_mass_transfer_coeff = MassTransferCoefficients()
    slag_mass_transfer_coeff.add(slag_mass_transfer_coeff_blowing, 0.0)
    slag_mass_transfer_coeff.add(slag_mass_transfer_coeff_no_blowing, time_blowing_in_min * 60)

    reaction_zone = ReactionZone(area, steel_zone, steel_mass_transfer_coeff, slag_zone, slag_mass_transfer_coeff)
    (reaction_zone
     .add_heat_transfer(heat_transfer_coefficient)
     .add_transfer_of_phase_group(TransferOfPhaseGroup(PhaseGroup.ALL_SLAG, steel_zone)
                                  .add(flotation_rate / 60)))

    (calc
     .set_end_time(60 * time_end_in_min)
     .with_reaction_zone(reaction_zone))

    # initial zones
    steel_zone.add_addition(steel, time=0)
    slag_zone.add_addition(slag, time=0)

    # degassing happens only at the interface
    steel_zone.disable_degassing()
    slag_zone.disable_degassing()

    # heat loss
    steel_zone.add_power(1e6 * heat_loss_steel_in_mw)

    # pressure control
    calc.set_pressure_in_time_period(1.0e5 * blowing_pressure_in_bar, 0.0, time_blowing_in_min * 60)
    calc.set_pressure_in_time_period(degassing_pressure_in_pa, time_blowing_in_min * 60)

    # oxygen blowing
    steel_zone.add_continuous_addition(oxygen, 0, time_blowing_in_min * 60)

    # reduction step
    steel_zone.add_addition(metallic_reducer, (time_blowing_in_min + degassing_time_in_min) * 60)
    slag_zone.add_addition(slag_reducer, (time_blowing_in_min + degassing_time_in_min) * 60)
    steel_zone.add_addition(metallic_reducer, (time_blowing_in_min + degassing_time_in_min + 1) * 60)
    slag_zone.add_addition(slag_reducer, (time_blowing_in_min + degassing_time_in_min + 1) * 60)
    steel_zone.add_addition(metallic_reducer, (time_blowing_in_min + degassing_time_in_min + 2) * 60)
    slag_zone.add_addition(slag_reducer, (time_blowing_in_min + degassing_time_in_min + 2) * 60)
    steel_zone.add_addition(metallic_reducer, (time_blowing_in_min + degassing_time_in_min + 3) * 60)
    slag_zone.add_addition(slag_reducer, (time_blowing_in_min + degassing_time_in_min + 3) * 60)

    result = calc.calculate()
    times = np.array(result.get_time_points())

    # plot the results
    with open(reference_file_path, "r") as json_file:
        reference_data = json.load(json_file)

    plt.figure()
    steel_composition_ref = reference_data["data"]["steel"]["data"]
    for component in ["Cr", "Mn", "Si", "C", "Ni"]:
        line = plt.plot(times / 60, result.get_composition(steel_zone)[component], label=component)
        if component in steel_composition_ref:
            plt.plot(steel_composition_ref[component]["x"], steel_composition_ref[component]["y"],
                     "--", color=line[0].get_color())
    plt.xlabel("time / min")
    plt.ylabel("Composition of the steel melt / wt-%")
    plt.legend()
    plt.title("Ref. (dashed): Ding et al., Met Mater Trans 31B (2000) 197")

    plt.figure()
    slag_composition_ref = reference_data["data"]["slag"]["data"]
    slag_composition = result.get_composition_of_phase_group(slag_zone, PhaseGroup.ALL_SLAG)
    for component in ["Al2O3", "CaO", "Cr2O3", "MgO", "MnO", "SiO2"]:
        if component == "Cr2O3":
            line = plt.plot(times / 60, np.array(slag_composition["Cr2O3"]) + np.array(slag_composition["CrO"]),
                            label="Cr2O3 + CrO")
        else:
            line = plt.plot(times / 60, slag_composition[component], label=component)

        if component in slag_composition_ref:
            plt.plot(slag_composition_ref[component]["x"], slag_composition_ref[component]["y"],
                     "--", color=line[0].get_color())

    plt.xlabel("time / min")
    plt.ylabel("Composition of the slag / wt-%")
    plt.legend()
    plt.title("Ref. (dashed): Ding et al., Met Mater Trans 31B (2000) 197")

    plt.figure()
    plt.plot(times / 60, result.get_pressure(steel_zone))
    plt.xlabel("time / min")
    plt.ylabel("pressure / Pa")

    plt.figure()
    plt.plot(times / 60, np.array(result.get_temperature(steel_zone)) - 273.15, label="steel")
    plt.plot(times / 60, np.array(result.get_temperature(slag_zone)) - 273.15, label="slag")
    plt.plot(reference_data["data"]["temperature"]["data"]["x"],
             reference_data["data"]["temperature"]["data"]["y"],
             "--", label="reference")
    plt.xlabel("time / min")
    plt.ylabel("temperature/ \N{DEGREE SIGN}C")
    plt.legend()
    plt.title("Ref. (dashed): Ding et al., Met Mater Trans 31B (2000) 197")
    plt.plot()

    plt.figure()
    slag_masses_in_kg = result.get_amount(slag_zone)
    oxide_pct_in_slag = result.get_composition_of_phase_group(slag_zone, PhaseGroup.ALL_SLAG)
    cr_oxides_in_slag_masses_in_kg = (np.array(slag_masses_in_kg) *
                                      (np.array(oxide_pct_in_slag["Cr2O3"]) + np.array(oxide_pct_in_slag["CrO"])) / 100)
    line = plt.plot(times / 60, slag_masses_in_kg, label="total")
    slag_mass_ref = reference_data["data"]["total_slag_weight"]["data"]
    plt.plot(slag_mass_ref["x"], slag_mass_ref["y"], "--", color=line[0].get_color())

    line = plt.plot(times / 60, cr_oxides_in_slag_masses_in_kg, label="Cr-oxides")
    cr_oxide_slag_mass_ref = reference_data["data"]["cr2o3_slag_weight"]["data"]
    plt.plot(cr_oxide_slag_mass_ref["x"], cr_oxide_slag_mass_ref["y"], "--", color=line[0].get_color())

    plt.xlabel("time / min")
    plt.ylabel("slag mass / kg")
    plt.legend()
    plt.title("Ref. (dashed): Ding et al., Met Mater Trans 31B (2000) 197")

    plt.figure()
    plt.xlabel("time / min")
    plt.ylabel("Exhaust gas composition / wt-%")
    for component, composition in result.get_exhaust_gas().get_composition().items():
        plt.plot(times / 60, composition, label=component)
    plt.legend()

    plt.figure()
    plt.xlabel("time / min")
    plt.ylabel("Accumulated exhaust gas amount / kg")
    for component, accumulated_amount in result.get_exhaust_gas().get_amount_of_components().items():
        plt.plot(times / 60, accumulated_amount, label=component)
    plt.legend()

    plt.figure()
    plt.xlabel("time / min")
    plt.ylabel("Phase fraction in steel zone / -")
    for phase, fraction in result.get_fraction_of_phases(steel_zone).items():
        plt.plot(times / 60, fraction, label=phase)
    plt.legend()

    plt.figure()
    plt.xlabel("time / min")
    plt.ylabel("Phase fraction in slag zone / -")
    for phase, fraction in result.get_fraction_of_phases(slag_zone).items():
        plt.plot(times / 60, fraction, label=phase)
    plt.legend()

    plt.figure()
    plt.xlabel("time / min")
    plt.ylabel("Phase fraction in reaction zone / -")
    for phase, fraction in result.get_fraction_of_phases(reaction_zone).items():
        plt.plot(times / 60, fraction, label=phase)
    plt.legend()

    fig, ax1 = plt.subplots()
    ax1.plot(np.array(result.get_time_points()[:-1]) / 60, np.diff(result.get_time_points()), "bo-")
    ax1.set_xlabel("time / min")
    ax1.set_ylabel("time step / s", color="b")
    ax1.tick_params(axis="y", labelcolor="b")
    ax2 = ax1.twinx()
    ax2.set_ylabel("Number of calculations per time-step", color="r")
    ax2.plot(np.array(result.get_time_points()[:-1]) / 60, np.diff(result.get_num_of_performed_steps()), "ro-")
    ax2.tick_params(axis="y", labelcolor="r")
    ax3 = ax1.twinx()
    ax3.get_yaxis().set_visible(False)
    ax3.plot(np.array(result.get_time_points()) / 60, result.get_num_of_performed_steps(), "go-")

    plt.figure()
    for element, amount in result.get_amount_of_elements().items():
        plt.plot(times / 60, amount, label=element)
    plt.xlabel("time / min")
    plt.ylabel("total mass of element / kg")
    plt.legend()
    plt.show()
