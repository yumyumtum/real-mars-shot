"""Measurable ember checklist. The narrator does not get to declare victory."""

from __future__ import annotations

from typing import Any

from rms.data import V
from rms.physics import annual_habitat_dose_mSv
from rms.settlement import evaluate_month


def _item(item_id: str, ok: bool, current: Any, target: Any, estimate: bool, source_id: str, zh: str, en: str) -> dict[str, Any]:
    return {
        "id": item_id,
        "ok": bool(ok),
        "current": current,
        "target": target,
        "estimate": estimate,
        "source_id": source_id,
        "zh": zh,
        "en": en,
    }


def ember_checklist(state: dict[str, Any], site_name: str) -> dict[str, Any]:
    site = state["sites"][site_name]
    month = evaluate_month(site_name, site)
    dose = annual_habitat_dose_mSv(site_name, float(site.get("shielding_g_cm2", 0.0)))
    pop = int(site.get("population", 0))
    births = int(site.get("births", 0))
    donors = int(site.get("genome_archive_donors", 0))
    archive_path = pop >= int(V("win", "population_with_archive")) and births >= int(V("win", "births_with_archive")) and donors >= int(V("win", "genome_archive_donors"))
    census_path = pop >= int(V("win", "population_without_archive")) and births >= int(V("win", "births_with_archive"))
    people_ok = archive_path or census_path
    items = [
        _item(
            "independence_months",
            int(site.get("independent_months", 0)) >= int(V("win", "independence_years") * 12),
            int(site.get("independent_months", 0)),
            int(V("win", "independence_years") * 12),
            False,
            "game_calibration",
            "连续本地盈余月数（五年，且不是靠库存）",
            "Consecutive months of local surplus (five years, not a stockpile)",
        ),
        _item(
            "water_recovery",
            float(site.get("water_recovery", 0.0)) >= V("win", "water_recovery_min"),
            round(float(site.get("water_recovery", 0.0)), 3),
            V("win", "water_recovery_min"),
            False,
            "nasa_iss_water_2023",
            "运行中的水回收率",
            "Operating water recovery",
        ),
        _item(
            "water_isru",
            bool(month.get("water_covered_by_isru")),
            month.get("water_covered_by_isru"),
            True,
            False,
            "game_calibration",
            "损耗由本地水覆盖，而不是地球补水",
            "Losses covered by local water, not an Earth top-up",
        ),
        _item(
            "oxygen_margin",
            float(month.get("o2_ratio", 0.0)) >= V("win", "o2_margin"),
            round(float(month.get("o2_ratio", 0.0)), 3),
            V("win", "o2_margin"),
            True,
            "nasa_bvad_2022",
            "氧气产量 / 代谢需求",
            "Oxygen production / metabolic demand",
        ),
        _item(
            "food",
            float(month.get("food_ratio", 0.0)) >= V("win", "food_local_fraction"),
            round(float(month.get("food_ratio", 0.0)), 3),
            V("win", "food_local_fraction"),
            True,
            "game_calibration",
            "本地干食占需求的比例",
            "Local dry food as a fraction of demand",
        ),
        _item(
            "power",
            float(month.get("power_ratio", 0.0)) >= V("win", "power_margin_worst_case"),
            round(float(month.get("power_ratio", 0.0)), 3),
            V("win", "power_margin_worst_case"),
            True,
            "game_calibration",
            "最坏情况功率裕度（月夜或尘暴）",
            "Worst-case power margin (lunar night or dust storm)",
        ),
        _item(
            "dose",
            bool(dose["meets_target"]),
            round(float(dose["mSv_per_year"]), 2),
            dose["target_mSv_per_year"],
            True,
            "icrp103",
            "栖息地年剂量（毫希沃特 / 年）",
            "Habitat annual dose (mSv/year)",
        ),
        _item(
            "people",
            people_ok,
            {"population": pop, "births": births, "donors": donors},
            {
                "archive_path": {
                    "population": int(V("win", "population_with_archive")),
                    "births": int(V("win", "births_with_archive")),
                    "donors": int(V("win", "genome_archive_donors")),
                },
                "census_path_population": int(V("win", "population_without_archive")),
            },
            True,
            "smith2014",
            "人口：100 名居民 + 10 次地外出生 + 1 万名供体档案，或约 1.4 万名居民",
            "People: 100 residents + 10 off-world births + a 10,000-donor archive, or about 14,000 residents",
        ),
        _item(
            "industry",
            float(site.get("industrial_closure", 0.0)) >= V("win", "industrial_closure"),
            round(float(site.get("industrial_closure", 0.0)), 3),
            V("win", "industrial_closure"),
            False,
            "game_calibration",
            "关键备件可在本地制造的比例",
            "Fraction of critical spare parts made locally",
        ),
        _item(
            "knowledge",
            bool(site.get("knowledge_archive")),
            bool(site.get("knowledge_archive")),
            True,
            False,
            "game_calibration",
            "制造与农业知识的本地冗余档案",
            "A local redundant archive of making and growing",
        ),
    ]
    return {
        "site": site_name,
        "win": all(item["ok"] for item in items),
        "passed": sum(1 for item in items if item["ok"]),
        "total": len(items),
        "items": items,
        "month": {key: month[key] for key in month if key != "flows"},
    }


