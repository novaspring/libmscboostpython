cmake_minimum_required(VERSION 2.6.4)

# ***** project specific configuration that must be first *****
project(libMscBoost)
set(MSC_PROJECT_NUMBER 0000 CACHE STRING "MSC Project number")
SET(MSC_PROJECT_RELEASE_DIR "Software/0000 \(MSC\)/Software/Releases/0000_libMscBoostPython" CACHE STRING "MSC Project Directory")

set(PYTHON_BINARY_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src")

# *****  load MSC helpers *****

include(version.in)
include(msc)

# We don't need a PDF file.
set(DOXYFILE_LATEX off)
include(UseDoxygen)

add_subdirectory(src/MscBoost)
add_subdirectory(src/tests)
add_subdirectory(src/examples)
