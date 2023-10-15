from matplotlib.ticker import ScalarFormatter
import matplotlib.pyplot as plt
import os


def plot_phases(phases_list, df_Gmin, func, labels_list,
                colormaps, use_defined_range, cbar_label,
                save_plot, current_directory, output_fname, plt_output_fname):
    # Create a new figure with subplots
    fig, axs = plt.subplots(nrows=1, ncols=len(phases_list), figsize=(
        3.1 * len(phases_list), 3), sharex=True, sharey=True)

    for i, phase in enumerate(phases_list):
        cmap, vmin, vmax = colormaps[phase]

        if use_defined_range:
            sc = axs[i].scatter(df_Gmin['lnacr_o'], df_Gmin['T']-273.15,
                                c=df_Gmin[f'{func}({phase})'],
                                cmap=cmap, s=5, alpha=0.6, vmin=vmin, vmax=vmax)
            axs[i].scatter([-7.9663978], [300], color='white')
        else:
            sc = axs[i].scatter(df_Gmin['lnacr_o'], df_Gmin['T']-273.15,
                                c=df_Gmin[f'{func}({phase})'],
                                cmap=cmap, s=5, alpha=0.6)
            axs[i].scatter([-7.9663978], [300], color='white')

        cbar = plt.colorbar(sc, ax=axs[i])

        # Change colorbar numbering to scientific notation
        formatter = ScalarFormatter(useMathText=True)
        formatter.set_scientific(True)
        formatter.set_powerlimits((-1, 1))
        cbar.ax.yaxis.set_major_formatter(formatter)

        # Label the colorbar of the last plot only
        if i == len(phases_list) - 1:
            cbar.set_label(cbar_label, fontsize=14)
        if i == 0:
            axs[i].set_ylabel(r'T ($^\circ$C)', fontsize=14)

        axs[i].set_xlabel('Natural log of oxygen activity', fontsize=14)
        axs[i].set_xlim(-60, -5)
        axs[i].set_ylim(200, 600)
        axs[i].set_xticks(range(-60, -5, 10))
        axs[i].set_yticks(range(200, 601, 100))
        axs[i].grid(True, which='both', linestyle='--', linewidth=0.5)
        axs[i].set_title(f'{labels_list[i]}')
        axs[i].set_aspect('auto', 'box')

    plt.tight_layout()
    if save_plot:
        # plt_output_fname = "_Gm_phases.png"
        plt.savefig(os.path.join(current_directory, output_fname + plt_output_fname),
                    format='png', dpi=300, bbox_inches='tight')
    plt.show()
