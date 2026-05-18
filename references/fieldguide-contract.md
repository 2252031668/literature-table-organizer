# Field Guide Contract

## Purpose

Identify the worksheet that explains how the user wants literature fields to be filled.

## Required semantics

The sheet name is not fixed.

The worksheet is valid when its header row can be mapped to these semantic columns:

- field name
- fill guidance
- recommended values or notes

Accept light variants such as:

- field name variants
- fill strategy variants
- notes-only variants

## Interpretation rules

- Treat the field-name column as the target column name in the primary paper sheet.
- Treat the guidance column as the expected fill strategy or wording rule.
- Treat the values/notes column as the allowed values, examples, or semantic boundary.

## Required pause behavior

Stop and discuss with the user when:

- no worksheet can be mapped to the required semantics
- only one or two of the semantic columns are present
- multiple field-guide candidates conflict with each other
- the target paper sheet contains columns with no corresponding guide entry and those columns matter for the requested work
