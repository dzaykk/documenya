from app.exceptions.base import AppException


class DocumentNotFoundError(AppException):
    status_code = 404
    detail = "Document not found"


class DocumentAlreadyProcessingError(AppException):
    status_code = 409
    detail = "Document is already processing"


class DocumentAlreadyProcessedError(AppException):
    status_code = 409
    detail = "Document is already processed"


class DocumentProcessingFailedError(AppException):
    status_code = 409
    detail = "Document processing failed"


class UnsupportedDocumentTypeError(AppException):
    status_code = 400
    detail = "Unsupported file type"


class EmptyDocumentError(AppException):
    status_code = 400
    detail = "Document is empty"


class FileTooLargeError(AppException):
    status_code = 413
    detail = "File is too large"