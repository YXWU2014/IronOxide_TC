from matplotlib.ticker import ScalarFormatter
import matplotlib.pyplot as plt
import os
from matplotlib.patches import Rectangle


def plot_phases(phases_list, df_Gmin, func, labels_list,
                colormaps, use_defined_range, cbar_label, title,
                xlim, ylim, alpha, s_base, s_highlight,
                save_plot, current_directory, output_fname, plt_output_fname):
    # Create a new figure with subplots
    fig, axs = plt.subplots(nrows=1, ncols=len(phases_list), figsize=(
        3.1 * len(phases_list), 3), sharex=True, sharey=True)

    for i, phase in enumerate(phases_list):
        cmap, vmin, vmax = colormaps[phase]

        if use_defined_range:
            sc = axs[i].scatter(df_Gmin['lnacr_o'], df_Gmin['T']-273.15,
                                c=df_Gmin[f'{func}({phase})'], label=f'{labels_list[i]}',
                                cmap=cmap, s=s_base, alpha=alpha, vmin=vmin, vmax=vmax)
        else:
            sc = axs[i].scatter(df_Gmin['lnacr_o'], df_Gmin['T']-273.15,
                                c=df_Gmin[f'{func}({phase})'], label=f'{labels_list[i]}',
                                cmap=cmap, s=s_base, alpha=alpha)
        axs[i].scatter([-7.9663978], [300],
                       facecolors='white', edgecolors='black', linewidths=1, s=s_highlight)
        axs[i].scatter([-59.5], [300],
                       facecolors='white', edgecolors='black', linewidths=1, s=s_highlight)

        cbar = plt.colorbar(sc, ax=axs[i])

        # Change colorbar numbering to scientific notation
        formatter = ScalarFormatter(useMathText=True)
        formatter.set_scientific(True)
        formatter.set_powerlimits((-1, 1))
        cbar.ax.yaxis.set_major_formatter(formatter)

        # Label the colorbar of the last plot only
        if i == len(phases_list) - 1:
            cbar.set_label(cbar_label, fontsize=14)
        # if i == 0:
        #     axs[i].set_ylabel(r'T ($^\circ$C)', fontsize=14)

        # Overall x and y labels
        fig.suptitle(title, fontsize=14, fontweight='normal', y=0.9)

        fig.text(0.5, -0.02, 'Natural log of oxygen activity',
                 ha='center', fontsize=14,  fontweight='normal')
        fig.text(-0.0, 0.5, r'T ($^\circ$C)', va='center',
                 rotation='vertical', fontsize=14,  fontweight='normal')

        # Adjust layout to make room for overall x and y labels
        plt.tight_layout(rect=[0.01, 0.02, 1, 1])

        # axs[i].set_xlabel('Natural log of oxygen activity', fontsize=14)
        axs[i].set_xlim(xlim[0], xlim[1])
        axs[i].set_ylim(ylim[0], ylim[1])
        axs[i].set_xticks(range(xlim[0], xlim[1]+1, xlim[2]))
        axs[i].set_yticks(range(ylim[0], ylim[1]+1, ylim[2]))
        axs[i].grid(True, which='both', linestyle='--', linewidth=0.5)
        # axs[i].set_title(f'{labels_list[i]}')
        axs[i].legend(scatterpoints=0, handlelength=0, fontsize=14, loc='upper left',
                      facecolor='white', edgecolor='black', framealpha=0.8)
        axs[i].set_box_aspect(1)

        # Define coordinates and dimensions of the rectangle
        rect_x, rect_y = -10, 250
        rect_width, rect_height = 5, 100
        rect = Rectangle((rect_x, rect_y), rect_width, rect_height,
                         linewidth=1, edgecolor='firebrick', facecolor='none')
        axs[i].add_patch(rect)

        rect_x, rect_y = -60, 250
        rect_width, rect_height = 5, 100
        rect = Rectangle((rect_x, rect_y), rect_width, rect_height,
                         linewidth=1, edgecolor='navy', facecolor='none')
        axs[i].add_patch(rect)

    plt.tight_layout()
    if save_plot:
        # plt_output_fname = "_Gm_phases.png"
        plt.savefig(os.path.join(current_directory, output_fname + plt_output_fname),
                    format='png', dpi=300, bbox_inches='tight')
    plt.show()

