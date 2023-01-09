# Manual steps preceding this script
# 1) Copy data from Edouard to cluster
# 2) in data/ETH/XXXX/ rename COSMO_CLM2_EU-CORDEX_XXXX_191019/ to raw_data/ where XXXX is EVAL, FOREST or GRASS
# 3) in raw_data directories, delete years prior to 1986 and delete empty directories temp_year where year in ${year} - 2010
# 4) delete 2015_old.tar

# loop over experiments
for experiment in EVAL FOREST GRASS
do
  echo $experiment
  # Unzip remaining years, only extracting relevant data
  # loop over years
  for year in {1986..2015}
  do
    echo $year
  
    cd /net/xenon/climphys/jwohland/projects/lucas_3dwinds/data/ETH/${experiment}/
    tar -xzf ./raw_data/${year}.tar ./${year}/output/6hr/
    tar -xzf ./raw_data/${year}.tar ./${year}/output/3D/
    mv ${year}/output/* ${year}
    rm -r ${year}/output
    
    #combine all timesteps in a year
    cdo copy ${year}/6hr/*.nc ${year}/6hr_${year}.nc
    cdo copy ${year}/3D/*.nc ${year}/3D_${year}.nc
    
    # create directory structure with one variable per folder
    mkdir -p U_10M V_10M FI T U V RELHUM
    
    #choose variables from 6hr and store in separate files
    cdo selvar,U_10M ${year}/6hr_${year}.nc U10M/U10M_${year}.nc
    cdo selvar,V_10M ${year}/6hr_${year}.nc V10M/V10M_${year}.nc
    
    #choose variables from 3D and store in separate files
    cdo sellevel,92500,85000 -selvar,FI ${year}/3D_${year}.nc FI/FI_${year}.nc
    cdo sellevel,92500,85000 -selvar,T ${year}/3D_${year}.nc T/T_${year}.nc
    cdo sellevel,92500,85000 -selvar,U ${year}/3D_${year}.nc U/U_${year}.nc
    cdo sellevel,92500,85000 -selvar,V ${year}/3D_${year}.nc V/V_${year}.nc
    cdo sellevel,92500,85000 -selvar,RELHUM ${year}/3D_${year}.nc RELHUM/RELHUM_${year}.nc
    
    #cleanup
    rm -r ${year}
  done
done