class TgqSimError(Exception):
    """Base class for all exceptions raised by the tgqsim module."""
    def __init__(self, *message):
        super().__init__(" ".join(message))
        self.message = " ".join(message)
    
    def __repr__(self) -> str:
        return repr(self.message)