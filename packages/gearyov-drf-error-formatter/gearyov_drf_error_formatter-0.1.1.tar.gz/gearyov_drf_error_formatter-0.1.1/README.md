# gearyov-drf-error-formatter

Custom DRF exception handler that formats all exceptions into a consistent JSON payload.

## Features

- **Uniform JSON output** for both DRF-native exceptions and unhandled Python exceptions  
- **Client errors** (4xx) preserve field-level details as flattened messages  
- **Server errors** (5xx) return exception args and type for easier debugging  
- Automatically includes **exception type** and **originating view** in the response

## Installation

```bash

pip install gearyov-drf-error-formatter
