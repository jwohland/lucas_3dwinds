# Create directory structure and move raw_data into correct directories
cd ../data/JLU

# Remove data outside of 01/1986 - 12/2015
for year in {1979..1985}
do
  rm */*/*${year}010100-*.nc
done


for experiment in EVAL FOREST GRASS
do
  for variable in U V U_10M V_10M FI S S_10M
  do
    # Create directory structure
    mkdir -p ${experiment}/${variable}
  done
done

# EVAL has different directory structure than GRASS and FOREST
# EVAL: variable_name/variable_name*.nc
# FOREST & GRASS: variable_name.nc
# Move all variables out of extra folders for EVAL
mv EVAL/raw_data/*/* EVAL/raw_data/

# Copy data
for experiment in EVAL FOREST GRASS
do
  # doing this explicitly per variable here because wildcards a bit tricky, e.g.,
  # U_10 and U850 both show up using U*
  echo ${experiment}
  for wind_direction in U V
  do
    cp ${experiment}/raw_data/${wind_direction}_10M* ${experiment}/${wind_direction}_10M
    for pressure_level in 925 850 750  # this trows some errors because 925 only in FOREST and GRASS and 750 only in EVAL
    do
      cp ${experiment}/raw_data/${wind_direction}${pressure_level}* ${experiment}/${wind_direction}
    done
  done
  cp ${experiment}/raw_data/FI* ${experiment}/FI
done