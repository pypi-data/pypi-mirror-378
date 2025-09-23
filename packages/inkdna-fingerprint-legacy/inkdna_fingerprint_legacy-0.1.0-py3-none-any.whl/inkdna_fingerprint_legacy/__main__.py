
from __future__ import annotations
import argparse
from pathlib import Path
from .forge_offline import stamp_pdf
from .verify_offline import verify_pdf

def main():
    ap = argparse.ArgumentParser(prog="inkdna-legacy", description="Offline InkDNA legacy stamper (no keys, no API).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    enc = sub.add_parser("stamp", help="Stamp a PDF with a code (offline)")
    enc.add_argument("pdf", type=Path)
    enc.add_argument("--code", required=True)
    enc.add_argument("-o", "--out", type=Path)

    ver = sub.add_parser("verify", help="Verify a stamped PDF (offline)")
    ver.add_argument("pdf", type=Path)
    ver.add_argument("--code", help="Optional expected code to match")

    args = ap.parse_args()
    if args.cmd == "stamp":
        out = args.out or args.pdf.with_name(args.pdf.stem + "_inkdna.pdf")
        stamp_pdf(args.pdf, out, code=args.code)
        print(f"Stamped -> {out}")
    else:
        ok, msg, info = verify_pdf(args.pdf, code=args.code)
        print(msg)
        if not ok:
            print(info)

if __name__ == "__main__":
    main()
