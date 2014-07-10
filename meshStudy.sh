#!/bin/sh
cd ${0%/*} || exit 1    # run from this directory

./blockMeshRes.py 80
./Allrun
./perf.py True 80
./Allclean

./blockMeshRes.py 90
./Allrun
./perf.py True 90
./Allclean

./blockMeshRes.py 100
./Allrun
./perf.py True 100
./Allclean

./blockMeshRes.py 110
./Allrun
./perf.py True 110
./Allclean
