"""Player-facing numbers. Narration may add scene; it may not replace these figures."""

from __future__ import annotations

from typing import Any

from rms.data import i18n
from rms.gates import current_phase, gates
from rms.physics import (
    annual_imleo_t,
    comms_delay,
    conjunction_dose_mSv,
    consumables,
    mass_ratio,
    next_window_label,
    people_export,
    propellant_kg,
)
from rms.state import public_view, ready_crew
from rms.win import ember_checklist, foothold_progress

SUGGESTIONS: dict[str, list[dict[str, Any]]] = {
    "earth_analog": [
        {"type": "facility", "facility": "analog_habitat"},
        {"type": "research", "tech_id": "vacuum_thermal_lab"},
        {"type": "research", "tech_id": "analog_operations"},
        {"type": "analog", "days": 30},
    ],
    "machines": [
        {"type": "research", "tech_id": "precision_robotics"},
        {"type": "mission", "profile": "lunar_probe"},
        {"type": "research", "tech_id": "launch_abort"},
    ],
    "moon": [
        {"type": "research", "tech_id": "lunar_isru_pilot"},
        {"type": "mission", "profile": "lunar_isru_demo"},
        {"type": "research", "tech_id": "storm_shelter"},
    ],
    "biology": [
        {"type": "research", "tech_id": "simulant_biology"},
        {"type": "biology", "organism": "cyanobacteria", "site": "earth_simulant"},
        {"type": "research", "tech_id": "genome_bank"},
    ],
    "cislunar_crew": [
        {"type": "mission", "profile": "lunar_crew_sortie"},
        {"type": "mission", "profile": "lunar_cargo"},
        {"type": "research", "tech_id": "buried_habitat"},
    ],
    "mars_cargo": [
        {"type": "mission", "profile": "mars_relay"},
        {"type": "mission", "profile": "mars_robot"},
        {"type": "research", "tech_id": "heavy_edl"},
    ],
    "mars_outpost": [
        {"type": "mission", "profile": "mars_crew_conjunction"},
        {"type": "mission", "profile": "mars_isru"},
        {"type": "research", "tech_id": "industrial_isru"},
    ],
    "independence": [
        {"type": "independence", "site": "moon"},
        {"type": "mission", "profile": "greenhouse", "destination": "moon"},
        {"type": "mission", "profile": "reactor_module", "destination": "moon"},
    ],
    "ember": [],
}


def compute_answer(state: dict[str, Any] | None, action: dict[str, Any]) -> dict[str, Any]:
    topic = action.get("topic", "rocket")
    if topic == "rocket":
        isp = float(action.get("isp", 450))
        delta = float(action.get("dv", 3600))
        payload = float(action.get("payload_kg", 10000))
        return propellant_kg(payload, delta, isp) | {"mass_ratio_check": mass_ratio(delta, isp)}
    if topic == "dose":
        return conjunction_dose_mSv(
            float(action.get("transit_shield", 0)),
            float(action.get("surface_shield", 0)),
        )
    if topic == "consumables":
        return consumables(
            int(action.get("crew", 6)),
            float(action.get("days", 860)),
            water_recovery=float(action.get("water_recovery", 0.98)),
            food_closure=float(action.get("food_closure", 0.0)),
            o2_mode=str(action.get("o2_mode", "sabatier")),
        )
    if topic == "comms":
        return comms_delay()
    if topic == "people":
        if state is None:
            raise ValueError("people capacity needs a save")
        return people_export(
            state["launch"],
            qualified=len(ready_crew(state)),
            pipeline_per_year=state["crew"]["pipeline_per_year"],
            ntr="ntr_stage" in state["tech"],
        )
    if topic == "windows":
        year = int(action.get("year") or (state["clock"]["year"] if state else 2026))
        month = int(action.get("month") or (state["clock"]["month"] if state else 1))
        return {"next_window": next_window_label(year, month), "synodic_days": 779.94, "source_id": "nasa_dra5_2009"}
    raise ValueError(f"unknown topic {topic}")


def _suggestions(state: dict[str, Any]) -> list[dict[str, Any]]:
    phase = current_phase(state)
    options = []
    if "analog_habitat" not in state["facilities"] and phase == "earth_analog":
        options.append({"type": "facility", "facility": "analog_habitat"})
    for item in SUGGESTIONS.get(phase, []):
        if item not in options:
            options.append(item)
    if phase != "earth_analog":
        options.append({"type": "wait", "months": 3})
    return options[:4]


