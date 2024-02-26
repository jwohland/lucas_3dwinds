# Overview and sequencing of scripts


# Preprocessing per model
bash preprocess_ETH.sh
python preprocess_ETH.py

bash preprocess_GERICS.sh
python preprocess_GERICS.py

python preprocess_OUR.py

bash preprocess_IDL.sh
python preprocess_IDL.py

bash preprocess_JLU.sh

python preprocess_BCCR.py

# Compute monthly aggregates
python compute_monthly_winds.py
python compute_sub-daily_focusareas.py

# Analysis
python analyze_monthly_means.py
python analyze_subdaily.py
python analyze_summernights_IDL.py

# Compute hub height winds
python compute_hub_height.py
# Compute power generation
python compute_power.py

# Evaluation power generation
python analyze_generation.py