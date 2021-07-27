#!/bin/bash

MYDIR="$(dirname "$(realpath "$0")")"
FILE="runsolver-3.4.0.tar.bz2"

cd ${MYDIR}
wget http://www.cril.univ-artois.fr/~roussel/runsolver/${FILE}

tar xfvj ${FILE}
rm ${FILE}

cd runsolver/src/
make