def summary_lines(state: dict[str, Any]) -> list[str]:
    language = state.get("language", "zh")
    text = i18n(language)
    phase = current_phase(state)
    phase_name = text["phases"].get(phase, phase)
    people = people_export(
        state["launch"],
        qualified=len(ready_crew(state)),
        pipeline_per_year=state["crew"]["pipeline_per_year"],
        ntr="ntr_stage" in state["tech"],
    )
    best = None
    for site_name in ("moon", "mars", "freespace"):
        report = ember_checklist(state, site_name)
        if best is None or report["passed"] > best["passed"]:
            best = report
    assert best is not None
    window = next_window_label(state["clock"]["year"], state["clock"]["month"])
    if language == "zh":
        lines = [
            f"—— {text['status_header']} · {text['turn']} {state['clock']['turn']} · {state['clock']['year']}年{state['clock']['month']}月 ——",
            f"{text['phase']}：{phase_name}",
            f"{text['treasury']}：{state['treasury_busd']:.2f}　{text['budget']}：{state['annual_budget_busd']:.2f}",
            f"{text['opinion']} {state['public_opinion']}　{text['politics']} {state['political_capital']}　{text['stability']} {state['earth_stability']}　{text['dissent']} {state['dissent']}",
            f"{text['crew_ready']}：{len(ready_crew(state))}　近地轨道运力约 {annual_imleo_t(state['launch']):.0f} 吨/年",
            f"{text['next_window']}：{window}",
            f"{text['people_decade']} {people['people']} {text['people_unit']}（估计，约束来自{ '质量与窗口' if people['binding'] == 'mass_and_windows' else '训练'}）。",
            *_foothold_lines(state, "zh"),
            f"{text['ember']}（{best['site']}）：{best['passed']}/{best['total']}",
        ]
    else:
        binding = "mass and windows" if people["binding"] == "mass_and_windows" else "training"
        lines = [
            f"—— {text['status_header']} · {text['turn']} {state['clock']['turn']} · {state['clock']['year']}-{state['clock']['month']:02d} ——",
            f"{text['phase']}: {phase_name}",
            f"{text['treasury']}: {state['treasury_busd']:.2f}    {text['budget']}: {state['annual_budget_busd']:.2f}",
            f"{text['opinion']} {state['public_opinion']}    {text['politics']} {state['political_capital']}    {text['stability']} {state['earth_stability']}    {text['dissent']} {state['dissent']}",
            f"{text['crew_ready']}: {len(ready_crew(state))}    LEO capacity about {annual_imleo_t(state['launch']):.0f} t/year",
            f"{text['next_window']}: {window}",
            f"{text['people_decade']} {people['people']} {text['people_unit']} (estimate; bound by {binding}).",
            *_foothold_lines(state, "en"),
            f"{text['ember']} ({best['site']}): {best['passed']}/{best['total']}",
        ]
    if state.get("outcome"):
        lines.append(f"OUTCOME {state['outcome']} · {state.get('outcome_reason')}")
    return lines


def _foothold_lines(state: dict[str, Any], language: str) -> list[str]:
    text = i18n(language)
    lines = []
    for row in foothold_progress(state):
        label = text[f"foothold_{row['path']}"]
        unit = text["foothold_unit_days"] if row["unit"] == "days" else text["foothold_unit_months"]
        line = f"{label} {row['site']}: {row['current']}/{row['target']} {unit}"
        if row["achieved"]:
            line += f" · {text['foothold_won']}"
        lines.append(line)
    return lines


def image_prompt(state: dict[str, Any], payload: dict[str, Any]) -> str:
    phase = current_phase(state)
    language = "Chinese caption" if state.get("language") == "zh" else "English caption"
    subject = payload.get("action") or phase
    return (
        "Documentary space-program concept art, physically plausible hardware, no fantasy aliens, "
        "no flags or insignia of real nations, natural light, 35mm film still. "
        f"Scene tied to phase {phase}, action {subject}, year {state['clock']['year']}. "
        f"A short {language} may appear as a small plaque, not as a poster of slogans. "
        "If people are present they are inside pressure vessels or analog habitats, not standing on open regolith without suits."
    )


