from tc_python import *
import time
import json
import numpy as np
import scipy.optimize
import scipy.interpolate
import matplotlib.pyplot as plt

"""
Deriving Diffusion Coefficients from Experiment

This example demonstrates the direct optimization of mobility database parameters by fitting 
to experimentally measured composition profiles. A manual determination of the interdiffusion
coefficients (for example using the Boltzmann-Matano method) is not required. Additionally, 
no derivatives of the experimental curve are required as this is difficult for scattered data.

This example takes several minutes to calculate. The results are updated continually in the 
Results window. The plot example shown is the final iteration.

The example uses data from:
* Rettig, Ralf, Susanne Steuer, and Robert F. Singer. 2011. “Diffusion of Germanium in Binary 
  and Multicomponent Nickel Alloys.” Journal of Phase Equilibria and Diffusion 32 (3): 198–205. 
  doi:10.1007/s11669-011-9853-6.
* Liu, Y.Q., D.J. Ma, and Y. Du. 2010. “Thermodynamic Modeling of the Germanium–nickel System.”
  Journal of Alloys and Compounds 491 (1–2): 63–71. doi:10.1016/j.jallcom.2009.11.036.
"""

# global variables
is_first_iteration = True
lines_ax1 = None
lines_ax2 = None
lines_ax3 = None
all_iterations = []
all_residuals = []


def get_experimental_composition_profile(filename):
    """Reads the JSON composition profile file"""
    data_file_path = os.path.join(os.path.dirname(__file__), filename)
    with open(data_file_path, encoding="utf-8") as json_file:
        data = json.loads(json_file.read())

    exp_profile = {}
    exp_profile["distance"] = np.zeros(len(data["data"]))
    exp_profile["composition_mp"] = np.zeros(len(data["data"]))
    for index, dataset in enumerate(data["data"]):
        exp_profile["distance"][index] = dataset["x"]  # in micrometers
        exp_profile["composition_mp"][index] = dataset["c"]  # in at-%

    # convert to meter and displace grid so that first coordinate is at distance zero
    exp_profile["distance"] /= 1e6
    exp_profile["distance"] -= exp_profile["distance"][0]

    return exp_profile


def residual_composition_profile(x, max_conc):
    """Determines the residual between the experimental composition profile and that calculated with the current
    mobility parameter set.

    The parameter `x` contains the current mobility parameters and as last item the current displacement of the
    concentration profile step.
    """
    diffusion_calc = system.with_isothermal_diffusion_calculation()
    equilibrium_calc = system.with_single_equilibrium_calculation()

    # remove the existing lines so only the latest line is shown
    global is_first_iteration, lines_ax1, lines_ax2, lines_ax3, all_iterations, all_residuals
    if not is_first_iteration:
        lines_ax1.pop(0).remove()
        lines_ax2.pop(0).remove()
        lines_ax3.pop(0).remove()
    is_first_iteration = False

    for index, parameter in enumerate(parameters):
        diffusion_calc.with_system_modifications(
            SystemModifications().set(PhaseParameter(parameter["name"])
                                      .set_expression_with_upper_limit(str(parameter["initial_value"] * x[index]))))
        equilibrium_calc.with_system_modifications(
            SystemModifications().set(PhaseParameter(parameter["name"])
                                      .set_expression_with_upper_limit(str(parameter["initial_value"] * x[index]))))

    # initial concentration profile: step-function with step in the middle of the region
    displacement_initial_profile = x[-1] / 2
    step_at = displacement_initial_profile * width
    diffusion_result = (diffusion_calc
                        .add_region(Region("FCC")
                                    .add_phase("FCC_A1")
                                    .set_width(width)
                                    .with_grid(CalculatedGrid.double_geometric(no_of_points=100,
                                                                               lower_geometrical_factor=0.985,
                                                                               upper_geometrical_factor=1.015))
                                    .with_composition_profile(CompositionProfile(Unit.MOLE_PERCENT)
                                                              .add("Ge", ElementProfile.step(lower_boundary=1e-6,
                                                                                             upper_boundary=max_conc,
                                                                                             step_at=step_at))))
                        .set_temperature(temperature)
                        .set_simulation_time(simulation_time)
                        .calculate())

    # interpolation and calculation of the residuals at each grid point of the experimental profile
    distance, mf_ge = diffusion_result.get_mole_fraction_of_component_at_time("Ge", simulation_time)
    distance = np.array(distance)
    mp_ge = np.array(mf_ge) * 100
    mp_ge_interpolator = scipy.interpolate.interp1d(distance, mp_ge)
    mp_ge_interpolated = mp_ge_interpolator(exp_profile["distance"])

    residuals = mp_ge_interpolated - exp_profile["composition_mp"]
    sum_of_squares = np.sum(residuals ** 2)
    all_iterations.append(len(all_iterations) + 1)
    all_residuals.append(sum_of_squares)

    # calculate how the diffusivity varies
    ge_linspace, D_ge = calculate_diffusivities("Ge", 0, max_conc, 100, temperature, "Ni", equilibrium_calc)
    plt.suptitle("Ge profile in Ni-Ge, x=" + str(x) + ", sum of squares=" + str(sum_of_squares))
    lines_ax1 = ax1.plot(distance * 1e6, np.array(mp_ge), label="Calculated")
    lines_ax2 = ax2.semilogy(ge_linspace, D_ge, label="D_Ge_Ge_Ni")
    lines_ax3 = ax3.semilogy(all_iterations, all_residuals)
    plt.show(block=False)
    plt.pause(1e-13)
    time.sleep(0.2)

    return sum_of_squares


