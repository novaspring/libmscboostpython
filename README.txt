Overview
========

This library provides Python 3.x helper functions.

Requirements
============
 * Python 3.0
 * pytest (python3-pytest)
 * coverage

Installation of coverage (ubuntu 16.04)
=================================
 * sudo apt-get install python3-pip
 * sudo pip3 install coverage
 * sudo pip3 install pytest-cov

Compilation
===========

Relase
------

mkdir Release
cd Release
cmake ..
# or cmake -DCMAKE_INSTALL_PREFIX=/usr ..
make -j8 -s all doc && make test
make install DESTDIR=/tmp/libMscBoostPython
sensible-browser doc/html/index.html

Coverage
---------

mkdir Release_Coverage
cd Release_Coverage
cmake -DBUILD_TYPE=Coverage ..
make -j8 -s all && coverage-clean test coverage-doc
sensible-browser Coverage/index.html
