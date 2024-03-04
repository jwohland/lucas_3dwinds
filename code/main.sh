# Overview and sequencing of scripts

###############
# Preprocessing
###############
bash preprocess_GERICS.sh
python preprocess_GERICS.py
bash preprocess_IDL.sh
python preprocess_IDL.py

###############
# Computation
###############
python compute_approximate_heights.py  # Approximate  heights per model level
python compute_monthly_winds.py  # monthly aggregates
python compute_sub-daily_focusareas.py  # sub-daily in focus areas
python compute_hub_height.py  # hub height winds
python compute_power.py  # power generation

###############
# Analysis / Plotting
###############
python analyze_monthly_means.py  # Mean wind changes
python analyze_subdaily.py  # Daily cycle
python analyze_summernights_IDL.py  # Summernights / Jet in IDL
python analyze_generation.py  # power generation