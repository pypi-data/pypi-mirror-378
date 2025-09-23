
from __future__ import annotations
import json, zlib, time, hashlib
from pathlib import Path
import pikepdf

_MARKER = b"/Span <</DINKDNA true>> BDC"

def _content_hash_excluding_our_streams(pdf_path: Path) -> str:
    pdf = pikepdf.Pdf.open(str(pdf_path))
    h = hashlib.sha256()
    for page in pdf.pages:
        raw = page.Contents
        refs = [] if raw is None else (list(raw) if isinstance(raw, pikepdf.Array) else [raw])
        for ref in refs:
            try:
                obj = ref if hasattr(ref, "read_bytes") else pdf.open_object(ref)
                data = obj.read_bytes()
            except Exception:
                continue
            if _MARKER in data:
                continue
            h.update(data)
    return h.hexdigest()

def stamp_pdf(input_pdf: str | Path, output_pdf: str | Path, *, code: str) -> None:
    input_pdf = Path(input_pdf)
    output_pdf = Path(output_pdf)

    chash = _content_hash_excluding_our_streams(input_pdf)
    env = {"v": 1, "code": str(code), "content_hash": chash, "ts": int(time.time())}
    env_json = json.dumps(env, separators=(",", ":"), sort_keys=True).encode("utf-8")
    env_zip = zlib.compress(env_json)
    env_hex = env_zip.hex().upper().encode("utf-8")

    pdf = pikepdf.Pdf.open(str(input_pdf))
    for page in pdf.pages:
        res = page.Resources or pikepdf.Dictionary()
        fonts = res.get("/Font", pikepdf.Dictionary())
        if "/F1" not in fonts:
            fonts["/F1"] = pdf.make_indirect(
                pikepdf.Dictionary(
                    {"/Type": pikepdf.Name("/Font"), "/Subtype": pikepdf.Name("/Type1"), "/BaseFont": pikepdf.Name("/Helvetica")}
                )
            )
        res["/Font"] = fonts
        page.Resources = res

        stm = b"\n".join([
            b"q",
            b"3 Tr",
            b"BT",
            b"/F1 1 Tf",
            b"10000 10000 Td",
            _MARKER,
            b"<" + env_hex + b"> Tj",
            b"EMC",
            b"ET",
            b"Q",
        ])

        existing = page.Contents
        if existing is None:
            page.Contents = pdf.make_indirect(pdf.make_stream(stm))
        else:
            arr = list(existing) if isinstance(existing, pikepdf.Array) else [existing]
            arr.append(pdf.make_stream(stm))
            page.Contents = pdf.make_indirect(pikepdf.Array(arr))

    pdf.save(str(output_pdf))
