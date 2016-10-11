# e.g. for MSC-LDK which doesn't support python detection in configuration
set(PYTHON_MANUAL_INSTALL_PATH "" CACHE PATH "When set, python modules will be installed with raw shell commands instead of auto-detection.")

if(POLICY CMP0012)
  cmake_policy(SET CMP0012 NEW)
endif()

file(
  GLOB SRC
  "*.py"
  )

if (NOT "${PYHTON_MANUAL_INSTALL_PATH}")
  message("X ${SRC}.${PYTHON_MANUAL_INSTALL_PATH}.")
  install(
    FILES ${SRC}
    DESTINATION ${PYTHON_MANUAL_INSTALL_PATH}/MscBoost
    PERMISSIONS ${PERM_644}
    )
else()
  include(PythonModule)

  add_python_module(
    MscBoost
    ${SRC}
    INSTALL
    )

  add_pylama_test()
endif()
