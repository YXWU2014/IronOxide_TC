# %% ===== Thermocalc calculation =====

from tc_python import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
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
        k = 250
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
start_time = time.time()

tk_values = np.arange(100+273.15, 1400+273.15, 10)
print("temperature range: ", tk_values)
with Pool(processes=16) as pool:
    all_results = pool.map(tc_calculation, tk_values)

elapsed_time = time.time() - start_time
print("Time taken: ", int(elapsed_time), "seconds")

# print(len(all_results[0]))

# %% ===== Unpack the calculation results and save into excel =====

# Merge results from different processes
list_of_conditions = [res[0] for res in all_results]
list_np_HEMATITE = [res[1] for res in all_results]
list_np_MAGNETITE = [res[2] for res in all_results]
list_np_WUSTITE = [res[3] for res in all_results]
list_np_BCC_A2 = [res[4] for res in all_results]
list_np_LIQUID = [res[5] for res in all_results]

# print(len(list_of_conditions))

# Flattening the lists
list_of_conditions = [
    item for sublist in list_of_conditions for item in sublist]
list_np_HEMATITE = [item for sublist in list_np_HEMATITE for item in sublist]
list_np_MAGNETITE = [item for sublist in list_np_MAGNETITE for item in sublist]
list_np_WUSTITE = [item for sublist in list_np_WUSTITE for item in sublist]
list_np_BCC_A2 = [item for sublist in list_np_BCC_A2 for item in sublist]
list_np_LIQUID = [item for sublist in list_np_LIQUID for item in sublist]

# print(len(list_of_conditions))

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


# %% ===== Choose one temperature to check before mapping =====

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


# %% ===== check mapping for one phase =====

plt.figure(figsize=(6, 6))
plt.scatter(df['lnacr_o'], df['T'], c=df['np(HEMATITE)'], s=5,  alpha=0.6)
plt.xlabel(df.columns[0])
plt.ylabel(df.columns[1])
plt.grid(True)
plt.show()

# %% ===== Organise all phases into the same plot =====

# Splitting the main dataframe into individual dataframes and filtering them
df_HEMATITE = df[['lnacr_o', 'T', 'np(HEMATITE)']]
df_HEMATITE = df_HEMATITE[df_HEMATITE['np(HEMATITE)'] >= 0.001]

df_MAGNETITE = df[['lnacr_o', 'T', 'np(MAGNETITE)']]
df_MAGNETITE = df_MAGNETITE[df_MAGNETITE['np(MAGNETITE)'] >= 0.001]

df_WUSTITE = df[['lnacr_o', 'T', 'np(WUSTITE)']]
df_WUSTITE = df_WUSTITE[df_WUSTITE['np(WUSTITE)'] >= 0.001]

df_BCC_A2 = df[['lnacr_o', 'T', 'np(BCC_A2)']]
df_BCC_A2 = df_BCC_A2[df_BCC_A2['np(BCC_A2)'] >= 0.001]

df_LIQUID = df[['lnacr_o', 'T', 'np(LIQUID)']]
df_LIQUID = df_LIQUID[df_LIQUID['np(LIQUID)'] >= 0.001]

# Plotting the individual dataframes
plt.figure(figsize=(5, 5))
colors = {
    'HEMATITE': '#377eb8',
    'MAGNETITE': '#ff7f00',
    'WUSTITE': '#4daf4a',
    'BCC_A2': '#f781bf',
    'LIQUID': '#a65628'
}

plt.scatter(df_HEMATITE['lnacr_o'], df_HEMATITE['T'], s=10,
            label='HEMATITE', color=colors['HEMATITE'], alpha=0.5)

plt.scatter(df_MAGNETITE['lnacr_o'], df_MAGNETITE['T'], s=10,
            label='MAGNETITE', color=colors['MAGNETITE'], alpha=0.5)

plt.scatter(df_WUSTITE['lnacr_o'], df_WUSTITE['T'], s=10,
            label='WUSTITE', color=colors['WUSTITE'], alpha=0.5)

plt.scatter(df_BCC_A2['lnacr_o'], df_BCC_A2['T'], s=10,
            label='BCC_A2', color=colors['BCC_A2'], alpha=0.5)

plt.scatter(df_LIQUID['lnacr_o'], df_LIQUID['T'], s=10,
            label='LIQUID', color=colors['LIQUID'], alpha=0.5)

plt.xlabel('LN O activtity', fontsize=14)
plt.ylabel('T (K)', fontsize=14)
plt.title('full equilibrium', fontsize=14)
plt.legend(fontsize=12, loc='upper left')
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.grid(True)
plt.tight_layout()

plt_output_fname = output_fname + ".png"
plt.savefig(os.path.join(current_directory, plt_output_fname))

plt.show()

# %%
