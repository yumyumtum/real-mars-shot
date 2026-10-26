"""Rules-engine tests: published numbers, ordering, saves, win and loss."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from rms.data import DATA, references, science, tech_tree  # noqa: E402
from rms.events import apply_event  # noqa: E402
from rms.gates import gates  # noqa: E402
from rms.missions import plan_mission  # noqa: E402
from rms.physics import (  # noqa: E402
    conjunction_dose_mSv,
    consumables,
    delta_v,
    in_mars_window,
    lunar_cargo_imleo_t,
    mars_cargo_imleo_t,
    mass_ratio,
    people_export,
    shield_transmission,
    wastewater_kg_per_cm_d,
    window_center,
)
from rms.settlement import evaluate_month  # noqa: E402
from rms.state import load_game, new_state, public_view, save_game  # noqa: E402
from rms.turn import resolve  # noqa: E402
from rms.viz import habitat_svg, orbit_html, scene_card_svg  # noqa: E402
from rms.win import ember_checklist  # noqa: E402


def _walk_leaves(node, path=""):
    if isinstance(node, dict) and "value" in node and "source_id" in node:
        yield path, node
        return
    if isinstance(node, dict):
        for key, child in node.items():
            yield from _walk_leaves(child, f"{path}.{key}" if path else key)


class ScienceIntegrityTest(unittest.TestCase):
    def test_every_leaf_has_a_source_and_an_estimate_flag(self):
        refs = references()
        for path, leaf in _walk_leaves(science()):
            self.assertIn("estimate", leaf, path)
            self.assertIsInstance(leaf["estimate"], bool, path)
            self.assertIn(leaf["source_id"], refs, path)

    def test_reference_ids_appear_in_the_markdown(self):
        text = (ROOT / "REFERENCES.md").read_text(encoding="utf-8")
        for source_id in references():
            self.assertIn(source_id, text)

    def test_tech_prereqs_exist(self):
        tree = tech_tree()
        for tech_id, row in tree.items():
            for prereq in row["prereq"]:
                self.assertIn(prereq, tree, f"{tech_id} -> {prereq}")

    def test_data_files_are_json(self):
        for path in DATA.glob("*.json"):
            json.loads(path.read_text(encoding="utf-8"))


class RocketAndDoseTest(unittest.TestCase):
    def test_rocket_equation_identity(self):
        isp = 450.0
        ratio = 2.0
        dv = delta_v(isp, ratio)
        self.assertAlmostEqual(mass_ratio(dv, isp), 2.0, places=9)

    def test_lunar_cargo_factor_is_in_a_sane_band(self):
        result = lunar_cargo_imleo_t(1.0)
        self.assertGreater(result["imleo_t"], 4.0)
        self.assertLess(result["imleo_t"], 10.0)

    def test_mars_cargo_heavier_than_payload(self):
        result = mars_cargo_imleo_t(1.0)
        self.assertGreater(result["imleo_t"], 5.0)
        self.assertLess(result["imleo_t"], 20.0)

    def test_zero_extra_shielding_reproduces_published_cruise_product(self):
        self.assertEqual(shield_transmission(0.0), 1.0)
        dose = conjunction_dose_mSv(0.0, 0.0, outbound_days=180, surface_days=0, return_days=180)
        # 360 * 1.84 mSv = 662.4 mSv = 0.662 Sv, inside Zeitlin's 0.66 ± 0.12 Sv.
        self.assertAlmostEqual(dose["transit_mSv"], 662.4, places=6)
        self.assertGreaterEqual(dose["total_Sv"], 0.54)
        self.assertLessEqual(dose["total_Sv"], 0.78)

    def test_unshielded_conjunction_exceeds_cap_and_shielded_can_fit(self):
        bare = conjunction_dose_mSv(0.0, 0.0)
        self.assertGreater(bare["total_mSv"], 900)
        self.assertTrue(bare["exceeds_planning_cap"])
        shielded = conjunction_dose_mSv(20, 200)
        self.assertLess(shielded["total_mSv"], 600)
        self.assertGreater(bare["total_mSv"], shielded["total_mSv"])

    def test_ntr_campaign_sits_in_dra_band_and_chemical_sits_above_it(self):
        from rms.physics import campaign_imleo_t

        cons = consumables(6, 860, water_recovery=0.98, food_closure=0.0, o2_mode="sabatier")
        chemical = campaign_imleo_t(6, ntr=False, consumables_t=cons["shipped_life_support_t"])
        nuclear = campaign_imleo_t(6, ntr=True, consumables_t=cons["shipped_life_support_t"])
        self.assertGreater(chemical["imleo_t"], 1200)
        self.assertGreaterEqual(nuclear["imleo_t"], 800)
        self.assertLessEqual(nuclear["imleo_t"], 1200)
        self.assertGreater(chemical["imleo_t"], nuclear["imleo_t"])


class ConsumablesTest(unittest.TestCase):
    def test_wastewater_sum_and_ninety_eight_percent_makeup(self):
        wastewater = wastewater_kg_per_cm_d()
        self.assertAlmostEqual(wastewater, 0.101 + 2.946 + 1.42, places=9)
        crew, days = 6, 900
        closed = consumables(crew, days, water_recovery=0.98, o2_mode="open")
        self.assertAlmostEqual(closed["water_makeup_kg"], crew * days * wastewater * 0.02, places=6)
        # Food dominates a long open-loop manifest versus the water makeup at 98%.
        self.assertGreater(closed["food_shipped_kg"], closed["water_makeup_kg"] * 10)

    def test_open_water_is_much_heavier_than_closed(self):
        closed = consumables(6, 860, water_recovery=0.98, o2_mode="sabatier")
        opened = consumables(6, 860, water_recovery=0.0, o2_mode="open")
        self.assertGreater(opened["shipped_life_support_kg"], closed["shipped_life_support_kg"] * 2)

    def test_food_scales_with_crew_days(self):
        one = consumables(1, 10, water_recovery=1, food_closure=0, o2_mode="open")
        many = consumables(4, 10, water_recovery=1, food_closure=0, o2_mode="open")
        self.assertAlmostEqual(many["food_shipped_kg"], one["food_shipped_kg"] * 4, places=6)


class CalendarAndPeopleTest(unittest.TestCase):
    def test_windows_are_about_one_synodic_period_apart(self):
        first = window_center(0)
        second = window_center(1)
        self.assertEqual(first, date(2026, 11, 15))
        self.assertAlmostEqual((second - first).days, 779.94, delta=1.5)
        self.assertTrue(in_mars_window(first))
        midpoint = date.fromordinal(first.toordinal() + 390)
        self.assertFalse(in_mars_window(midpoint))

    def test_starting_fleet_cannot_export_a_city(self):
        state = new_state(user_id="people", seed=1)
        report = people_export(state["launch"], qualified=36, pipeline_per_year=8, years=10, ntr=False)
        self.assertLess(report["people"], 40)
        self.assertGreater(report["people"], 0)
        self.assertEqual(report["binding"], "mass_and_windows")


class OrderingTest(unittest.TestCase):
    def test_crewed_mars_at_the_start_is_not_quietly_allowed(self):
        state = new_state(user_id="order", seed=3)
        state["treasury_busd"] = 100
        plan = plan_mission(state, {"profile": "mars_crew_conjunction"})
        self.assertEqual(plan["class"], "impossible")
        self.assertTrue(any(item["id"] == "missing_tech" for item in plan["impossible"]))

    def test_crewed_mars_without_analogs_is_reckless_once_edl_exists(self):
        state = new_state(user_id="order2", seed=3)
        state["treasury_busd"] = 100
        state["tech"] = ["heavy_edl"]
        plan = plan_mission(state, {"profile": "mars_crew_conjunction"})
        self.assertEqual(plan["class"], "reckless")
        self.assertGreaterEqual(plan["failure_p"], 0.5)
        result = resolve(state, {"type": "mission", "profile": "mars_crew_conjunction"}, force_event="none")
        self.assertTrue(result["needs_confirmation"])
        self.assertEqual(state["clock"]["turn"], 0)
        self.assertEqual(state["sites"]["mars"]["crew_returned"], 0)

    def test_confirmed_premature_mars_crew_can_fail_without_a_win(self):
        state = new_state(user_id="order3", seed=3)
        state["treasury_busd"] = 100
        state["tech"] = ["heavy_edl"]
        result = resolve(
            state,
            {"type": "mission", "profile": "mars_crew_conjunction", "confirm_reckless": True},
            force_roll=1,
            force_event="none",
        )
        self.assertFalse(result["success"])
        self.assertNotEqual(state.get("outcome"), "win")
        self.assertGreater(state["crew"]["fatalities"], 0)

    def test_uncontained_release_is_game_over_only_after_confirmation(self):
        state = new_state(user_id="bio", seed=4)
        held = resolve(state, {"type": "biology", "organism": "cyanobacteria", "site": "earth_open"}, force_event="none")
        self.assertTrue(held["needs_confirmation"])
        self.assertIsNone(state["outcome"])
        done = resolve(
            state,
            {"type": "biology", "organism": "cyanobacteria", "site": "earth_open", "confirm_reckless": True},
            force_event="none",
        )
        self.assertEqual(done["outcome"], "game_over")
        self.assertEqual(done["outcome_reason"], "biosafety")

    def test_tardigrade_survival_does_not_count_as_establishment(self):
        state = new_state(user_id="tardi", seed=4)
        result = resolve(state, {"type": "biology", "organism": "tardigrade", "site": "earth_lab"}, force_event="none")
        self.assertTrue(result["survival_is_not_habitation"])
        self.assertFalse(result["established"])
        self.assertTrue(state["biology"]["tardigrade_exposure"])
        self.assertLess(gates(state)["bio_simulant"], True)


class SaveAndSecretTest(unittest.TestCase):
    def test_roundtrip_strips_secrets_and_writes_a_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["REALMARSSHOT_SAVE_DIR"] = tmp
            try:
                state = new_state(user_id="pilot", seed=11, language="en", director="Ada")
                self.assertIn("secrets", state)
                first = save_game(state, backup=False)
                state["clock"]["turn"] = 2
                second = save_game(state, backup=True)
                self.assertTrue(second["backup_path"])
                self.assertTrue(Path(second["backup_path"]).exists())
                loaded = load_game("pilot")
                self.assertTrue(loaded["exists"])
                self.assertNotIn("secrets", public_view(loaded["data"]))
                self.assertIn("secrets", loaded["data"])
                self.assertEqual(Path(first["save_path"]).name, "user-pilot.json")
            finally:
                os.environ.pop("REALMARSSHOT_SAVE_DIR", None)

    def test_path_traversal_user_id_is_rejected(self):
        with self.assertRaises(ValueError):
            new_state(user_id="../etc/passwd")

    def test_two_calls_with_the_same_seed_share_a_mole_assignment(self):
        a = new_state(user_id="a1", seed=99)
        b = new_state(user_id="b1", seed=99)
        self.assertEqual(a["secrets"], b["secrets"])


class OutcomeTest(unittest.TestCase):
    def _ember_moon(self):
        state = new_state(user_id="ember", seed=5, language="zh")
        moon = state["sites"]["moon"]
        moon.update({
            "population": 120,
            "births": 12,
            "trial": True,
            "independent_months": 60,
            "habitat": True,
            "greenhouse": True,
            "farms_m2": 7000,
            "fission_kwe": 4000,
            "polar": True,
            "shielding_g_cm2": 800,
            "spe_shelter": True,
            "water_recovery": 0.98,
            "sabatier_fraction": 0.47,
            "electrolysis": True,
            "industrial_closure": 0.85,
            "knowledge_archive": True,
            "genome_archive_donors": 10000,
            "isru_water_kg_year": 50000,
            "isru_o2_kg_year": 50000,
        })
        return state

    def test_new_game_is_not_a_win(self):
        state = new_state(user_id="fresh", seed=1)
        report = ember_checklist(state, "moon")
        self.assertFalse(report["win"])
        self.assertEqual(report["passed"], 0)

    def test_prepared_moon_meets_every_ember_item(self):
        state = self._ember_moon()
        month = evaluate_month("moon", state["sites"]["moon"])
        self.assertTrue(month["win_month"], month)
        report = ember_checklist(state, "moon")
        self.assertTrue(report["win"], [item for item in report["items"] if not item["ok"]])

    def test_thin_shielding_blocks_the_win(self):
        state = self._ember_moon()
        state["sites"]["moon"]["shielding_g_cm2"] = 0
        self.assertFalse(ember_checklist(state, "moon")["win"])

    def test_resolving_a_turn_on_a_finished_seed_records_the_win(self):
        state = self._ember_moon()
        result = resolve(state, {"type": "wait", "months": 1}, force_event="none")
        self.assertEqual(result["outcome"], "win")
        self.assertEqual(state["outcome_site"], "moon")

    def test_earth_collapse_is_a_loss_until_an_ember_exists(self):
        state = new_state(user_id="collapse", seed=2)
        state["earth_stability"] = 1
        apply_event(state, "climate_shock", 10)
        result = resolve(state, {"type": "wait", "months": 1}, force_event="none")
        self.assertEqual(result["outcome"], "game_over")
        self.assertEqual(result["outcome_reason"], "earth_collapse")

    def test_a_live_ember_wins_even_if_earth_stability_hits_zero(self):
        state = self._ember_moon()
        state["earth_stability"] = 0
        result = resolve(state, {"type": "status"})
        # status does not re-check. A time-advancing turn does, and win is tested first.
        result = resolve(state, {"type": "wait", "months": 1}, force_event="none")
        self.assertEqual(result["outcome"], "win")

    def test_shortfall_without_a_rescue_ends_the_outpost(self):
        state = new_state(user_id="die", seed=8)
        state["earth_stability"] = 10
        state["treasury_busd"] = 0.1
        moon = state["sites"]["moon"]
        moon["population"] = 3
        moon["habitat"] = True
        moon["trial"] = True
        result = resolve(state, {"type": "wait", "months": 4}, force_event="none")
        self.assertEqual(result["outcome"], "game_over")
        self.assertIn("extinction", result["outcome_reason"])


class FlowTest(unittest.TestCase):
    def test_first_moves_are_an_analog_not_a_rocket(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["REALMARSSHOT_SAVE_DIR"] = tmp
            try:
                state = new_state(user_id="sample", language="zh", director="顾长川", program="火种计划", seed=7)
                save_game(state, backup=False)
                built = resolve(state, {"type": "facility", "facility": "analog_habitat"}, force_roll=90, force_event="quiet_quarter")
                self.assertTrue(built["ok"])
                self.assertIn("analog_habitat", state["facilities"])
                run = resolve(state, {"type": "analog", "days": 30}, force_roll=99, force_event="none")
                self.assertTrue(run["success"])
                self.assertGreaterEqual(state["eclss"]["closed_habitat_days_record"], 30)
                self.assertTrue(gates(state)["analog_30"])
                self.assertNotIn("secrets", json.dumps({k: built[k] for k in built if k != "public_state"}))
            finally:
                os.environ.pop("REALMARSSHOT_SAVE_DIR", None)

    def test_committed_example_save_matches_the_engine(self):
        example = json.loads((ROOT / "examples" / "save-example.json").read_text(encoding="utf-8"))
        state = new_state(user_id="sample", language="zh", director="顾长川", program="火种计划", seed=7)
        resolve(state, {"type": "facility", "facility": "analog_habitat"}, force_roll=90, force_event="quiet_quarter")
        resolve(state, {"type": "analog", "days": 30}, force_roll=99, force_event="none")
        self.assertEqual(example["game"], "realmarsshot")
        self.assertEqual(example["language"], "zh")
        self.assertEqual(example["clock"], state["clock"])
        self.assertEqual(example["treasury_busd"], state["treasury_busd"])
        self.assertEqual(example["public_opinion"], state["public_opinion"])
        self.assertEqual(example["political_capital"], state["political_capital"])
        self.assertEqual(example["earth_stability"], state["earth_stability"])
        self.assertEqual(example["dissent"], state["dissent"])
        self.assertEqual(example["eclss"]["closed_habitat_days_record"], state["eclss"]["closed_habitat_days_record"])
        self.assertIn("analog_habitat", example["facilities"])
        self.assertIsNone(example["last_event"])
        self.assertIsNone(example["secrets"]["mole"])
        report = ember_checklist(example, "moon")
        self.assertFalse(report["win"])

    def test_scene_and_orbit_artifacts_exist(self):
        state = new_state(user_id="art", seed=1)
        svg = scene_card_svg(state, {"phase": "earth_analog", "action": "brief", "summary_lines": ["a", "b"]})
        self.assertIn("scene-card", svg)
        html = orbit_html()
        self.assertIn("fallback-canvas", html)
        self.assertIn("three.module.js", html)
        self.assertIn("habitat-section", habitat_svg())


if __name__ == "__main__":
    unittest.main()
