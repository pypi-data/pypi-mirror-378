

class FountError(Exception):
    def __init__(self, message=None, code=None, details=None):
        self.code = code
        self.details = details
        super().__init__(message)

class UnauthorizedError(FountError):
    ...

class TimedOutError(FountError):
    ...

class RateLimitError(FountError):
    ...

class CSVParseError(FountError):
    ...

class CSVFileError(FountError):
    ...

class UploadError(FountError):
    ...

class TrainingError(FountError):
    ...

class InferenceError(FountError):
    ...

class TuningError(FountError):
    ...
