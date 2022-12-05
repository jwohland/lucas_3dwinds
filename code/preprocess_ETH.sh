# Manual steps preceding this script
# 1) Copy data from Edouard to cluster
# 2) in data/ETH/XXXX/ rename COSMO_CLM2_EU-CORDEX_XXXX_191019/ to raw_data/ where XXXX is EVAL, FOREST or GRASS
# 3) in raw_data directories, delete years prior to 1986 and delete empty directories temp_year where year in 1999 - 2010


# todo loop over experiments
# Unzip remaining years, only extracting relevant data
# todo loop over years
cd /net/xenon/climphys/jwohland/lucas_3dwinds/data/ETH/EVAL/
tar -xvzf ./raw_data/1999.tar ./1999/output/6hr/
tar -xvzf ./raw_data/1999.tar ./1999/output/3D/
mv 1999/output/* 1999
rm -r 1999/output

#combine all timesteps in a year
cdo copy 1999/6hr/*.nc 1999/6hr_1999.nc
cdo copy 1999/3D/*.nc 1999/3D_1999.nc

# create directory structure with one variable per folder
mkdir -p U_10M V_10M FI T U V RELHUM

#choose variables from 6hr and store in separate files
cdo selvar,U_10M 1999/6hr_1999.nc U10M/U10M_1999.nc
cdo selvar,V_10M 1999/6hr_1999.nc V10M/V10M_1999.nc

#choose variables from 3D and store in separate files
cdo sellevel,92500,85000 -selvar,FI 1999/3D_1999.nc FI/FI_1999.nc
cdo sellevel,92500,85000 -selvar,T 1999/3D_1999.nc T/T_1999.nc
cdo sellevel,92500,85000 -selvar,U 1999/3D_1999.nc U/U_1999.nc
cdo sellevel,92500,85000 -selvar,V 1999/3D_1999.nc V/V_1999.nc
cdo sellevel,92500,85000 -selvar,RELHUM 1999/3D_1999.nc RELHUM/RELHUM_1999.nc

#cleanup
rm -r 1999
