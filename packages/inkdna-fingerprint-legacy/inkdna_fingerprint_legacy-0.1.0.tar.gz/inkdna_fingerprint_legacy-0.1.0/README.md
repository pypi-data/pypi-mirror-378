
# inkdna-fingerprint-legacy

**Offline** legacy InkDNA stamper & verifier for PDFs.
No keys. No API. No device activation.

> ⚠️ Limit: OCR/raster pipelines (render → OCR → rebuild) will remove the fingerprint.

## CLI
```bash
inkdna-legacy stamp input.pdf --code "ORD-123" -o output.pdf
inkdna-legacy verify output.pdf --code "ORD-123"
```

## Python
```python
from inkdna_fingerprint_legacy import stamp_pdf, verify_pdf
stamp_pdf("input.pdf", "stamped.pdf", code="ORD-123")
ok, msg, details = verify_pdf("stamped.pdf", code="ORD-123")
print(ok, msg, details)
```
