---
name: csv-formatting-guidelines
description: Use when creating or modifying CSV files to meet organizational standards.
---
- Ensure CSV files have a header row with the correct column names.
- Use canonical spelling for regions (North, South, East, West) in the region column.
- Format timestamps in the UTC timezone as YYYY-MM-DDTHH:MM:SSZ.
- Remove any duplicate rows before finalizing the CSV.
- Ensure all monetary amounts are represented in integer cents (e.g., $1,606.67 should be 160667).
- Follow RFC 4180 for quoting rules: fields containing commas or double quotes must be enclosed in double quotes, and double quotes within fields must be escaped by doubling them.
- Validate the CSV structure before submission to ensure compliance with the expected format.