def earth_alive_for_foothold(state: dict[str, Any]) -> bool:
    """A foothold is a living branch of Earth, so Earth itself has to still be there."""
    if float(state.get("earth_stability", 0)) <= 0:
        return False
    if state.get("biology", {}).get("uncontained"):
        return False
    collapsed = (
        int(state.get("deficit_months", 0)) >= 12
        and float(state.get("political_capital", 0)) <= 0
        and float(state.get("public_opinion", 0)) <= 15
    )
    return not collapsed


_PATHS = (
    ("human", "foothold_500", "inhabited_days", "foothold_days"),
    ("biology", "foothold_biology", "biology_closed_months", "foothold_biology_months"),
    ("machine", "foothold_machine", "machine_tended_months", "foothold_machine_months"),
)

def foothold_progress(state: dict[str, Any]) -> list[dict[str, Any]]:
    """Best site for each path. Mars wins a tie, because 500 days is a Mars stay."""
    rows = []
    block = state.get("footholds") or {}
    for key, reason, field, target_key in _PATHS:
        target = int(V("win", target_key))
        best_site = "mars"
        best_value = int(state["sites"]["mars"].get(field, 0))
        for site_name in ("moon", "freespace"):
            value = int(state["sites"][site_name].get(field, 0))
            if value > best_value:
                best_site = site_name
                best_value = value
        record = block.get(key) or {}
        site_name = record["site"] if record.get("achieved") and record.get("site") else best_site
        current = int(state["sites"][site_name].get(field, 0))
        rows.append({
            "path": key,
            "reason": reason,
            "site": site_name,
            "progress": int(record.get("progress") or current),
            "current": current,
            "target": target,
            "achieved": bool(record.get("achieved")),
            "unit": "days" if key == "human" else "months",
        })
    return rows


def consider_footholds(state: dict[str, Any]) -> list[dict[str, Any]]:
    """Record each first-tier win once. Does not set state['outcome']."""
    if not earth_alive_for_foothold(state):
        return []
    block = state.setdefault("footholds", {})
    announced = []
    for key, reason, field, target_key in _PATHS:
        row = block.setdefault(key, {"achieved": False, "announced": False, "just_announced": False, "reason": reason, "site": None, "progress": 0})
        if row.get("achieved"):
            continue
        target = float(V("win", target_key))
        best: tuple[str, float] | None = None
        for site_name in ("mars", "moon", "freespace"):
            progress = float(state["sites"][site_name].get(field, 0))
            if progress + 1e-9 >= target and (best is None or progress > best[1]):
                best = (site_name, progress)
        if best is None:
            continue
        row.update({
            "achieved": True,
            "announced": True,
            "just_announced": True,
            "reason": reason,
            "site": best[0],
            "progress": int(best[1]),
        })
        announced.append(dict(row))
    return announced


def any_ember(state: dict[str, Any]) -> dict[str, Any] | None:
    for site_name in ("moon", "mars", "freespace"):
        report = ember_checklist(state, site_name)
        if report["win"]:
            return report
    return None
