# log into Juelich cluster
juelich

# copy OUR wind data, needs password confirmation
# EVAL
scp -pr /home/jwohland/fpslucas/PHASE1/EVAL/EUR-44/OUR/ERAINT/evaluation/*/*/*/3hr/ua g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/OUR/EVAL
scp -pr /home/jwohland/fpslucas/PHASE1/EVAL/EUR-44/OUR/ERAINT/evaluation/*/*/*/3hr/va g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/OUR/EVAL
# GRASS
scp -pr /home/jwohland/fpslucas/PHASE1/GRASS/EUR-44/OUR/ERAINT/evaluation/*/*/*/3hr/ua g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/OUR/GRASS
scp -pr /home/jwohland/fpslucas/PHASE1/GRASS/EUR-44/OUR/ERAINT/evaluation/*/*/*/3hr/va g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/OUR/GRASS
# FOREST
scp -pr /home/jwohland/fpslucas/PHASE1/FOREST/EUR-44/OUR/ERAINT/evaluation/*/*/*/3hr/ua g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/OUR/FOREST
scp -pr /home/jwohland/fpslucas/PHASE1/FOREST/EUR-44/OUR/ERAINT/evaluation/*/*/*/3hr/va g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/OUR/FOREST