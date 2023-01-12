# Splitting large e*.nc files per variable and only keep relevant ones.
# This .sh script needs to be executed before the preprocess_GERICS.py script

# Manual steps required before executing this script
# 1) Rename experiments following:
#   "grass": "062008",
#   "forest": "062009",
#   "eval": "062010"

# loop over experiments
for experiment in EVAL FOREST GRASS
do
  echo $experiment
  cd /net/xenon/climphys/jwohland/projects/lucas_3dwinds/data/GERICS/${experiment}/
  # create directory structure with one variable per folder
  mkdir -p FIB T U V PS FI FI_interpolated S

  for year in {1986..2015}
  do
    echo $year
    mkdir ${year}

    #combine all timesteps in a year
    cdo copy raw_data/*t${year}*.nc ${year}/data_${year}.nc

    # Split variables and store in separate folders. Level selection is later performed in the python script
    for variable in FIB T U V PS FI
    do
      cdo selvar,${variable} ${year}/data_${year}.nc ${variable}/${variable}_${year}.nc
    done

    #cleanup
    rm -r ${year}
  done
done