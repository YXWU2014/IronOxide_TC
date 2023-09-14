# %% Thermocalc calculation

from tc_python import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from multiprocessing import Pool

current_directory = os.path.dirname(os.path.abspath(__file__))
cache_fname = os.path.basename(__file__) + "_cache"
output_fname = os.path.splitext(os.path.basename(__file__))[0]

print("Cache Filename: ", cache_fname)
print("Output Filename: ", output_fname)
print("Current Dir: ", current_directory)


def tc_calculation(tk):
    with TCPython() as start:
        batch_calculation = (
            start
            .set_cache_folder(os.path.join(current_directory, cache_fname))
            .set_ges_version(5)
            .select_database_and_elements("tcfe11", ["Fe", "O"])
            .deselect_phase("*")
            .select_phase("BCC_A2 Liquid")
            .select_database_and_elements("ssub5", ["Fe", "O"])
            .deselect_phase("*")
            .select_phase("HEMATITE MAGNETITE WUSTITE GAS")
            .get_system()
            .with_batch_equilibrium_calculation()
            .set_condition("T", 100+273.15)
            .set_condition("P", 0.5)
            .set_condition("lnacr(o)", -400)
            .with_reference_state("O", 'GAS', tk, 10000)
            .disable_global_minimization()
        )

        # Generate condition combinations for equilibrium calculations
        k = 500
        list_of_conditions = [(("lnacr(o)", lnacr_o), ("T", tk))
                              for lnacr_o in np.linspace(-80, -5, k)]

        batch_calculation.set_conditions_for_equilibria(list_of_conditions)

        results = batch_calculation.calculate(
            ["np(HEMATITE)", "np(MAGNETITE)", "np(WUSTITE)", "np(BCC_A2)", "np(LIQUID)"], 100)

        return (
            list_of_conditions,
            results.get_values_of('np(HEMATITE)'),
            results.get_values_of('np(MAGNETITE)'),
            results.get_values_of('np(WUSTITE)'),
            results.get_values_of('np(BCC_A2)'),
            results.get_values_of('np(LIQUID)')
        )


# Parallelize the computation over different tk values
tk_values = np.arange(100+273.15, 1600+273.15, 50)
print("temperature range: ", tk_values)
with Pool() as pool:
    all_results = pool.map(tc_calculation, tk_values)

# print(len(all_results[0]))

# %% Unpack the calculation results

# Merge results from different processes
list_of_conditions = [res[0] for res in all_results]
list_np_HEMATITE = [res[1] for res in all_results]
list_np_MAGNETITE = [res[2] for res in all_results]
list_np_WUSTITE = [res[3] for res in all_results]
list_np_BCC_A2 = [res[4] for res in all_results]
list_np_LIQUID = [res[5] for res in all_results]

print(len(list_of_conditions))

# Flattening the lists
list_of_conditions = [
    item for sublist in list_of_conditions for item in sublist]
list_np_HEMATITE = [item for sublist in list_np_HEMATITE for item in sublist]
list_np_MAGNETITE = [item for sublist in list_np_MAGNETITE for item in sublist]
list_np_WUSTITE = [item for sublist in list_np_WUSTITE for item in sublist]
list_np_BCC_A2 = [item for sublist in list_np_BCC_A2 for item in sublist]
list_np_LIQUID = [item for sublist in list_np_LIQUID for item in sublist]

print(len(list_of_conditions))


# # ====== postprocessing of tc calculation ======
# list_np_FCC_L12_merge = [max(a, b, c) for a, b, c in zip(
#     list_np_FCC_L12, list_np_FCC_L12_1, list_np_FCC_L12_2)]

df = pd.DataFrame(columns=['lnacr_o', 'T', 'np(HEMATITE)',
                  'np(MAGNETITE)', 'np(WUSTITE)', 'np(BCC_A2)', 'np(LIQUID)'])

# Convert conditions and results to DataFrame
df = pd.DataFrame({
    'lnacr_o': [dict(conditions)['lnacr(o)'] for conditions in list_of_conditions],
    'T': [dict(conditions)['T'] for conditions in list_of_conditions],
    'np(HEMATITE)': list_np_HEMATITE,
    'np(MAGNETITE)': list_np_MAGNETITE,
    'np(WUSTITE)': list_np_WUSTITE,
    'np(BCC_A2)': list_np_BCC_A2,
    'np(LIQUID)': list_np_LIQUID
})

df.to_excel(os.path.join(current_directory,
            "tc_full_df_check.xlsx"), index=False)


# %%  plot

# # Plotting

# Filter the dataframe for rows where T is 373.15
filtered_df = df[df['T'] == 473.15]
filtered_df.to_excel(os.path.join(current_directory,
                                  "tc_full_df_check_filter.xlsx"), index=False)

plt.plot(filtered_df['lnacr_o'], filtered_df['np(HEMATITE)'],
         color='blue', label='HEMATITE')
plt.plot(filtered_df['lnacr_o'], filtered_df['np(MAGNETITE)'],
         color='red', label='MAGNETITE')
plt.plot(filtered_df['lnacr_o'], filtered_df['np(BCC_A2)'],
         color='green', label='BCC_A2')

plt.xlabel('LN O activtity')
plt.ylabel('Mole fraction')
plt.grid(True)
# plt.xlim(-100, -25)

plt_output_fname = output_fname + ".png"
plt.savefig(os.path.join(current_directory, plt_output_fname))


# %% ----------------------------------------------------------------

# Extract the first two columns for x and y axes
x = df.iloc[:, 0]
y = df.iloc[:, 1]

# Using a color palette to ensure distinct colors for each scatter plot

plt.figure(figsize=(15, 10))

# Iterate over columns and colors simultaneously using zip

plt.scatter(x, y, c=df.iloc[:, 5], s=50,  alpha=0.6)

plt.xlabel(df.columns[0])
plt.ylabel(df.columns[1])
plt.legend()
plt.title("Scatter Plot of Columns against First Two Columns with Distinct Colors")
plt.grid(True)
plt.show()

# %%
