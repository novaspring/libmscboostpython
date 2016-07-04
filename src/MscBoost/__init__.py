# As there are not only pure class submodules but also submodules with singleton
# initialization (e.g. Logging or Git) we can't import all submodules.
# This would initialize the singletons even when not needed and e.g. list
# them in Application (EnvironmentVariable).
# Therefore we have to import on demand, e.g. with
# from MscBoost.Application import Application
