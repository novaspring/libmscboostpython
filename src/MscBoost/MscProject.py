import os
import re

class Version():
    """Provides access to MSC projects versions by parsing version.in."""

    ## @param path The path to the version.in (cmake's PROJECT_SOURCE_DIR)
    def __init__(self, path):
        """Initializes a new instance."""
        version_in = os.path.join(path, "version.in")
        
        with open(version_in, "r") as version_in_file:
            ## @param major The major part of the version (incremented on incompatible changes).
            self.major = self._get_version_part(version_in_file, "MAJOR")
            ## @param minor The minor part of the version (incremented on compatible feature changes).
            self.minor = self._get_version_part(version_in_file, "MINOR")
            ## @param patch The patch part of the version (incremented on bugfixes).
            self.patch = self._get_version_part(version_in_file, "PATCH")

            # These must always exist
            assert self.major is not None
            assert self.minor is not None
            assert self.patch is not None

            # This is optional.Older definitions might not have it
            ## @param build The build part of the version (incremented when the actual source code is not changed).
            self.build = self._get_version_part(version_in_file, "BUILD")

    def __repr__(self):
        """Returns a human readable version (e.g. v1.0.0.0)."""
        # build version is optional
        build = ""
        if self.build is not None:
            build = ".{0}".format(self.build)
            
        return "v{0}.{1}.{2}{3}".format(
            self.major,
            self.minor,
            self.patch,
            build
            )

    ## @param version_in_file The open file handle for version.in
    ## @param part The part of the version to return, e.h. "MAJOR", "MINOR", "PATCH" or "BUILD"
    def _get_version_part(self, version_in_file, part):
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
        
## @brief MSC Project
## See also <a href="https://docs.python.org/3/howto/argparse.html">argparse</a>.
class MscProject():
    """An MSC project follows various guide lines. For example, it has a version.in. This class provides access to projects following the guideline.
    """
    
    def __init__(self, path):
        ## @param path The path to the project root directory (cmake's PROJECT_SOURCE_DIR)
        self.path = path
        ## @param version The version of the project.
        self.version = Version(path)

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