# -------------------------------------------------------------------------


def plot_phases_crop(phases_list, df_Gmin, func, labels_list,
                     colormaps, use_defined_range, cbar_label, title,
                     xlim, ylim, alpha, s_base, s_highlight,
                     save_plot, current_directory, output_fname, plt_output_fname):
    # Create a new figure with subplots
    fig, axs = plt.subplots(nrows=1, ncols=len(phases_list), figsize=(
        3.1 * len(phases_list), 3), sharex=True, sharey=True)

    for i, phase in enumerate(phases_list):
        cmap, vmin, vmax = colormaps[phase]

        if use_defined_range:
            sc = axs[i].scatter(df_Gmin['lnacr_o'], df_Gmin['T']-273.15,
                                c=df_Gmin[f'{func}({phase})'], label=f'{labels_list[i]}',
                                cmap=cmap, s=s_base, alpha=alpha, vmin=vmin, vmax=vmax)
        else:
            sc = axs[i].scatter(df_Gmin['lnacr_o'], df_Gmin['T']-273.15,
                                c=df_Gmin[f'{func}({phase})'], label=f'{labels_list[i]}',
                                cmap=cmap, s=s_base, alpha=alpha)
        axs[i].scatter([-7.9663978], [300],
                       facecolors='white', edgecolors='black', linewidths=1, s=s_highlight)
        axs[i].scatter([-59.9], [300],
                       facecolors='white', edgecolors='black', linewidths=1, s=s_highlight)

        cbar = plt.colorbar(sc, ax=axs[i])

        # # Change colorbar numbering to scientific notation
        # formatter = ScalarFormatter(useMathText=True)
        # formatter.set_scientific(True)
        # formatter.set_powerlimits((-1, 1))
        # cbar.ax.yaxis.set_major_formatter(formatter)

        # Label the colorbar of the last plot only
        if i == len(phases_list) - 1:
            cbar.set_label(cbar_label, fontsize=14)
        # if i == 0:
        #     axs[i].set_ylabel(r'T ($^\circ$C)', fontsize=14)
        # if i == 1:
        #     axs[i].set_xlabel('Natural log of oxygen activity', fontsize=14)

        # Overall x and y labels
        fig.suptitle(title, fontsize=14, fontweight='normal', y=0.9)

        fig.text(0.5, -0.02, 'Natural log of oxygen activity',
                 ha='center', fontsize=14,  fontweight='normal')
        fig.text(-0.02, 0.5, r'T ($^\circ$C)', va='center',
                 rotation='vertical', fontsize=14,  fontweight='normal')

        # Adjust layout to make room for overall x and y labels
        plt.tight_layout(rect=[0.05, 0.08, 1, 1])

        axs[i].set_xlim(xlim[0], xlim[1])
        axs[i].set_ylim(ylim[0], ylim[1])
        axs[i].set_xticks(range(xlim[0], xlim[1]+1, xlim[2]))
        axs[i].set_yticks(range(ylim[0], ylim[1]+1, ylim[2]))
        axs[i].grid(True, which='both', linestyle='--', linewidth=0.5)
        # axs[i].set_title(f'{labels_list[i]}')
        axs[i].legend(scatterpoints=0, handlelength=0, fontsize=14, loc='upper left',
                      facecolor='white', edgecolor='black', framealpha=0.8)
        axs[i].set_box_aspect(1)

    plt.tight_layout()
    if save_plot:
        # plt_output_fname = "_Gm_phases.png"
        plt.savefig(os.path.join(current_directory, output_fname + plt_output_fname),
                    format='png', dpi=300, bbox_inches='tight')
    plt.show()
