
from __future__ import annotations
import json, re, zlib, hashlib
from pathlib import Path
import pikepdf

_MARKER = b"/Span <</DINKDNA true>> BDC"
_HEX_TEXT_RE = re.compile(rb"<([0-9A-Fa-f\s]+)>\s*Tj")

def _extract_env(pdf_path: Path):
    pdf = pikepdf.Pdf.open(str(pdf_path))
    for page in pdf.pages:
        raw = page.Contents
        refs = [] if raw is None else (list(raw) if isinstance(raw, pikepdf.Array) else [raw])
        for ref in refs:
            try:
                obj = ref if hasattr(ref, "read_bytes") else pdf.open_object(ref)
                data = obj.read_bytes()
            except Exception:
                continue
            pos = data.find(_MARKER)
            if pos < 0:
                continue
            m = _HEX_TEXT_RE.search(data, pos)
            if not m:
                continue
            hex_bytes = re.sub(rb"\s+", b"", m.group(1))
            try:
                comp = bytes.fromhex(hex_bytes.decode("ascii"))
                js = zlib.decompress(comp)
                env = json.loads(js.decode("utf-8"))
            except Exception:
                continue
            if isinstance(env, dict) and "content_hash" in env:
                return env
    return None

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

def verify_pdf(pdf_path: str | Path, *, code: str | None = None):
    pdf_path = Path(pdf_path)
    env = _extract_env(pdf_path)
    if not env:
        return False, "No InkDNA payload found", {}
    claimed = env.get("content_hash")
    actual = _content_hash_excluding_our_streams(pdf_path)
    ok_hash = (claimed == actual)
    ok_code = True if code is None else (str(env.get("code","")) == str(code))
    ok = ok_hash and ok_code
    details = {"matched_hash": ok_hash, "matched_code": ok_code, "env": env}
    return ok, ("OK" if ok else "FAIL"), details
