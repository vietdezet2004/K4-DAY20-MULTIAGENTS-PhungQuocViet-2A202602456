---
name: error-logging-standards
description: Use when processing and logging error data to ensure compliance with organizational standards.
---
- Ensure the top-level JSON object includes "schema_version": 2 and "generated_by": "log-triage".
- Sort error entries by service name and then by timestamp in ascending order.
- Maintain a count of occurrences for each error, using a repeat count to indicate how many times the same error has occurred.
- Use lowercase service names with hyphens replaced by underscores in the output.
- Ensure that all timestamps are in UTC format (YYYY-MM-DDTHH:MM:SSZ).
- Validate that all exception fields are correctly populated and formatted.
- Document any discrepancies or issues found during the logging process for future reference.