def decorate(state: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    view = public_view(state)
    payload = dict(payload)
    payload["phase"] = current_phase(state)
    payload["gates"] = gates(state)
    payload["summary_lines"] = summary_lines(state)
    payload["suggested_actions"] = _suggestions(state)
    payload["image_prompt"] = image_prompt(state, payload)
    payload["language"] = state.get("language", "zh")
    payload["outcome"] = state.get("outcome")
    payload["outcome_reason"] = state.get("outcome_reason")
    payload["footholds"] = foothold_progress(state)
    victories = []
    for key, row in (state.get("footholds") or {}).items():
        if not row.get("just_announced"):
            continue
        text = {
            "foothold_500": {
                "zh": f"立足胜利：人在{row['site']}连续活过{row['progress']}天，本地粮食、氧气和水撑住了其中真实的一份，地球也还在。这不是火种。战役继续。",
                "en": f"Foothold won: people stayed alive on {row['site']} for {row['progress']} days, with a real share of food, oxygen, and water made there, and Earth is still alive. This is not the ember. The campaign continues.",
            },
            "foothold_biology": {
                "zh": f"立足胜利：地球生命在{row['site']}的封闭生态位里、不靠地球补给，自行延续了{row['progress']}个月。缓步动物的暴露不算，开放的火星地表也不算。战役继续。",
                "en": f"Foothold won: Earth life persisted on {row['site']} for {row['progress']} months inside a sheltered niche, with no Earth resupply. A tardigrade exposure does not count, and neither does the open Martian surface. The campaign continues.",
            },
            "foothold_machine": {
                "zh": f"立足胜利：机器在{row['site']}独自维持电力、备件、活着的生物和一份档案，已经{row['progress']}个月。没有生命的机器人不算。战役继续。",
                "en": f"Foothold won: machines on {row['site']} kept power, spares, living Earth organisms, and an archive going for {row['progress']} months with no Earth arrival. Robots with no life do not count. The campaign continues.",
            },
        }[row["reason"]]
        victories.append({
            "path": key,
            "outcome": "win",
            "outcome_reason": row["reason"],
            "tier": "foothold",
            "site": row["site"],
            "progress": row["progress"],
            "continues": state.get("outcome") != "win",
            "zh": text["zh"],
            "en": text["en"],
        })
        row["just_announced"] = False
    if victories:
        payload["foothold_victories"] = victories
    payload["public_state"] = {
        "clock": view["clock"],
        "treasury_busd": view["treasury_busd"],
        "annual_budget_busd": view["annual_budget_busd"],
        "tech": view["tech"],
        "facilities": list(view["facilities"].keys()),
        "revelations": view["revelations"],
    }
    # Never attach secrets, even if the caller passes a full state.
    payload.pop("secrets", None)
    return payload


def opening_brief(state: dict[str, Any]) -> dict[str, str]:
    people = people_export(
        state["launch"],
        qualified=len(ready_crew(state)),
        pipeline_per_year=state["crew"]["pipeline_per_year"],
    )
    zh = (
        f"{state['director']}，{state['program']}从 {state['clock']['year']} 年 1 月起算。"
        "目标不是把一面旗插上火星，而是让地球文明在另一个世界上留下一颗能自己开始的火种："
        "连续五年不靠地球的生命物资，水循环至少 98%，本地粮食、氧气、功率和剂量达标，"
        "并且要么有大约一万四千名居民，要么有一百名居民、十次地外出生、和一万名供体的种质档案。"
        "一百个人本身不是一个物种备份。档案才是那一轮新的骰子。"
        "在那之前有三种立足，每一种都要求地球还没垮，宣布一次，然后战役继续。"
        "人：至少两人在月球、火星或深空连续活过500天，本地干食至少四分之一、本地氧气至少一半、损耗的水至少一半来自当地。"
        "生物：能繁殖的地球物种（蓝细菌、地衣、苔藓、极端微生物或作物，不包括只是挨过暴露的缓步动物）在温室或覆土生态位里、不靠地球补给，延续36个月。开放地表不算。"
        "机器：机器人维持电力、备件、活着的生物和一份档案至少24个月。没有生命的机器不算。"
        f"若把未来十年全部近地轨道运力都用来送人，化学推进大约只能送出 {people['people']} 人。"
        "所以顺序不该是先把人扔出去。先在地球上把冷、热、真空、低氧和封闭生态做错几次，"
        "然后是机器，然后是月球，然后是微生物和植物，然后才是人，然后才是火星窗口。"
        "窗口大约每 779.94 天一次。错过就等。"
    )
    en = (
        f"{state['director']}, the {state['program']} starts in January {state['clock']['year']}. "
        "The aim is not a flag on Mars. It is a seed that can begin a civilization without Earth: "
        "five years without life-critical resupply, water recovery at least 98%, local food, oxygen, "
        "power, and dose on target, and either about 14,000 residents or 100 residents, ten off-world births, "
        "and a 10,000-donor archive. A hundred people are not a species backup. The archive is the next throw of the dice. "
        "Before that there are three footholds. Each one requires Earth still standing, is announced once, and does not end the campaign. "
        "Crew: at least two people alive for 500 days on the Moon, Mars, or in free space, with at least a quarter of dry food, half of oxygen, and half of water losses made locally. "
        "Life: a reproducing Earth species (cyanobacteria, lichen, moss, extremophiles, or crops — not a tardigrade that merely endured exposure) persists 36 months in a greenhouse or buried niche with no Earth resupply. Open ground does not count. "
        "Machines: robots keep power, spares, living organisms, and an archive going for 24 months. Machines with no life do not count. "
        f"If every tonne of LEO capacity for a decade is spent on crew, chemical propulsion sends about {people['people']} people. "
        "So the order is not 'throw the crew.' Fail the cold, the heat, the vacuum, and the closed air on Earth first, "
        "then machines, then the Moon, then microbes and plants, then humans, then a Mars window. "
        "Windows are about 779.94 days apart. Miss one and you wait."
    )
    return {"zh": zh, "en": en}
