# Evidence Template

Each paper should end with one Markdown file under `evidence/`.

## Required sections

1. Row metadata
   - row number
   - paper title
   - original link
   - source type
   - local source path
2. Source segments used
   - path
   - locator such as page or line range
   - quoted or summarized segment
3. Classification conclusions
   - one row per user-defined classification field
4. Field-by-field evidence mapping
   - field value
   - source segments used
   - derivation note
5. Verified summary fields
   - updated wording
   - source segments used
6. Warnings or notes

## Source-type rules

- If the source is a PDF, keep `paper.pdf` and generate `paper.txt`.
- If the source is a web preview, keep `source.md` with the URL, access date, and the key content that was actually used.
- Every field conclusion should be traceable to one or more explicit source segments.

## Tone rules

- Keep wording concise and factual.
- Do not write speculative language unless the row is explicitly marked as unresolved.
- When evidence is weak, say so in the warning section instead of pretending certainty.
