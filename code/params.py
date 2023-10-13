# Spatial extent of IDL grid. Most other grids have additional area outside this box which
# should be removed as only available in subset of models.
# Values are taken from computation in notebooks/05_horizontal_grids.ipynb
import yaml
import sys

sys.path.append(".")

horizontal_ranges = {"rlons": slice(-28.21, 17.99), "rlats": slice(-23.21, 21.67)}

EXPERIMENTS = ["GRASS", "FOREST", "EVAL"]

# simple approximate mapping from model levels and/or pressure levels to meters above ground
with open("../code/approximate_heights.yaml", mode="r") as file:
    approximate_heights = yaml.safe_load(file)

# Roughness lenghts from Breil et al. "The Opposing Effects of Reforestation and
# Afforestation on the Diurnal Temperature Cycle at the Surface and in the Lowest
# Atmospheric Model Level in the European Summer, Journal of Climate, 2019, Table 1
roughness_dict = {}
for institution in ["IDL", "JLU", "ETH", "GERICS"]:
    roughness_dict[institution] = {}
roughness_dict["IDL"]["NET"] = 1.09
roughness_dict["IDL"]["BDT"] = 0.8
roughness_dict["IDL"]["C3"] = 0.12

roughness_dict["JLU"]["NET"] = 1
roughness_dict["JLU"]["BDT"] = 1
roughness_dict["JLU"]["C3"] = 0.03

roughness_dict["ETH"]["NET"] = 0.7
roughness_dict["ETH"]["BDT"] = 0.83
roughness_dict["ETH"]["C3"] = 0.048

# The GERICS roughness lengths can not be directly compared to the ones from the other models
# because GERICS computes effective roughness as a combination of the land-use roughness
# and roughness due to sub-grid scale orography. Instead of the Breil et al. values, we therefore
# use the effective roughness lengths.
# Since we only have the effective roughness in the FOREST simulations (without distinction between
# NET and BDT, we assume that both are identical. In the rest of the analysis, the effective
# roughness is computed as 0.5 * ( NET + BDT ), which then ends up being correct.
# Computation of those values is documented in code/compute_effective_roughness_GERICS.py
roughness_dict["GERICS"]["NET"] = 1.686
roughness_dict["GERICS"]["BDT"] = 1.686
roughness_dict["GERICS"]["C3"] = 0.693
