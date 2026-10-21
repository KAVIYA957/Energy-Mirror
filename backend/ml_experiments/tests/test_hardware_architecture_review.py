"""
test_hardware_architecture_review.py - Unit tests validating the hardware architecture review JSON artifact.

Tests cover:
1. Structural integrity and JSON schema conformity of hardware_architecture_review.json
2. Verified manufacturer citations and primary-source URLs for ADE9153A, BL0942, PZEM-004T, and ESP32
3. Absence of reactive power (Q) register in PZEM-004T v3.0 documented specifications
4. ESP32 internal ADC non-linearity limitations documented and direct analog sensing prohibited
5. Isolation requirements for ADE9153A (UG-1253) documented
6. The 12W detectability budget: 3-part scientific distinction (accuracy vs resolution vs attribution)
7. Architectural comparison and selection rationales
8. Per-appliance Go/No-Go decision table completeness
9. Safety and non-energized compliance mandates
"""

import os
import sys
import json
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ML_EXPERIMENTS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
BACKEND_DIR = os.path.abspath(os.path.join(ML_EXPERIMENTS_DIR, ".."))

if ML_EXPERIMENTS_DIR not in sys.path:
    sys.path.insert(0, ML_EXPERIMENTS_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

REVIEW_JSON_PATH = os.path.join(
    ML_EXPERIMENTS_DIR, "results", "hardware_architecture_review.json"
)


class TestHardwareArchitectureReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assertTrue(
            os.path.exists(REVIEW_JSON_PATH),
            f"Hardware architecture review file not found at {REVIEW_JSON_PATH}",
        )
        with open(REVIEW_JSON_PATH, "r", encoding="utf-8") as f:
            cls.data = json.load(f)

    def test_metadata_and_non_energized_mandate(self):
        """Verify document metadata and non-energized status."""
        meta = self.data.get("metadata", {})
        self.assertEqual(meta.get("milestone"), "2C.6")
        self.assertEqual(meta.get("base_checkpoint"), "508dd44")
        self.assertIn("Non-Energized", meta.get("status", ""))

    def test_verified_components_citations_and_urls(self):
        """Verify candidate components have primary-source datasheets and verified status."""
        comps = self.data.get("verified_component_specifications", {})
        expected_keys = [
            "Analog_Devices_ADE9153A",
            "Shanghai_Belling_BL0942",
            "Peacefair_PZEM_004T_v3",
            "Espressif_ESP32_WROOM_32E",
        ]
        for key in expected_keys:
            self.assertIn(key, comps, f"Missing component specification: {key}")
            spec = comps[key]
            self.assertEqual(spec.get("verification_status"), "VERIFIED_PRIMARY_SOURCE")
            self.assertTrue(spec.get("primary_datasheet_url", "").startswith("https://"))

    def test_pzem_004t_reactive_power_limitation(self):
        """Verify that PZEM-004T v3.0 is documented as lacking native reactive power (Q)."""
        pzem = self.data["verified_component_specifications"]["Peacefair_PZEM_004T_v3"]
        quantities = pzem.get("quantities_measured", [])
        # Ensure reactive power is not claimed as a native measured quantity
        for q in quantities:
            self.assertNotIn("Reactive Power (VAR", q)

        # Check architecture comparison mentions this limitation
        arch_b = self.data["architecture_tradeoff_comparison"]["Architecture_B_Prebuilt_Module_PZEM_004T"]
        self.assertIn("NO REACTIVE POWER", arch_b.get("measurement_capabilities", ""))

    def test_esp32_adc_unsuitability_documented(self):
        """Verify ESP32 internal ADC is documented as unsuitable for direct AC metrology."""
        esp = self.data["verified_component_specifications"]["Espressif_ESP32_WROOM_32E"]
        adc_notes = esp.get("adc_performance_and_limitations", "")
        self.assertIn("MUST NEVER be used for direct analog", adc_notes)
        self.assertIn("DNL", adc_notes)
        self.assertIn("INL", adc_notes)

    def test_ade9153a_isolation_requirement_documented(self):
        """Verify ADE9153A is documented as non-isolated and requiring external galvanic isolation."""
        ade = self.data["verified_component_specifications"]["Analog_Devices_ADE9153A"]
        iso_notes = ade.get("isolation_and_safety_limitations", "")
        self.assertIn("REQUIRES external galvanic digital isolator", iso_notes)
        self.assertIn("EV-ADE9153ASHIELDZ does NOT include onboard isolation", iso_notes)

    def test_12w_detectability_three_part_distinction(self):
        """Verify 3-part scientific distinction: total power vs resolution vs unique attribution."""
        budget = self.data.get("the_12w_low_power_measurement_budget", {})
        distinction = budget.get("three_part_scientific_distinction", {})

        q1 = distinction.get("question_1_total_power_accuracy", {})
        q2 = distinction.get("question_2_resolve_small_power_change", {})
        q3 = distinction.get("question_3_unique_appliance_attribution", {})

        self.assertEqual(q1.get("can_instrument_measure_total_power_accurately"), "YES")
        self.assertEqual(q2.get("can_instrument_resolve_small_change"), "YES_IN_LABORATORY_ONLY")
        self.assertEqual(q3.get("can_change_be_uniquely_attributed_to_appliance"), "NO_FROM_AGGREGATE_ACTIVE_POWER")

    def test_voltage_sag_sensitivity_calculation(self):
        """Verify voltage sag sensitivity is quantitatively modeled (1% sag on 800W = 16W)."""
        sag = self.data["the_12w_low_power_measurement_budget"]["uncertainty_budget_components"]["grid_voltage_sag_sensitivity"]
        self.assertEqual(sag.get("apparent_power_change_from_1pct_sag_w"), 16.0)

    def test_architecture_tradeoff_verdicts(self):
        """Verify Architecture A is preferred for bench aggregate and Architecture B for ground truth."""
        arch_a = self.data["architecture_tradeoff_comparison"]["Architecture_A_Integrated_IC_ADE9153A"]
        arch_b = self.data["architecture_tradeoff_comparison"]["Architecture_B_Prebuilt_Module_PZEM_004T"]

        self.assertIn("PREFERRED ARCHITECTURE FOR RESEARCH TEST BENCH AGGREGATE", arch_a.get("verdict", ""))
        self.assertIn("PREFERRED ARCHITECTURE FOR APPLIANCE-LEVEL GROUND TRUTH", arch_b.get("verdict", ""))

    def test_go_no_go_decision_table_completeness(self):
        """Verify decision table covers all 4 target appliances with explicit statuses."""
        table = self.data.get("go_no_go_decision_table", {})
        expected_apps = [
            "bulb_01_12w_led",
            "fan_01_45w_ceiling_fan",
            "pump_01_75w_water_pump",
            "heater_01_140w_water_heater",
        ]
        for app in expected_apps:
            self.assertIn(app, table)
            self.assertIn("decision_status", table[app])

        # 12W must be NO_GO for aggregate active only
        self.assertIn("NO_GO", table["bulb_01_12w_led"]["decision_status"])
        # 75W must be GO
        self.assertIn("GO", table["pump_01_75w_water_pump"]["decision_status"])

    def test_safety_and_deployment_constraints(self):
        """Verify safety mandates require isolation, overcurrent protection, and software gate."""
        safety = self.data.get("safety_and_deployment_constraints", {})
        self.assertIn("ENABLE_HARDWARE_INGEST remains FALSE", safety.get("software_gate", ""))
        self.assertIn("Zero mains voltage connections", safety.get("non_energized_mandate", ""))
        self.assertIn("2.5 kV RMS", safety.get("galvanic_isolation", ""))


if __name__ == "__main__":
    unittest.main()
