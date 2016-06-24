if(POLICY CMP0012)
  cmake_policy(SET CMP0012 NEW)
endif()

include(PythonModule)

file(
  GLOB SRC
  "*.py"
  )

add_python_module(
  MscBoost
  ${SRC}
  INSTALL
  )

add_pylama_test()
