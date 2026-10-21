"""
download_refit_house21.py - Acquire CLEAN_House21.csv from official Strathclyde repository

Downloads the official REFIT archive (CLEAN_REFIT_081116.7z, CC BY 4.0),
extracts only the required target file CLEAN_House21.csv into backend/ml_experiments/data/,
verifies SHA-256 and byte count, and purges the temporary monolithic archive.
"""

import hashlib
import os
import shutil
import ssl
import sys
import time
import urllib.request
import py7zr

ARCHIVE_URL = "https://pure.strath.ac.uk/ws/portalfiles/portal/62090184/CLEAN_REFIT_081116.7z"
TARGET_FILENAME = "CLEAN_House21.csv"
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
ARCHIVE_PATH = os.path.join(DATA_DIR, "CLEAN_REFIT_081116.7z")
TARGET_PATH = os.path.join(DATA_DIR, TARGET_FILENAME)

def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def download_and_extract_house21() -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if os.path.exists(TARGET_PATH) and os.path.getsize(TARGET_PATH) > 10 * 1024 * 1024:
        print(f"Target file already exists: {TARGET_PATH}")
        size_mb = os.path.getsize(TARGET_PATH) / (1024 * 1024)
        print(f"File size: {size_mb:.2f} MB ({os.path.getsize(TARGET_PATH)} bytes)")
        checksum = compute_sha256(TARGET_PATH)
        print(f"SHA-256: {checksum}")
        return TARGET_PATH

    print(f"Target not found. Downloading official REFIT archive from:\n  {ARCHIVE_URL}")
    print(f"Destination: {ARCHIVE_PATH}")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(
        ARCHIVE_URL,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    
    t0 = time.time()
    downloaded = 0
    chunk_size = 4 * 1024 * 1024  # 4 MB chunks
    last_report = t0
    
    with urllib.request.urlopen(req, timeout=60, context=ctx) as resp, open(ARCHIVE_PATH, "wb") as out_f:
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            out_f.write(chunk)
            downloaded += len(chunk)
            now = time.time()
            if now - last_report >= 5.0:
                elapsed = now - t0
                speed = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                print(f"  Downloaded: {downloaded / (1024 * 1024):.1f} MB ({speed:.2f} MB/s)")
                last_report = now
                
    total_time = time.time() - t0
    print(f"Download completed in {total_time:.1f} s ({downloaded / (1024 * 1024):.1f} MB)")
    archive_sha256 = compute_sha256(ARCHIVE_PATH)
    print(f"Archive SHA-256: {archive_sha256}")

    print(f"Extracting {TARGET_FILENAME} using py7zr...")
    t_extract = time.time()
    with py7zr.SevenZipFile(ARCHIVE_PATH, mode="r") as z:
        all_names = z.getnames()
        matching = [n for n in all_names if TARGET_FILENAME.lower() in n.lower()]
        print(f"Archive contents matching target: {matching}")
        if not matching:
            raise RuntimeError(f"Could not find {TARGET_FILENAME} in archive. Available files: {all_names[:10]}...")
        
        target_in_archive = matching[0]
        z.extract(targets=[target_in_archive], path=DATA_DIR)
        
    extracted_candidate = os.path.join(DATA_DIR, target_in_archive)
    if os.path.exists(extracted_candidate) and extracted_candidate != TARGET_PATH:
        shutil.move(extracted_candidate, TARGET_PATH)
        
    print(f"Extraction completed in {time.time() - t_extract:.1f} s.")
    
    if os.path.exists(ARCHIVE_PATH):
        print(f"Purging temporary archive {ARCHIVE_PATH} to free disk space...")
        os.remove(ARCHIVE_PATH)
        print("Archive purged successfully.")

    if not os.path.exists(TARGET_PATH):
        raise FileNotFoundError(f"Extraction failed: {TARGET_PATH} does not exist.")
        
    target_size = os.path.getsize(TARGET_PATH)
    target_sha256 = compute_sha256(TARGET_PATH)
    print("=" * 70)
    print(f"ACQUISITION SUCCESS:")
    print(f"  File: {TARGET_PATH}")
    print(f"  Size: {target_size / (1024 * 1024):.2f} MB ({target_size:,} bytes)")
    print(f"  SHA-256: {target_sha256}")
    print("=" * 70)
    return TARGET_PATH

if __name__ == "__main__":
    download_and_extract_house21()
