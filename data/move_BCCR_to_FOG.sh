# Move BCCR data from Juelich server to ETH FOG cluster and then extract from .tar archives

for experiment in EVAL FOREST GRASS
do
  target_dir=../data/BCCR/${experiment}/raw_data
  for variable in ua va zg
  do
    echo ${variable}
    # retrieve data
    scp jwohland@juelich:/home/jwohland/fpslucas/PHASE1/${experiment}/EUR-44/BCCR/ERAINT/evaluation/BCCR-WRFV381/v1/r1i1p1/1hr/${variable}*.tar $target_dir
    # extract data
    tar -xvf ${target_dir}/*.tar
    rm ${target_dir}/*.tar
  done
done