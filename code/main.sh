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

# Analysis
