"""
Custom exceptions for the Self-Operating Computer
"""

class ModelNotRecognizedException(Exception):
    """Raised when the specified model is not recognized."""
    pass

    def __init__(self, model, message="Model not recognized"):
        self.model = model
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} : {self.model} "