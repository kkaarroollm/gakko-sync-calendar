class CommandPipelineError(Exception):
    """Exception raised when a command pipeline fails."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
