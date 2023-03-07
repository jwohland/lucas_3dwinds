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

