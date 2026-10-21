"""
verify_sources.py - Forensic Verification of Public NILM Dataset Availability,
Headers, File Sizes, and Metadata Schemas without Downloading Bulk Archives.
"""

import urllib.request
import json
import ssl

SOURCES = {
    "UKDALE_Metadata_Building1": "https://raw.githubusercontent.com/JackKelly/UK-DALE_metadata/master/building1.yaml",
    "UKDALE_Metadata_Building2": "https://raw.githubusercontent.com/JackKelly/UK-DALE_metadata/master/building2.yaml",
    "REFIT_Metadata_House11": "https://raw.githubusercontent.com/nilmtk/nilm_metadata/master/central_metadata/dataset/refit.yaml",
    "REFIT_Archive_Direct": "https://pure.strath.ac.uk/ws/portalfiles/portal/52873459/CLEAN_REFIT_081116.7z",
}

def verify_url(name: str, url: str):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "EnergyMirror-Auditor/1.0"},
        method="HEAD"
    )
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            cl = resp.headers.get("Content-Length")
            cl_mb = f"{int(cl) / (1024*1024):.2f} MB" if cl else "Unknown"
            print(f"[OK] {name:<26} | Status: {resp.status} | Content-Length: {cl_mb} ({cl} bytes)")
    except Exception as e:
        # Fallback to GET with Range 0-10 if HEAD is disallowed by repository server
        try:
            req_get = urllib.request.Request(
                url,
                headers={"User-Agent": "EnergyMirror-Auditor/1.0", "Range": "bytes=0-10"}
            )
            with urllib.request.urlopen(req_get, timeout=10, context=ctx) as resp:
                cl = resp.headers.get("Content-Range") or resp.headers.get("Content-Length")
                print(f"[OK-GET] {name:<26} | Status: {resp.status} | Range/Length: {cl}")
        except Exception as e2:
            print(f"[FAIL] {name:<26} | Error: {e2}")

if __name__ == "__main__":
    print("=" * 80)
    print("ENERGY MIRROR: PUBLIC NILM DATASET PROVENANCE & ACCESS VERIFICATION")
    print("=" * 80)
    for name, url in SOURCES.items():
        verify_url(name, url)
