from tc_python import *
from matplotlib import pyplot as plt

"""
This example shows how a very simplified process simulation of a BOF converter
can be set up.
"""

with TCPython() as session:
    session.set_cache_folder(os.path.basename(__file__) + '_cache')

    calc = session.with_metallurgy().with_adiabatic_process_calculation(ProcessDatabase.OXDEMO)
    calc.set_end_time(15 * 60)

    steel_zone = MetalBulkZone(density=7800)
    slag_zone = SlagBulkZone(density=4500)

    steel_zone.add_addition(SingleTimeAddition({"Fe": None, "C": 4.5, "Si": 1.0}, amount=120e3,
                                               temperature=1600 + 273.15), time=0)
    slag_zone.add_addition(SingleTimeAddition({"CaO": 75, "SiO2": 25}, amount=1.2e3,
                                              composition_unit=CompositionUnit.MOLE_PERCENT,
                                              temperature=1500 + 273.15), time=0)

    steel_zone.add_continuous_addition(ContinuousGasAddition({"O2": 100}, rate=1,
                                                             rate_unit=GasRateUnit.NORM_CUBIC_METER_PER_SEC))

    # the mass transfer coefficient is an empirical parameter that depends on the conditions in the actual converter
    calc.with_reaction_zone(ReactionZone(area=10.0,
                                         left_zone=steel_zone, mass_transfer_coefficient_left=1.0e-5,
                                         right_zone=slag_zone, mass_transfer_coefficient_right=1.0e-6))

    result = calc.calculate()

    print(f"Stable phases in the steel melt: {result.get_stable_phases(steel_zone)}")

    plt.figure()
    plt.plot(result.get_time_points(), result.get_temperature('metal'))
    plt.title("Very simple BOF process simulation")
    plt.xlabel("Time / s")
    plt.ylabel("Temperature of the steel melt / K")

    plt.figure()
    for component, content in result.get_composition_of_phase_group(steel_zone, PhaseGroup.ALL_METAL).items():
        if component != "Fe":
            plt.plot(result.get_time_points(), content, label=component)
    plt.title("Very simple BOF process simulation")
    plt.xlabel("Time / s")
    plt.ylabel("Steel composition / wt-%")
    plt.legend()

    plt.show()
