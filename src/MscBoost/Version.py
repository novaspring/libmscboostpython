class Version():
    """Provides application version handling."""

    ## @param major The major version number. (vMajor.Minor.Patch.Extra)
    ## @param minor The minor version number. (vMajor.Minor.Patch.Extra)
    ## @param patch The patch level. (vMajor.Minor.Patch.Extra)
    ## @param extra The extra number (e.g. extra). (vMajor.Minor.Patch.Extra)
    def __init__(self, major, minor, patch, extra=None):
        """Initializes a new instance."""
        ## @param major The major part of the version (incremented on incompatible changes).
        self.major = major
        ## @param minor The minor part of the version (incremented on compatible feature changes).
        self.minor = minor
        ## @param patch The patch part of the version (incremented on bugfixes).
        self.patch = patch

        ## @param extra The extra part of the version (incremented when the actual source code is not changed).
        self.extra = extra

    def __repr__(self):
        """Returns a human readable version (e.g. v1.0.0.0)."""
        # extra version is optional
        extra = ""
        if self.extra is not None:
            extra = ".{0}".format(self.extra)

        return "v{0}.{1}.{2}{3}".format(
            self.major,
            self.minor,
            self.patch,
            extra
            )

    def __eq__(self, other):
        """== and != operator"""
        if isinstance(other, Version):
            rc = self.major == other.major \
                and self.minor == other.minor \
                and self.patch == other.patch \
                and self.extra == other.extra
        else:
            rc = NotImplemented

        return rc

    def __lt__(self, other):
        """< and > operator"""
        if isinstance(other, Version):
            if self.extra is None:
                sextra = 0
            else:
                sextra = self.extra

            if other.extra is None:
                oextra = 0
            else:
                oextra = other.extra

            rc = (self.major < other.major) \
                or ((self.major == other.major) and self.minor < other.minor) \
                or ((self.major == other.major and self.minor == other.minor) and self.patch < other.patch) \
                or ((self.major == other.major and self.minor == other.minor and self.patch == other.patch) and sextra < oextra)
        else:
            rc = NotImplemented

        return rc

    def __le__(self, other):
        """<= and >= operator"""
        if isinstance(other, Version):
            if self.extra is None:
                sextra = 0
            else:
                sextra = self.extra

            if other.extra is None:
                oextra = 0
            else:
                oextra = other.extra

            rc = (self.major <= other.major) \
                or ((self.major == other.major) and self.minor <= other.minor) \
                or ((self.major == other.major and self.minor == other.minor) and self.patch <= other.patch) \
                or ((self.major == other.major and self.minor == other.minor and self.patch == other.patch) and sextra < oextra)
        else:
            rc = NotImplemented

        return rc
