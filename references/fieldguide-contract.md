# Field Guide Contract

## Purpose

Interpret the worksheet that explains how workbook fields should be filled.

## Two levels of guide

### Legacy workbook field-guide sheet

The workbook may contain a lightweight guide sheet with headers that can be mapped to:

- field name
- fill guidance
- recommended values or notes

This is still acceptable as an input format.

### Upgraded field manual

In survey-oriented mode, the legacy sheet is not the final authority.
The skill must upgrade it into a decision-ready `field-manual.md`.

## Legacy-sheet detection

The sheet name is not fixed.

The worksheet is considered a valid legacy guide candidate when its header row can be mapped to:

- field name
- fill guidance
- recommended values or notes

## Upgrade requirement in survey-oriented mode

The upgraded field manual should express, for each field:

- field name
- writing chapter or writing question served by this field
- field purpose
- decision question
- recommended values
- positive triggers
- negative or confusing cases
- required evidence
- conservative fallback rule when evidence is insufficient

## Interpretation rules

- Treat the workbook field-guide sheet as a lightweight source, not necessarily the final classification protocol.
- Treat the field manual as the authoritative decision layer in survey-oriented mode.
- If the guide remains too weak to support stable classification, stop batch processing and discuss with the user.

## Required pause behavior

Stop and discuss when:

- no worksheet can be mapped to the legacy semantics
- only one or two legacy semantic columns are present
- multiple guide candidates conflict with each other
- a target field matters for the survey outline but has no usable guide entry
- the guide lacks stable decision questions or boundary rules for major taxonomy fields
