if(POLICY CMP0012)
  cmake_policy(SET CMP0012 NEW)
endif()

include(AddPyTest)

setup_pytest(
  /usr/bin/py.test-3
  ${PROJECT_BINARY_DIR}/py.test.sh
  )

add_pytest(
  conftest.py

  test_Application.py
  test_Environment.py
  test_FilePath.py
  test_FindBestMatch.py
  # test_Git.py
  test_Logging.py
  test_MscProject.py
  test_Version.py

  # test_pylama.py

  NOINSTALL
)

add_pylama_test()
