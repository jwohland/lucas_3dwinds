# log into Juelich cluster
juelich

# copy IDL wind data, needs password confirmation
# EVAL
scp -pr /home/jwohland/fpslucas/PHASE1/EVAL/EUR-44/IDL/ERAINT/evaluation/*/*/*/1hr/ua g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/IDL/EVAL
scp -pr /home/jwohland/fpslucas/PHASE1/EVAL/EUR-44/IDL/ERAINT/evaluation/*/*/*/1hr/va g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/IDL/EVAL
# GRASS
scp -pr /home/jwohland/fpslucas/PHASE1/GRASS/EUR-44/IDL/ERAINT/evaluation/*/*/*/1hr/ua g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/IDL/GRASS
scp -pr /home/jwohland/fpslucas/PHASE1/GRASS/EUR-44/IDL/ERAINT/evaluation/*/*/*/1hr/va g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/IDL/GRASS
# FOREST
scp -pr /home/jwohland/fpslucas/PHASE1/FOREST/EUR-44/IDL/ERAINT/evaluation/*/*/*/1hr/ua g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/IDL/FOREST
scp -pr /home/jwohland/fpslucas/PHASE1/FOREST/EUR-44/IDL/ERAINT/evaluation/*/*/*/1hr/va g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/IDL/FOREST

# copy IDL geopotential height
# EVAL
scp -pr /home/jwohland/fpslucas/PHASE1/EVAL/EUR-44/IDL/ERAINT/evaluation/*/*/*/1hr/zg g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/IDL/EVAL
scp -pr /home/jwohland/fpslucas/PHASE1/EVAL/EUR-44/IDL/ERAINT/evaluation/*/*/*/1hr/zg g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/IDL/EVAL
# GRASS
scp -pr /home/jwohland/fpslucas/PHASE1/GRASS/EUR-44/IDL/ERAINT/evaluation/*/*/*/1hr/zg g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/IDL/GRASS
scp -pr /home/jwohland/fpslucas/PHASE1/GRASS/EUR-44/IDL/ERAINT/evaluation/*/*/*/1hr/zg g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/IDL/GRASS
# FOREST
scp -pr /home/jwohland/fpslucas/PHASE1/FOREST/EUR-44/IDL/ERAINT/evaluation/*/*/*/1hr/zg g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/IDL/FOREST
scp -pr /home/jwohland/fpslucas/PHASE1/FOREST/EUR-44/IDL/ERAINT/evaluation/*/*/*/1hr/zg g300106@levante.dkrz.de:/work/ch0636/g300106/projects/lucas_3dwinds/data/IDL/FOREST
