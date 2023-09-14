import sys
try:
    import pandas as pd
except ImportError:
    sys.stderr.write("The package `pandas` is not installed, please run `pip / pip3 install pandas`, this is not "
                     "possible with the Python bundled to Thermo-Calc")
    sys.exit(-1)
from tc_python import *

"""
This example shows how to read a time-temperature profile from a CSV-file and running a precipitation calculation
with it. The easiest CSV-file is simply a comma-separated text-file as shown in the present example.

Note: Requires the package pandas (install with `pip install pandas`) 
"""


# reading the CSV-file and converting it to the TC-Python datastructure
def get_time_temp_profile(file):
    df = pd.read_csv(file, header=(0), names=["t", "T"])
    temperature_profile = TemperatureProfile()
    for index, row in df.iterrows():
        temperature_profile.add_time_temperature(row["t"], row["T"])

    return temperature_profile, df.iloc[-1]["t"]


with TCPython():

    time_temp_profile, last_time_temp_profile_time = get_time_temp_profile("time_temperature.txt")

    calculation = (SetUp()
                   .set_cache_folder(os.path.basename(__file__) + "_cache")
                   .select_thermodynamic_and_kinetic_databases_with_elements("ALDEMO", "MALDEMO", ["Al", "Sc"])
                   .get_system()
                   .with_non_isothermal_precipitation_calculation()
                   .set_composition("Sc", 0.18)
                   .with_temperature_profile(time_temp_profile)
                   .set_simulation_time(last_time_temp_profile_time)
                   .with_matrix_phase(MatrixPhase("FCC_A1")
                                    .add_precipitate_phase(PrecipitatePhase("AL3SC"))
                               )
                   )

    simulation_results = calculation.calculate()
    time, mean_radius = simulation_results.get_mean_radius_of("AL3SC")
    print(time)
    print(mean_radius)


