# Oxide_TC

just implemented to map the full equilibrium regimes as a function of temperature and O activity

- Pressure = 0.5Pa (5e-6 bar) and only Fe and O
- plotting as T(K) and ln(Oxygen activity): referenced to the Oxygen gas at each temperature
- (we can update the choice of databse later)

## Notebook

- see `Oxide_TC_calculation.ipynb` for full calculation and visualisations.

## Dependencies

- **tc-python and Thermo-Calc**
- **TCFE**: using the TCFE11 database for the BCC and Liquid phases.
- **SSUB**: Using the SSUB5 database for the HEMATITE, MAGNETITE, and WUSTITE phases.

## Visuals

#### Full Equilibrium phase diagram as a function of temperature and O activity

<img src="Oxide_TC_FullEquil.png" width="300"/>
  
#### Gibbs energy of phases as a function of temperature and O activity

![Oxide_TC_Gm_phases](Oxide_TC_Gm_phases.png)

<!-- #### minimum Gibbs energy diagram

<img src="Oxide_TC_Gmin.png" width="300"/> -->

#### Driving force of phases (against gas) as a function of temperature and O activity

![Oxide_TC_dgm_phases](Oxide_TC_dgm_phases.png)

#### Maximum Driving force diagram

<img src="Oxide_TC_DGMmax.png" width="300"/>
