class DocumentError(Exception):
    pass

class DocumentNotFoundError(DocumentError):
    pass


class DocumentAlreadyProcessingError(DocumentError):
    pass


class DocumentAlreadyProcessedError(DocumentError):
    pass


class UnsupportedDocumentTypeError(DocumentError):
    pass


class EmptyDocumentError(DocumentError):
    pass