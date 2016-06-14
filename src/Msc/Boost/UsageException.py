class UsageException(Exception):
    """Provides an exception class for command line misuses within Application."""

    # @param what Exception message.
    def __init__(self, what):
        super(self.__class__,self).__init__(what)
