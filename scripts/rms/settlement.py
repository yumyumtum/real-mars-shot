"""Monthly resource balance for an off-world site.

The independence clock advances only on a month that meets the ember
thresholds with local production. Stores can keep people alive and still
not count. A resupply resets the clock.
"""

from __future__ import annotations

from typing import Any

from rms.data import V
from rms.physics import (
    annual_habitat_dose_mSv,
    local_food_kg_per_day,
    power_demand_kwe,
    power_worst_kwe,
    wastewater_kg_per_cm_d,
)


def _o2_and_water(site: dict[str, Any], crew: int, days: float) -> dict[str, float]:
    o2_need = crew * V("human", "o2_kg_per_cm_d") * days
    food_dry = local_food_kg_per_day(site) * days
    plants = min(o2_need, food_dry * V("human", "o2_from_plants_kg_per_kg_dry_food"))
    o2_isru = float(site.get("isru_o2_kg_year", 0.0)) * days / 365.25
    renew_water = float(site.get("isru_water_kg_year", 0.0)) * days / 365.25
    recovery = float(site.get("water_recovery", 0.0))
    makeup = crew * wastewater_kg_per_cm_d() * days * (1.0 - recovery)
    water_left = renew_water - makeup
    extra_o2 = 0.0
    if site.get("electrolysis") and water_left > 0:
        sab = float(site.get("sabatier_fraction", 0.0))
        water_per_o2 = (18.0 / 16.0) * (1.0 - sab if sab > 0 else 1.0)
        extra_o2 = water_left / water_per_o2
    return {
        "o2_need": o2_need,
        "o2_renew": o2_isru + plants + extra_o2,
        "food_dry": food_dry,
        "food_need": crew * V("human", "food_solids_kg_per_cm_d") * days,
        "makeup": makeup,
        "renew_water": renew_water,
        "water_left_after_makeup": water_left,
    }


def evaluate_month(site_name: str, site: dict[str, Any]) -> dict[str, Any]:
    crew = int(site.get("population", 0))
    demand = power_demand_kwe(site)
    worst = power_worst_kwe(site_name, site)
    power_ratio = (worst / demand) if demand > 0 else (1.0 if crew == 0 else 0.0)
    if crew <= 0:
        return {
            "crew": 0,
            "power_ratio": power_ratio,
            "survival": True,
            "win_month": False,
            "reason": "uncrewed",
        }
    flows = _o2_and_water(site, crew, 30.0)
    food_ratio = flows["food_dry"] / flows["food_need"] if flows["food_need"] else 1.0
    o2_ratio = flows["o2_renew"] / flows["o2_need"] if flows["o2_need"] else 1.0
    water_ok = flows["water_left_after_makeup"] >= -1e-9
    dose = annual_habitat_dose_mSv(site_name, float(site.get("shielding_g_cm2", 0.0)))
    survival = (
        food_ratio >= 1.0 - 1e-9
        and o2_ratio >= 1.0 - 1e-9
        and water_ok
        and power_ratio >= 1.0 - 1e-9
    )
    win_month = (
        food_ratio >= V("win", "food_local_fraction") - 1e-9
        and o2_ratio >= V("win", "o2_margin") - 1e-9
        and water_ok
        and power_ratio >= V("win", "power_margin_worst_case") - 1e-9
        and dose["meets_target"]
        and float(site.get("water_recovery", 0.0)) >= V("win", "water_recovery_min") - 1e-9
    )
    return {
        "crew": crew,
        "power_ratio": power_ratio,
        "power_worst_kwe": worst,
        "power_demand_kwe": demand,
        "food_ratio": food_ratio,
        "o2_ratio": o2_ratio,
        "water_covered_by_isru": water_ok,
        "dose": dose,
        "survival": survival and True,
        "win_month": win_month,
        "flows": flows,
    }


def apply_month(state: dict[str, Any], site_name: str, resupply: bool = False) -> dict[str, Any]:
    site = state["sites"][site_name]
    before = int(site.get("dust_storm_months_left", 0))
    report = evaluate_month(site_name, site)
    report["site"] = site_name
    if resupply and site.get("trial"):
        site["independent_months"] = 0
        report["clock"] = "reset_resupply"
    elif site.get("trial") and int(site.get("population", 0)) > 0:
        if report["win_month"] and not resupply:
            site["independent_months"] = int(site.get("independent_months", 0)) + 1
            report["clock"] = "advanced"
        elif not report["survival"]:
            site["independent_months"] = 0
            report["clock"] = "reset_shortfall"
            _harm(state, site_name, report)
        else:
            report["clock"] = "held"
    if before > 0:
        site["dust_storm_months_left"] = before - 1
        if site["dust_storm_months_left"] == 0 and site.get("robots"):
            if site.get("rtg") or float(site.get("fission_kwe", 0)) > 0 or float(site.get("battery_kwe", 0)) > 0:
                site["survived_dust_season"] = True
                report["dust_season_survived"] = True
    return report


def _harm(state: dict[str, Any], site_name: str, report: dict[str, Any]) -> None:
    site = state["sites"][site_name]
    population = int(site.get("population", 0))
    if population <= 0:
        return
    power_ratio = float(report.get("power_ratio", 0))
    loss = 1 if power_ratio > 0.3 else max(1, population // 2)
    loss = min(population, loss)
    site["population"] = population - loss
    site["fatalities"] = int(site.get("fatalities", 0)) + loss
    state["public_opinion"] = max(0, state["public_opinion"] - 6)
    report["casualties"] = loss
    if site["population"] == 0 and site.get("trial"):
        can_rescue = state["earth_stability"] >= 25 and state["treasury_busd"] > 0.5
        if can_rescue:
            site["trial"] = False
            site["evacuated"] = True
            state["treasury_busd"] -= 0.4
            report["evacuated"] = True
        else:
            site["extinct"] = True
            report["extinct"] = True
