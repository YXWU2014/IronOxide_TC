# IronOxide_TC

## Updates 2023-10-1

Now in Jupyter Notebook.

I have tried to implement the three types of Gibbs energy assessments: Full Equilibrium, Molar Gibbs Energy, and Driving Force against the gas phase (normalised).

Still need to have another check to ensure the calculations are 100% consistent with Console mode and to determine if we need to try other databases.

- Pressure = 0.5 Pa (5e-6 bar) and only Fe and O
- Plotting as T(K) and ln(Oxygen activity): referenced to the oxygen gas phase at each temperature

## Notebook

- See `IronOxide_TC_calculations.ipynb` for full calculations and visualisations.

## Dependencies

- **tc-python and Thermo-Calc**
- **TCFE**: Using the TCFE11 database for the BCC and Liquid phases.
- **SSUB**: Using the SSUB5 database for the HEMATITE, MAGNETITE, and WUSTITE phases.

## Visuals

#### Full Equilibrium phase diagram as a function of temperature and O activity

<img src="IronOxide_TC_FullEquil.png" width="300"/>
  
#### Gibbs energy of phases as a function of temperature and O activity

![IronOxide_TC_Gm_phases](IronOxide_TC_Gm_phases.png)

<!-- #### Minimum Gibbs energy diagram

<img src="IronOxide_TC_Gmin.png" width="300"/> -->

#### Driving force of phases (against gas phase) as a function of temperature and O activity

![IronOxide_TC_DGM_phases](IronOxide_TC_DGM_phases.png)

#### Maximum Driving Force diagram

<img src="IronOxide_TC_DGMmax.png" width="300"/>
