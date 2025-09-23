from typing import Any, Dict, Optional, Tuple

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


class ExceptionFormatter:
    """
    Custom DRF exception handler that formats all exceptions
    into a consistent JSON payload with status, code, messages,
    exception type, and originating view.
    """

    CLIENT_ERROR_RANGE = range(400, 500)

    def __call__(self, exception: Exception, context: Dict[str, Any]) -> Response:
        """
        Entry point for the exception handler.

        If DRF recognizes the exception, extracts status and messages
        via `_extract_from_drf`; otherwise, treats it as unhandled
        via `_extract_unhandled`. Always returns a Response with
        a standardized payload.
        """
        standard_response = drf_exception_handler(exception, context)
        exception_type = exception.__class__.__name__
        view_name = self._get_view_name(context)

        if standard_response:
            status_code, error_messages = self._extract_from_drf(standard_response)
        else:
            status_code, error_messages = self._extract_unhandled(exception)

        error_code = (
            "client_error"
            if status_code in self.CLIENT_ERROR_RANGE
            else "internal_server_error"
        )

        payload = {
            "status": "error",
            "code": error_code,
            "default_code": (
                exception.default_code if isinstance(exception, APIException) else None
            ),
            "error_messages": error_messages,
            "exception_type": exception_type,
            "view": view_name,
        }
        return Response(payload, status=status_code)

    def _get_view_name(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Retrieve the name of the view class from the context.
        Returns None if no view is present.
        """
        view = context.get("view")
        return view.__class__.__name__ if view else None

    def _extract_from_drf(self, response: Response) -> Tuple[int, Any]:
        """
        Extract status code and error messages from a DRF Response.

        - For client errors (400–499), flattens the error dict.
        - For other statuses, returns the 'detail' field or an empty list.
        """
        status_code = response.status_code

        if status_code in self.CLIENT_ERROR_RANGE:
            return status_code, self._flatten_errors(response.data)

        return status_code, response.data.get("detail", [])

    def _extract_unhandled(self, exception: Exception) -> Tuple[int, list]:
        """
        Handle any exceptions not processed by DRF's handler.

        Returns HTTP 500 and a list of the exception's arguments.
        """
        return status.HTTP_500_INTERNAL_SERVER_ERROR, list(exception.args)

    def _flatten_errors(self, errors: Any) -> Any:
        """
        Recursively flatten error structures:

        - If a dict, process each value.
        - If a single-item list of primitives, return the item.
        - If a multi-item list, flatten each element.
        - Otherwise, return the value unchanged.
        """
        if isinstance(errors, dict):
            return {key: self._flatten_errors(value) for key, value in errors.items()}
        if isinstance(errors, list):
            if len(errors) == 1 and isinstance(errors[0], (str, int, float)):
                return errors[0]
            return [self._flatten_errors(el) for el in errors]
        return errors


drf_json_exception_handler = ExceptionFormatter()
