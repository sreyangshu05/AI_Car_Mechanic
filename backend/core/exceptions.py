"""
Custom exceptions and DRF exception handler for consistent error responses.
All API errors follow the format:
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable description"
    }
}
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


class APIError(Exception):
    """Base API error with structured code, message, and HTTP status."""

    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ValidationError(APIError):
    """Input validation failed."""

    def __init__(self, message: str, code: str = 'VALIDATION_ERROR'):
        super().__init__(code=code, message=message, status_code=400)


class NotFoundError(APIError):
    """Requested resource not found."""

    def __init__(self, message: str = 'Resource not found', code: str = 'NOT_FOUND'):
        super().__init__(code=code, message=message, status_code=404)


class AIServiceError(APIError):
    """AI service (Gemini) encountered an error."""

    def __init__(self, message: str = 'AI service temporarily unavailable'):
        super().__init__(
            code='AI_SERVICE_ERROR',
            message=message,
            status_code=503,
        )


class MediaValidationError(APIError):
    """Media upload validation failed."""

    def __init__(self, message: str, code: str = 'INVALID_FILE'):
        super().__init__(code=code, message=message, status_code=400)


class InsufficientDataError(APIError):
    """Not enough information to perform the requested action."""

    def __init__(self, message: str = 'Insufficient information gathered'):
        super().__init__(
            code='INSUFFICIENT_DATA',
            message=message,
            status_code=400,
        )


def error_response(code: str, message: str, status_code: int = 400) -> Response:
    """Build a consistent error Response object."""
    return Response(
        {
            'success': False,
            'error': {
                'code': code,
                'message': message,
            },
        },
        status=status_code,
    )


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler that normalizes all errors
    into the standard {success, error} format.
    """
    # Handle our custom APIError subclasses
    if isinstance(exc, APIError):
        return error_response(exc.code, exc.message, exc.status_code)

    # Let DRF handle its own exceptions first
    response = exception_handler(exc, context)

    if response is not None:
        # Re-format DRF errors into our standard shape
        if isinstance(response.data, dict):
            detail = response.data.get('detail', '')
            if not detail:
                # Collect field-level errors
                errors = []
                for field, messages in response.data.items():
                    if isinstance(messages, list):
                        for msg in messages:
                            errors.append(f'{field}: {msg}')
                    else:
                        errors.append(f'{field}: {messages}')
                detail = '; '.join(errors) if errors else 'Invalid request'
            response.data = {
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': str(detail),
                },
            }
        elif isinstance(response.data, list):
            response.data = {
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': '; '.join(str(e) for e in response.data),
                },
            }
        return response

    # Unhandled exception — return generic 500 without exposing internals
    return None

