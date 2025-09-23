
"""Offline legacy InkDNA stamper & verifier (PDF only)."""
from .forge_offline import stamp_pdf
from .verify_offline import verify_pdf
__all__ = ["stamp_pdf", "verify_pdf"]
