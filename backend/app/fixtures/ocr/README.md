# OCR Text Fixtures

Synthetic OCR-extracted text samples for the Northwind Legal Group intake demo.

Each `.txt` file represents the plain text that `app/services/ocr.py::extract_text`
would return after running Tesseract over a scanned complaint/intake letter. In the
app, this text lands in `Intake.description` and `Attachment.extracted_text`
(see `app/routers/intakes.py`), so the fixtures are shaped to match real OCR output:

- One letter per file: date, salutation, multi-paragraph body, signature block.
- Multi-page documents use the page separator `\n\n---\n\n` that
  `_extract_from_pdf` emits between pages (see `06-...-multipage.txt`).
- A couple of files include light, realistic OCR noise (e.g. `Novernber` for
  `November`, `l` misread for `I`) to mimic imperfect Tesseract output on
  handwritten or low-quality scans (see `08-...-handwritten.txt`).

## Everything here is fabricated

These samples are entirely fictional. All names are invented, street/town names
are made up, phone numbers use the reserved `555-01xx` range, complainant emails
use the `example.com` reserved domain, and dates are plausible but fabricated. No
real person, organization, or place is referenced.

## Category coverage

The samples span the intake categories defined in the schema seed
(`database/migrations/001_initial_schema.sql`):

| File | Category slug |
|------|---------------|
| `01-police-misconduct-traffic-stop.txt` | `police-misconduct` |
| `02-housing-discrimination-eviction.txt` | `housing` |
| `03-employment-disability-discrimination.txt` | `discrimination` |
| `04-free-speech-protest-permit.txt` | `free-speech` |
| `05-voting-rights-purge.txt` | `voting` |
| `06-privacy-data-rights-multipage.txt` | `privacy` |
| `07-immigration-detention.txt` | `immigration` |
| `08-prisoners-rights-medical-handwritten.txt` | `prisoners` |

## Suggested use

Feed a file's contents in as the `extracted` OCR text when seeding demo intakes,
or paste it into the scan-review flow to exercise classification and the
staff-review UI without needing a real scanned image.
