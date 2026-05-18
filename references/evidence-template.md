# Evidence Template

Each paper should end with one Markdown file under `evidence/`.

## Required sections

1. Row metadata
   - row number
   - paper title
   - original link
   - source type
   - source kind
   - evidence level
   - whether full backfill is allowed
   - local source path
2. Source inventory
   - final resolved URL
   - secondary URLs used
   - local source file
   - local text file when applicable
3. Source segments used
   - path
   - locator such as page or line range
   - quoted or summarized segment
4. Classification conclusions
   - one row per user-defined classification field
5. Field-by-field evidence mapping
   - field value
   - source segments used
   - derivation note
6. Verified summary fields
   - updated wording
   - source segments used
7. Warnings or notes

## Source-type rules

- If the source is a PDF, keep `paper.pdf` and generate `paper.txt`.
- If the source is a fulltext webpage, keep `source.md` with the URL, access date, and the key content that was actually used.
- If the source is a secondary review page, keep `review.md` and explicitly mark it as a secondary source.
- If the source is abstract-only, keep `source.md` but mark the row as not suitable for default full backfill.
- Every field conclusion should be traceable to one or more explicit source segments.

## Backfill rules

- `pdf_download`, `pdf_via_browser`, `fulltext_web`: full backfill allowed
- `secondary_review`: full backfill allowed, but note that it is not the original paper text
- `abstract_only`: path + warning only by default
- `unresolved`, `mismatch_or_unverifiable`: warning-only by default

## Tone rules

- Keep wording concise and factual.
- Do not write speculative language unless the row is explicitly marked as unresolved or abstract-only.
- When evidence is weak, say so in the warning section instead of pretending certainty.
