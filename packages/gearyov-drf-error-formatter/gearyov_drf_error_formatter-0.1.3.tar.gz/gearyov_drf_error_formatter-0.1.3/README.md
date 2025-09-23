# gearyov-drf-error-formatter

Custom Django REST Framework exception handler that **normalizes all errors** into a single, predictable JSON payload.

[![PyPI version](https://badge.fury.io/py/gearyov-drf-error-formatter.svg)](https://badge.fury.io/py/gearyov-drf-error-formatter)
[![Python Versions](https://img.shields.io/pypi/pyversions/gearyov-drf-error-formatter.svg)](https://pypi.org/project/gearyov-drf-error-formatter/)

```bash
pip install gearyov-drf-error-formatter
```

---

## Why?

Out of the box, DRF returns different shapes for different errors (validation vs. permission vs. server errors).  
This package provides a **single JSON contract** for clients, so your frontend and integrators can rely on one structure.

---

## Features

- **Uniform JSON output** for all exceptions (DRF + unhandled Python)
- **Client errors (4xx)**: returns **flattened** field-level messages
- **Server errors (5xx)**: returns exception args/type for easier debugging
- **Extra context**: includes exception type and originating view
- **`default_code` passthrough** for `APIException`-based errors
- Plug-and-play: just set `EXCEPTION_HANDLER`

---

## Installation

```bash
pip install gearyov-drf-error-formatter
```

Add to your Django settings:

```python
# settings.py
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "gearyov_drf_error_formatter.drf_json_exception_handler",
}
```

---

## Response format

Every error follows the same structure:

```json
{
  "status": "error",
  "code": "client_error" | "internal_server_error",
  "default_code": "OPTIONAL_STRING_OR_NULL",
  "error_messages": "... see below ...",
  "exception_type": "PythonOrDRFExceptionClassName",
  "view": "OriginatingViewClassNameOrNull"
}
```

---

## Examples

### Validation error (400)

```json
{
  "status": "error",
  "code": "client_error",
  "default_code": "invalid",
  "error_messages": {
    "password": "Too short"
  },
  "exception_type": "ValidationError",
  "view": "RegisterView"
}
```

### Custom APIException (400)

```json
{
  "status": "error",
  "code": "client_error",
  "default_code": "WRONG_LENGTH_PASSWORD_1",
  "error_messages": {
    "detail": "This is a custom error for testing"
  },
  "exception_type": "CustomApplicationError",
  "view": "CustomErrorView"
}
```

### Permission denied (403)

```json
{
  "status": "error",
  "code": "client_error",
  "default_code": "permission_denied",
  "error_messages": {
    "detail": "You do not have permission to perform this action."
  },
  "exception_type": "PermissionDenied",
  "view": "AdminOnlyView"
}
```

### Not found (404)

```json
{
  "status": "error",
  "code": "client_error",
  "default_code": "not_found",
  "error_messages": {
    "detail": "Not found."
  },
  "exception_type": "NotFound",
  "view": "UserDetailView"
}
```

### Server error (500)

```json
{
  "status": "error",
  "code": "internal_server_error",
  "default_code": null,
  "error_messages": ["Boom"],
  "exception_type": "ValueError",
  "view": "PaymentView"
}
```

---

## Customization

You can extend the formatter to add logging, Sentry, request IDs, etc.

```python
from gearyov_drf_error_formatter import ExceptionFormatter

class MyFormatter(ExceptionFormatter):
    def __call__(self, exception, context):
        # custom logging here
        return super().__call__(exception, context)

my_exception_handler = MyFormatter()
```

```python
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "myproject.exceptions.my_exception_handler",
}
```

---

## Compatibility

- Python ≥ 3.12
- Django REST Framework 3.x
- Django (any version supported by DRF)

---

## License

MIT

---

## Maintainer

Vladyslav Shesternyov
