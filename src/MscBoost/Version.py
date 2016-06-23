class Version():
    """Provides application version handling."""

    ## @param major The major version number. (vMajor.Minor.Patch.Build)
    ## @param minor The minor version number. (vMajor.Minor.Patch.Build)
    ## @param patch The patch level. (vMajor.Minor.Patch.Build)
    ## @param build The build number. (vMajor.Minor.Patch.Build)
    def __init__(self, major, minor, patch, build = None):
        """Initializes a new instance."""
        ## @param major The major part of the version (incremented on incompatible changes).
        self.major = major
        ## @param minor The minor part of the version (incremented on compatible feature changes).
        self.minor = minor
        ## @param patch The patch part of the version (incremented on bugfixes).
        self.patch = patch

        ## @param build The build part of the version (incremented when the actual source code is not changed).
        self.build = build

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

    def __eq__(self, other):
        """== and != operator"""
        if isinstance(other, Version):
            rc = self.major == other.major \
                and self.minor == other.minor \
                and self.patch == other.patch \
                and self.build == other.build
        else:
            rc = NotImplemented

        return rc

    def __lt__(self, other):
        """< and > operator"""
        if isinstance(other, Version):
            if self.build == None:
                sbuild = 0
            else:
                sbuild = self.build

            if other.build == None:
                obuild = 0
            else:
                obuild = other.build

            rc = (self.major < other.major) \
                 or ((self.major == other.major) and self.minor < other.minor) \
                 or ((self.major == other.major and self.minor == other.minor) and self.patch < other.patch) \
                 or ((self.major == other.major and self.minor == other.minor and self.patch == other.patch) and sbuild < obuild)
        else:
            rc = NotImplemented

        return rc

    def __le__(self, other):
        """<= and >= operator"""
        if isinstance(other, Version):
            if self.build == None:
                sbuild = 0
            else:
                sbuild = self.build

            if other.build == None:
                obuild = 0
            else:
                obuild = other.build

            rc = (self.major <= other.major) \
                 or ((self.major == other.major) and self.minor <= other.minor) \
                 or ((self.major == other.major and self.minor == other.minor) and self.patch <= other.patch) \
                 or ((self.major == other.major and self.minor == other.minor and self.patch == other.patch) and sbuild < obuild)
        else:
            rc = NotImplemented

        return rc
    
