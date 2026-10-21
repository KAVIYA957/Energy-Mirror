"""
download_iawe.py - Verified downloader for iAWE NILMTK HDF5 dataset.
Downloads iawe.h5 from Zenodo record 13917372 with MD5 and size verification.
"""

import os
import sys
import time
import hashlib
import urllib.request
import ssl

ZENODO_RECORD_ID = "13917372"
ZENODO_URL = "https://zenodo.org/records/13917372/files/iawe.h5?download=1"
EXPECTED_SIZE_BYTES = 427836094
EXPECTED_MD5 = "40c2a4486dde808ee814f4a9af520afb"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "iawe.h5")

def download_iawe():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if os.path.exists(OUTPUT_FILE):
        actual_size = os.path.getsize(OUTPUT_FILE)
        if actual_size == EXPECTED_SIZE_BYTES:
            print(f"File {OUTPUT_FILE} already exists with expected size ({actual_size} bytes).")
            print("Verifying MD5 checksum...")
            hasher = hashlib.md5()
            with open(OUTPUT_FILE, "rb") as f:
                while chunk := f.read(1024 * 1024 * 8):
                    hasher.update(chunk)
            actual_md5 = hasher.hexdigest()
            if actual_md5.lower() == EXPECTED_MD5.lower():
                print(f"MD5 verified: {actual_md5}")
                return True
            else:
                print(f"MD5 mismatch! Expected {EXPECTED_MD5}, got {actual_md5}. Re-downloading...")
                os.remove(OUTPUT_FILE)
        elif actual_size < EXPECTED_SIZE_BYTES:
            print(f"Partial file found ({actual_size} bytes / {actual_size/(1024*1024):.1f} MB). Resuming...")
        else:
            print(f"File size exceeds expected ({actual_size} > {EXPECTED_SIZE_BYTES}). Removing...")
            os.remove(OUTPUT_FILE)

    print(f"Connecting to Zenodo: {ZENODO_URL} ...")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    max_retries = 10
    retry = 0

    while retry < max_retries:
        try:
            current_bytes = os.path.getsize(OUTPUT_FILE) if os.path.exists(OUTPUT_FILE) else 0
            if current_bytes >= EXPECTED_SIZE_BYTES:
                break

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            if current_bytes > 0:
                headers["Range"] = f"bytes={current_bytes}-"
                print(f"Resuming download from byte {current_bytes} ({current_bytes / (1024*1024):.1f} MB)...")

            req = urllib.request.Request(ZENODO_URL, headers=headers)
            with urllib.request.urlopen(req, timeout=60, context=ctx) as response:
                mode = "ab" if current_bytes > 0 else "wb"
                with open(OUTPUT_FILE, mode) as out_file:
                    start_time = time.time()
                    downloaded_since_resume = 0
                    last_print = 0

                    while True:
                        chunk = response.read(1024 * 512)
                        if not chunk:
                            break
                        out_file.write(chunk)
                        downloaded_since_resume += len(chunk)
                        total_downloaded = current_bytes + downloaded_since_resume

                        elapsed = time.time() - start_time
                        if elapsed - last_print > 3 or total_downloaded >= EXPECTED_SIZE_BYTES:
                            percent = (total_downloaded / EXPECTED_SIZE_BYTES) * 100
                            speed_mb = (downloaded_since_resume / (1024 * 1024)) / max(elapsed, 0.001)
                            print(f"Progress: {total_downloaded / (1024*1024):.1f}/{EXPECTED_SIZE_BYTES / (1024*1024):.1f} MB ({percent:.1f}%) @ {speed_mb:.2f} MB/s")
                            last_print = elapsed

            final_size = os.path.getsize(OUTPUT_FILE)
            if final_size >= EXPECTED_SIZE_BYTES:
                print(f"File reached expected size: {final_size} bytes.")
                break
        except Exception as e:
            retry += 1
            print(f"Connection error ({e}). Retrying in 5 seconds (attempt {retry}/{max_retries})...")
            time.sleep(5)

    print("Verifying MD5 checksum of downloaded file...")
    hasher = hashlib.md5()
    with open(OUTPUT_FILE, "rb") as f:
        while chunk := f.read(1024 * 1024 * 8):
            hasher.update(chunk)

    final_md5 = hasher.hexdigest()
    final_size = os.path.getsize(OUTPUT_FILE)
    print(f"Saved to: {OUTPUT_FILE}")
    print(f"Final Size: {final_size} bytes (Expected: {EXPECTED_SIZE_BYTES})")
    print(f"Final MD5:  {final_md5} (Expected: {EXPECTED_MD5})")

    assert final_size == EXPECTED_SIZE_BYTES, f"Size mismatch: {final_size} != {EXPECTED_SIZE_BYTES}"
    assert final_md5.lower() == EXPECTED_MD5.lower(), f"MD5 mismatch: {final_md5} != {EXPECTED_MD5}"
    print("SUCCESS: iawe.h5 verified and ready for inspection.")
    return True

if __name__ == "__main__":
    download_iawe()
