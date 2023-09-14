import json
import sys
try:
    import xmltodict
except ImportError:
    sys.stderr.write("The package `xmltodict` is not installed, please run `pip / pip3 install xmltodict`, this is not "
                     "possible with the Python bundled to Thermo-Calc")
    sys.exit(-1)
try:
    import yaml
except ImportError:
    sys.stderr.write("The package `pyyaml` is not installed, please run `pip / pip3 install pyyaml`, this is not "
                     "possible with the Python bundled to Thermo-Calc")
    sys.exit(-1)
try:
    from h5py import File
except ImportError:
    sys.stderr.write("The package `h5py` is not installed, please run `pip /pip3 install h5py`, this is not possible "
                     "with the Python bundled to Thermo-Calc")
    sys.exit(-1)
try:
    import pandas as pd
except ImportError:
    sys.stderr.write("The package `pandas` is not installed, please run `pip / pip3 install pandas`, this is not "
                     "possible with the Python bundled to Thermo-Calc")
    sys.exit(-1)
from tc_python import *

"""
This example shows how to create a property (step) diagram using TC-Python.
The alloy system Fe-Ni is used as an example.

The result is then saved in different file formats: 
    * JSON
    * XML
    * CSV
    * TXT
    * HDF5 

Note: Requires the packages h5py, pandas and lxml (install with `pip / pip3 install h5py pandas lxml`)
"""

database = "FEDEMO"
dependent_element = "Fe"
composition = {"Ni": 10.0}  # in wt-%

with TCPython() as start:
    start.set_cache_folder(os.path.basename(__file__) + "_cache")
    calculation = (
        start
            .select_database_and_elements(database, [dependent_element] + list(composition.keys()))
            .get_system()
            .with_property_diagram_calculation()
            .with_axis(CalculationAxis(ThermodynamicQuantity.temperature())
                       .set_min(500)
                       .set_max(3000)
                       )
            .set_condition(ThermodynamicQuantity.mass_fraction_of_a_component("Ni"), composition["Ni"] / 100)
    )

    property_diagram = calculation.calculate()
    property_diagram.set_phase_name_style(PhaseNameStyle.ALL)
    groups = \
        property_diagram.get_values_grouped_by_quantity_of(ThermodynamicQuantity.temperature(),
                                                           ThermodynamicQuantity.volume_fraction_of_a_phase(ALL_PHASES))

# to `*.json`
property_diagram_dict = {}
property_diagram_dict['title'] = 'Property diagram Fe-Ni'
property_diagram_dict['x-axis'] = 'T [K]'
property_diagram_dict['y-axis'] = 'Volume fraction of phases'
property_diagram_dict['lines'] = []

for group in groups.values():
    property_diagram_dict['lines'].append({'label': group.label, 'x': group.x, 'y': group.y})

with open(r"property_diagram.json", 'w') as outfile:
    json.dump(property_diagram_dict, outfile, indent=2, sort_keys=True)

# to `*.txt`
with open(r"property_diagram.txt", "w") as txt_file:
    for group in groups.values():
        txt_file.write(group.label + os.linesep)
        for i in range(0, len(group.x)):
            txt_file.write(str(group.x[i]) + "," + str(group.y[i]) + os.linesep)

# to `*.xml`
with open(r"property_diagram.xml", "w") as xml_file:
    xml_file.write(xmltodict.unparse({"data": property_diagram_dict}, pretty=True))

# to `*.yaml`
with open(r"property_diagram.yaml", "w") as file:
    file.write(yaml.dump(property_diagram_dict))

# to `*.HDF5`
with File(r"property_diagram.hdf5", "w") as f:
    f.attrs["database"] = database
    f.attrs["dependentElement"] = dependent_element
    composition_group = f.create_group("composition")
    composition_group["elements"] = [n.encode("ascii", "ignore") for n in composition.keys()]
    composition_group.create_dataset("concentration", shape=(len(composition),))
    for index, element in enumerate(list(composition_group["elements"])):
        composition_group["concentration"][index] = composition[element.decode("ascii")]
    composition_group["concentration"].attrs["unit"] = "weightPercent"

    for group in groups.values():
        phase_group = f.create_group(group.label)
        phase_group["T"] = group.x
        phase_group["T"].attrs["unit"] = "Kelvin"
        phase_group["fraction"] = group.y
        phase_group["fraction"].attrs["Unit"] = "volume fraction"

# to `*.CSV`
# note: due to the differing temperature axis range for each phase we choose here only one phase
group_label = next(iter(groups))  # taking one item from the dict
series = pd.Series(groups[group_label].y, index=groups[group_label].x)
series.index.name = "T/K"

df = pd.DataFrame({group_label: series})
df.index.name = "T/K"
df.to_csv(r"property_diagram.csv")
