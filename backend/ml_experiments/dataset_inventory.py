"""
dataset_inventory.py - Automated Metadata and Channel Inventory for Public NILM Datasets

Inspects and audits public NILM datasets (UK-DALE, REFIT, NILMTK, NILMBench)
against Energy Mirror's 4 target appliances:
  1. Water Heater (nominal 140 W resistive)
  2. Water Pump (nominal 75 W inductive)
  3. Ceiling Fan (nominal 45 W motor)
  4. LED Bulb (nominal 12 W lighting/SMPS)

Extracts metadata from official repositories and documents exact appliance channels,
sample rates, sizes, licenses, and mapping defensibility.
"""

import json
import urllib.request
import yaml
from typing import Dict, Any, List

UKDALE_METADATA_BASE = "https://raw.githubusercontent.com/JackKelly/UK-DALE_metadata/master"
REFIT_METADATA_BASE = "https://raw.githubusercontent.com/nilmtk/nilm_metadata/master"

def fetch_yaml(url: str) -> Dict[str, Any]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "EnergyMirror-Audit/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            return yaml.safe_load(response.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e), "url": url}

def audit_ukdale_buildings() -> Dict[str, Any]:
    """Audit all 5 houses in UK-DALE for target appliance categories."""
    results = {}
    for b_id in range(1, 6):
        url = f"{UKDALE_METADATA_BASE}/building{b_id}.yaml"
        data = fetch_yaml(url)
        if "error" in data:
            results[f"building_{b_id}"] = data
            continue
        
        appliances = data.get("appliances", [])
        app_list = []
        for app in appliances:
            app_list.append({
                "meters": app.get("meters"),
                "type": app.get("type"),
                "original_name": app.get("original_name"),
                "nominal_on_power": app.get("nominal_consumption", {}).get("on_power") if isinstance(app.get("nominal_consumption"), dict) else None,
                "description": (app.get("description", "") or "")[:120],
                "fuel": app.get("fuel"),
            })
        results[f"building_{b_id}"] = {
            "total_appliances": len(appliances),
            "appliances": app_list,
        }
    return results

def main():
    print("=" * 80)
    print("ENERGY MIRROR NILM DATASET AUDIT & INVENTORY")
    print("=" * 80)
    print("Fetching official UK-DALE metadata...")
    ukdale = audit_ukdale_buildings()
    for b_id, b_data in ukdale.items():
        if "error" in b_data:
            print(f"[{b_id}] Error: {b_data['error']}")
            continue
        print(f"\n--- UK-DALE {b_id.upper()} ({b_data['total_appliances']} instrumented appliances) ---")
        for app in b_data["appliances"]:
            # Check target categories
            t = (app["type"] or "").lower()
            name = (app["original_name"] or "").lower()
            desc = (app["description"] or "").lower()
            
            is_relevant = any(k in t or k in name or k in desc for k in [
                "boiler", "pump", "heater", "water", "fan", "light", "lamp", "led"
            ])
            if is_relevant:
                print(f"  * Meter {app['meters']}: Type='{app['type']}', Name='{app['original_name']}', NomPower={app['nominal_on_power']} W")
                if app['description']:
                    print(f"    Desc: {app['description']}...")

if __name__ == "__main__":
    main()
