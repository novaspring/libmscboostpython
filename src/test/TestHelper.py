import os

def find_project_root():
    """Returns the project root directory (cmake's PROJECT_SOURCE_DIR)."""
    dir = os.getcwd()
    while not os.path.exists(os.path.join(dir, "COPYING")):
        dir = os.path.abspath(dir)
        if dir == "/":
            # Reached root
            raise Exception("Not called within cmake project directory")

        dir = os.path.join(dir, "..")

    return dir
