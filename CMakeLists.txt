cmake_minimum_required(VERSION 2.6.4)

# ***** project specific configuration that must be first *****
project(libMscBoostPython)
set(MSC_PROJECT_NUMBER 0000 CACHE STRING "MSC Project number")
SET(MSC_PROJECT_RELEASE_DIR "Software/0000 \(MSC\)/Software/Releases/0000_libMscBoostPython" CACHE STRING "MSC Project Directory")

# ***** Custom configuration *****

set(PROJECT_HAS_NO_C_CODE true)
set(PROJECT_HAS_PYTHON_CODE true)

# Cover the Msc module
set(PYTEST_COVERAGE_EXTRA_ARGS "--cov=Msc")

# *****  load MSC helpers *****

include(version.in)
include(msc)
include(msc_app_python)

# We don't need a PDF file.
set(DOXYFILE_LATEX off)
include(UseDoxygen)

add_subdirectory(src/Msc)
add_subdirectory(src/Msc/Boost)
add_subdirectory(src/examples)
add_subdirectory(src/test)
