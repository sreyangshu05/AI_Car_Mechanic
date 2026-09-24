"""
Middleware for handling unhandled exceptions globally.
Catches any exception that slips through DRF's exception handler
and returns a safe 500 response without exposing internals.
"""

import logging
import json
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class ExceptionHandlerMiddleware:
    """
    Catches unhandled exceptions and returns a structured JSON error.
    Only applies to API paths (starting with /api/).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """Handle uncaught exceptions for API endpoints."""
        if not request.path.startswith('/api/'):
            return None

        # Import here to avoid circular imports
        from core.exceptions import APIError

        if isinstance(exception, APIError):
            return JsonResponse(
                {
                    'success': False,
                    'error': {
                        'code': exception.code,
                        'message': exception.message,
                    },
                },
                status=exception.status_code,
            )

        # Log the unexpected error
        logger.error(
            'Unhandled exception on %s %s: %s',
            request.method,
            request.path,
            str(exception),
            exc_info=True,
        )

        return JsonResponse(
            {
                'success': False,
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'An unexpected error occurred. Please try again.',
                },
            },
            status=500,
        )

