import os
import re

from .Version import Version

## @brief MSC Project
## See also <a href="https://docs.python.org/3/howto/argparse.html">argparse</a>.
class MscProject():
    """An MSC project follows various guide lines. For example, it has a version.in. This class provides access to projects following the guideline.
    """

    def __init__(self, path):
        ## @param path The path to the project root directory (cmake's PROJECT_SOURCE_DIR)
        self.path = path
        self._create_version_from_in()

    ## @param path_below_root Some path below the root (e.g. src/test)
    ## @return the path to the project root (cmake's PROJECT_SOURCE_DIR)
    @staticmethod
    def find_project_root(path_below_root):
        """Returns the project root directory (containing COPYING/)."""
        dir = path_below_root
        while not os.path.exists(os.path.join(dir, "COPYING")):
            dir = os.path.abspath(dir)
            if dir == "/":
                # Reached root
                raise RuntimeError("Not called within a cmake project directory")

            dir = os.path.join(dir, "..")

        return dir

    def _create_version_from_in(self):
        version_in = os.path.join(self.path, "version.in")

        with open(version_in, "r") as version_in_file:
            ## @param major The major part of the version (incremented on incompatible changes).
            major = self._get_version_part(version_in_file, "MAJOR")
            ## @param minor The minor part of the version (incremented on compatible feature changes).
            minor = self._get_version_part(version_in_file, "MINOR")
            ## @param patch The patch part of the version (incremented on bugfixes).
            patch = self._get_version_part(version_in_file, "PATCH")

            # These must always exist
            assert major is not None
            assert minor is not None
            assert patch is not None

            # This is optional.Older definitions might not have it
            ## @param build The build part of the version (incremented when the actual source code is not changed).
            build = self._get_version_part(version_in_file, "BUILD")

        ## @param version The version of the project.
        self.version = Version(major, minor, patch, build)

    ## @param version_in_file The open file handle for version.in
    ## @param part The part of the version to return, e.h. "MAJOR", "MINOR", "PATCH" or "BUILD"
    @staticmethod
    def _get_version_part(version_in_file, part):
        """Returns the part of the version as int or None."""
        re_def = re.compile(
            r'set\(VERSION_{} "(.*)"\)'.format(part)
            )

        line = version_in_file.readline()
        if line == "":
            # part does not exist, use a default one
            return None

        match = re_def.match(line)
        if match is not None:
            value = match.group(1)
            return int(value)
        else:
            raise KeyError("Expected {0} in version.in, got line {1}.".format(
                part,
                line,
                )
            )
