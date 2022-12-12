
# Remove data outside of 01/1986 - 12/2015
cd ../data/IDL
for year in {1979..1985}
do
  rm */*/*${year}010100-*.nc
done