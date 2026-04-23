#!/usr/bin/env python3
"""
cleanup_200dma.py — Remove report folders for stocks above their 200-day MA
"""
import os, json, shutil

REPORT_DIR = "/home/tonyho/workspace/invest/report"
AUDIT_FILE = "/home/tonyho/workspace/invest/scripts/dma_audit.json"

with open(AUDIT_FILE) as f:
    results = json.load(f)

to_remove = results["above_200"]
to_keep   = results["below_200"]
errors    = results["errors"]

print(f"Removing {len(to_remove)} folders (above 200-DMA)...\n")

removed = []
for ticker in to_remove:
    folder = os.path.join(REPORT_DIR, ticker)
    if os.path.isdir(folder):
        shutil.rmtree(folder)
        print(f"  [DELETED] {ticker}")
        removed.append(ticker)
    else:
        print(f"  [SKIP] {ticker} — folder not found")

print(f"\nKept {len(to_keep)} folders (below 200-DMA):")
for t in to_keep:
    print(f"  [KEPT] {t}")

if errors:
    print(f"\nSkipped {len(errors)} (no data / errors — kept for review):")
    for t in errors:
        print(f"  [REVIEW] {t}")

print(f"\n✅ Done. Deleted {len(removed)} folders.")