def calculate_diffusivities(element, c_min, c_max, num_points, temperature, dependent_element, calc):
    """Calculates the diffusivities of the element for the specified composition range"""
    (calc
     .disable_global_minimization()
     .set_condition(ThermodynamicQuantity.temperature(), temperature))
    c_linspace = np.linspace(c_min, c_max, num_points, endpoint=True)

    D = []
    for c in c_linspace:
        calc.set_condition(ThermodynamicQuantity.mole_fraction_of_a_component(element), c / 100)
        result = calc.calculate()
        D.append(result.get_value_of("DC(FCC,{},{},{})".format(element, element, dependent_element)))

    return c_linspace, D


if __name__ == "__main__":
    with TCPython() as session:
        data_directory = "data_for_D_06"
        temperature = 1150 + 273.15  # in K
        simulation_time = 10 * 3600  # in s
        max_conc = 13.5  # maximum Ge-concentration in at-%

        exp_profile = get_experimental_composition_profile(os.path.join(data_directory,
                                                                        "NiGe_{}C_10h.json".format(
                                                                            int(temperature - 273.15))))
        width = max(exp_profile["distance"])

        # optimization of the 0-order interaction parameters
        # all other database parameters can be derived from self and tracer diffusion data
        parameters = [{"name": "MQ(FCC_A1&Ni,Ni,Ge:VA;0)"},
                      {"name": "MQ(FCC_A1&Ge,Ge,Ni:VA;0)"}]

        system = (session.select_user_database_and_elements(os.path.join(os.path.dirname(__file__), data_directory,
                                                                         "NiGe_thermo.tdb"), ["Ni", "Ge"])
                  .without_default_phases().select_phase("FCC_A1")
                  .select_user_database_and_elements(os.path.join(os.path.dirname(__file__), data_directory,
                                                                  "NiGe_mob.tdb"), ["Ni", "Ge"])
                  .without_default_phases().select_phase("FCC_A1")
                  .get_system())

        # reading out the initial settings of the mobility parameters
        for parameter in parameters:
            parameter["database_parameter"] = (system.with_single_equilibrium_calculation()
                                               .get_system_data()
                                               .get_phase_parameter(parameter["name"]))
            expression = parameter["database_parameter"].get_intervals()[0].get_expression()
            parameter["lambda_function"] = lambda T: eval(expression)
            parameter["initial_value"] = parameter["lambda_function"](temperature)

        # setting up the plot (that will be dynamically updated)
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(7, 11))
        ax1.plot(exp_profile["distance"] * 1e6, exp_profile["composition_mp"], linestyle="None", marker="o",
                 label="Experimental")

        ax1.set_xlabel(u"Distance [\u03BCm]")
        ax1.set_ylabel("Ge-content [at-%]")

        ax2.set_xlabel("Ge [at-%]")
        ax2.set_ylabel("D_Ge_Ge_Ni [m**2/s]")
        ax2.set_ylim((pow(10, -14), pow(10, -11)))

        ax3.set_xlabel("Iteration")
        ax3.set_ylabel("Residual")

        # perform the mobility parameter optimization
        x0 = np.ones(len(parameters) + 1)  # initial displacement of step-profile is the last parameter to vary
        xopt = scipy.optimize.minimize(fun=residual_composition_profile, x0=x0, args=max_conc, method="Nelder-Mead",
                                       tol=1e-3, options={"disp": True})
        plt.show()

        # print the optimal result
        for index, parameter in enumerate(parameters):
            print("Optimal value for parameter {} = {}".format(parameter["name"],
                                                               parameter["initial_value"] * xopt["x"][index]))
