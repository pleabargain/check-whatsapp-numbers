# Phone Number Validator

A Streamlit application that validates and standardizes phone numbers in JSON files, with a current focus on UAE phone numbers.

## Features

- Validates and standardizes phone numbers to international format
- Handles multiple input formats:
  - Local numbers (e.g., `0501234567`)
  - International format with + (e.g., `+971501234567`)
  - International format with 00 (e.g., `00971501234567`)
  - Numbers with spaces and parentheses (e.g., `(0)50 123 4567`)
- Provides detailed error reporting
- Displays processed JSON in side panel
- Preserves original file (creates new standardized output)
- Shows processing statistics

## Input Requirements

The JSON file should follow this structure:

```json
{
  "people": [
    {
      "name": "John Doe",
      "phone": "0501234567",
      "location": "Dubai",
      "image": "https://example.com/image.jpg",
      "description": "..."
    }
  ]
}
```
    