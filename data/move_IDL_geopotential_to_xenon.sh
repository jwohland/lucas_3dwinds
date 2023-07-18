# The following retrieves the IDL geopotential data for the FOREST and GRASS simulations from the juelich server and copies to ETH servers
# Log in to juelich server and then execute the following

# copy IDL geopotential height
# GRASS
scp -pr /home/jwohland/fpslucas/PHASE1/GRASS/EUR-44/IDL/ERAINT/evaluation/*/*/*/1hr/zg jwohland@fog.ethz.ch:/net/xenon/climphys/jwohland/projects/lucas_3dwinds/data/IDL/GRASS
# FOREST
scp -pr /home/jwohland/fpslucas/PHASE1/FOREST/EUR-44/IDL/ERAINT/evaluation/*/*/*/1hr/zg jwohland@fog.ethz.ch:/net/xenon/climphys/jwohland/projects/lucas_3dwinds/data/IDL/FOREST
