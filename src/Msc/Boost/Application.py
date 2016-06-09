from abc import ABCMeta
from abc import abstractmethod


class Application():
    """Main application handling command line options and error handling. Override it, implement _Main() and call Run
    """
    _metaclass=ABCMeta

    def __init__(self):
        pass

    def Run(self):
        self._Main()

    @abstractmethod
    def _Main(self):
        pass
