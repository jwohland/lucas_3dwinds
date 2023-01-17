# Spatial extent of IDL grid. Most other grids have additional area outside this box which
# should be removed as only available in subset of models.
# Values are taken from computation in notebooks/5_horizontal_grids.ipynb
horizontal_ranges = {
    "rlons": slice(-28.21, 17.99),
    "rlats": slice(-23.21, 21.67)
}

EXPERIMENTS = ["GRASS", "FOREST", "EVAL"]
