Overview
========

This library provides Python 3.x helper functions.

Compilation
===========

mkdir Release
cd Release
cmake -DCMAKE_INSTALL_PREFIX=/usr
# or cmake -DCMAKE_INSTALL_PREFIX=/usr ..
make -j8 -s all doc && make test
make install DESTDIR=/tmp/libMscBoostPython
google-chrome doc/html/index.html
