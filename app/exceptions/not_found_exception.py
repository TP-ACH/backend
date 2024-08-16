class NotFoundException(Exception):
    """Exception raised for errors in the input where a resource is not found."""
    def __init__(self, message="Resource not found"):
        self.message = message
        super().__init__(self.message)