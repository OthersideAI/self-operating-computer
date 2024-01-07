class ModelNotRecognizedException(Exception):
    """Exception raised for unrecognized models.

    Attributes:
        model -- the unrecognized model
        message -- explanation of the error
    """

    def __init__(self, model, message="Model not recognized"):
        self.model = model
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} : {self.model} "