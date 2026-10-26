# Real Mars Shot 🚀

> 这是一个真实的、科学的、系统的探索外太空、并把地球文明扩展到多个星球的计划。
>
> A real, scientific, and systematic plan to explore outer space and make Earth civilization multi-planetary.

## 🎯 目标 / Mission

让地球文明跨越星球，不至于随地球的衰落而终结。

Make Earth civilization multi-planetary, so that it does not end with the decline of Earth.

## 🧭 原则 / Principles

- **真实 Real**: 基于真实的物理、工程与经济约束，不做科幻空想。
- **科学 Scientific**: 以可验证的科学研究和数据为依据。
- **系统 Systematic**: 从技术、生命保障、能源、资源、社会与治理等多个维度整体规划。

## 这是什么 / What this repository is

这是一款给智能体玩的技能游戏，不是一扇需要打开的图形窗口。OpenClaw、Claude Code、Copilot CLI、Grok Bot 这一类宿主读 `SKILL.md`，玩家用自然语言当计划负责人，Python 脚本负责存档、骰子、火箭方程、剂量、生命保障和胜负。设计全文在 `DESIGN.md`。文献在 `REFERENCES.md`。

This is a skill an agent plays, not a window you open. Hosts such as OpenClaw, Claude Code, Copilot CLI, and Grok Bot follow `SKILL.md`. You speak. Python owns the save, the dice, the rocket equation, dose, life support, and win or loss. The full design is `DESIGN.md`. Citations are in `REFERENCES.md`.

## 前提 / Premises

1. 人极脆弱，依赖水、电、空气、营养、温度、压力和辐射屏蔽。地衣、苔藓、缓步动物、极端细菌、蓝细菌比人容易送到远处。暴露后还活着，不等于在那里建立了生命。机器更能先抵达；只有机器、没有能延续的人，不算火种。
2. 顺序从易到难。先在地球上把冷、热、真空、低氧和封闭生态做错几次（试验舱、南极式驻留、生物圈二号式的封闭栖息地），然后是机器，然后是月球，然后是微生物和植物，然后才是人，然后才是火星。开局就把人射向火星，引擎会判成不可能或鲁莽。
3. 每一回合都数得过来：地球实际上能送出去多少人、推进剂和发射班次、质量预算、补给、乘员健康、剂量、能量、原位资源、大约 26 个月一次的火星窗口、通信延迟，以及政治。派系是虚构的。会有人争预算、堵路、催你跳步，也会有人安静地拆计划。
4. 数字要么来自文献，要么标明是估计。火箭方程、比冲、近地轨道到转移轨道的质量、月面和火星与转移中的剂量、火星大气、星壤高氯酸盐、月面水冰、闭环生命保障的回收率，都写在 `data/science.json`，出处在 `REFERENCES.md`。

Humans are fragile. Lower organisms travel more easily, and surviving an exposure is not a settlement. Machines can go first. Machines alone are not an ember. The honest order runs from Earth analogs, to machines, to the Moon, to microbes and plants, to humans, and only then to Mars. A crewed Mars shot on turn one comes back impossible or reckless. Every turn counts launch mass, consumables, dose, power, ISRU, the ~26-month window, light time, and politics among fictional factions. Measured numbers stay attached to sources. Estimates are marked.

## 怎么赢，怎么输 / Win and loss

赢：在月球、火星或自由空间留下一颗火种。十条要同时成立，包括连续五年的本地盈余（库存不算）、水回收至少 98% 且损耗由本地水覆盖、氧气与功率有裕度、九成以上干食本地生产、栖息地年剂量达标，以及要么约一万四千名居民，要么一百名居民、十次地外出生、再加一万名供体的种质档案。一百个人本身不是物种备份。纯机器文明不算赢。

输：确认后在地球上无约束释放试验生物；地球稳定度归零；计划在长期赤字、政治资本和舆论同时崩掉时被取消；孤注一掷的载人失败把国库、政治和乘员一起打光，地外又没有机器人；或者试炼中的居民死去而地球已经救不回来。

单次发射失败、模拟舱撤离、预算削减、错过窗口、作物病害，都还能继续。模拟舱失败是一次教训，不是一座坟墓。

Win by leaving an ember: five years of local surplus, 98% water recovery with local makeup, oxygen and power margin, mostly local food, a habitat dose on target, and either about 14,000 people or 100 residents, ten off-world births, and a 10,000-donor archive. A hundred people are not a species backup. A machine city is not a win.

Loss is an uncontained release on Earth, Earth-side collapse, a canceled program, an all-in crewed disaster with nothing left off-world, or a trial settlement dying while Earth cannot rescue it. A failed launch, an evacuated analog, a budget cut, a missed window, or a crop blight does not end the campaign.

## 🗺️ 路线图 / Roadmap

游戏的阶段就是这份计划的路线图。阶段由门推导，不锁死菜单。走得太快，任务会变成不可能或鲁莽。

The phases are the roadmap. They describe the honest next step. They do not lock the menu. Skipping ahead is impossible or reckless.

1. **地球模拟 Earth analogs.** 先建封闭舱。30 天，然后一年，并把水循环做到早期空间站的约 93%。
2. **机器先遣 Machines first.** 月球着陆器先于乘员。
3. **月球 Moon.** 确认水冰或制氧，再谈住人。
4. **生物火种 Biology.** 在模拟星壤里种，而不是往开放地表撒。缓步动物活下来也不算定居。
5. **近地乘员 Cislunar crew.** 人先从月球回来。
6. **火星货运 Mars cargo.** 重型进入、减速与着陆之后，货物落地并熬过尘季，制氧试点达到吨级每年。
7. **火星前哨 Mars outpost.** 先有一次往返，再谈留下。
8. **断供试炼 Independence.** 连续六十个月靠当地盈余活着。库存不走这只时钟。
9. **火种 Ember.** 十条清单全部为真。地球这边即使同时垮掉，已经成立的火种仍然算赢。

## 安装 / Install

需要 `python3`。不需要 pip 包。可选：`edge-tts` 命令行，用来念旁白；没有它，回合依然有效。

You need `python3`. No third-party Python packages. The `edge-tts` CLI is optional narration. A missing binary does not fail the turn.

把这个仓库放到宿主读取技能的目录，保证 `SKILL.md` 在该目录根上。例如：

```bash
git clone https://github.com/yumyumtum/real-mars-shot.git
# OpenClaw / Clawdbot 一类宿主常见位置：
#   ~/clawd/skills/realmarsshot
# Claude Code 一类宿主常见位置：
#   .claude/skills/realmarsshot
```

在聊天里说 `/realmarsshot`、`火星计划`、`太空探索游戏` 或 `real mars shot` 开始。宿主按 `SKILL.md` 问语言（简体中文或 English），然后调用脚本。你不需要自己记命令，除非你想绕过叙述、直接看引擎。

Say `/realmarsshot`, `火星计划`, `太空探索游戏`, or `real mars shot`. The host follows `SKILL.md`, asks for 简体中文 or English, and runs the scripts. The commands below are for reading the engine directly.

检查计算是否还成立：

```bash
python3 -m unittest discover -s tests -v
```

## 怎么玩 / How to play

你是计划负责人。说话即可。宿主应把句子收成一个动作：建造模拟舱、做 30 天封闭试验、研究一项科技、游说预算、训练乘员、把机器人送上月球、或者坚持现在就送人去火星。最后这种选择会被引擎拒绝或要求你确认风险。确认之前，时间不动。

每一回合结束时，宿主应原样给你一段状态，并可以写出一张场景卡（`scripts/render_scene.py`）。要看 Δv、科技树、栖息地剖面或任务架构，用 `scripts/render_diagram.py`。轨道图是 `scripts/render_orbits.py` 写的单个 HTML：没有网络时用 canvas，有网络时可以再加载 three.js。宿主若另有 `/show-me`、`diagram-design`、three.js 或 `/grill-me`，那些是可选钩子；脚本是没有它们时的退路。

存档在 `~/.realmarsshot/saves/user-<id>.json`，或你设置的 `$REALMARSSHOT_SAVE_DIR`。id 只含字母、数字、下划线和连字符。

You play the program director in ordinary language. A crewed Mars shot at the start is refused or held for confirmation, and the clock does not move until you accept the risk. Each turn ends with a status block. Scene cards, diagrams, and an orbit page are scripts. Host skills such as `/show-me`, diagram design, three.js, and `/grill-me` are optional. The scripts still work without them.

## 示例回合 / Sample turn

下面这条样本把骰子和事件固定住，只为了和 `examples/save-example.json` 对得上。真在玩的时候不要加 `--force-roll` 或 `--force-event`。

This sample pins the dice and the event so it matches `examples/save-example.json`. A real session does not pass `--force-roll` or `--force-event`.

```bash
export REALMARSSHOT_SAVE_DIR=/tmp/realmarsshot-sample
python3 scripts/new_game.py \
  --user-id sample --language zh \
  --director 顾长川 --program 火种计划 --seed 7
python3 scripts/resolve_turn.py --user-id sample \
  --force-roll 90 --force-event quiet_quarter \
  --action '{"type":"facility","facility":"analog_habitat"}'
python3 scripts/resolve_turn.py --user-id sample \
  --force-roll 99 --force-event none \
  --action '{"type":"analog","days":30}'
python3 scripts/status_report.py --user-id sample
```

开场会说明：目标不是插旗；若把未来十年的近地轨道运力都拿去送人，化学推进大约只能送出 10 人；顺序是模拟、机器、月球、微生物和植物、人，然后才是火星窗口。窗口大约每 779.94 天一次。

第一回合花六个月和 0.35（十亿美元）建好模拟舱，事件是安静的一季。第二回合做 30 天封闭试验并且成功。引擎打出的状态是：

The opening says the aim is not a flag, that a decade of chemical crew flights can export about 10 people, and that the order is analogs, machines, the Moon, microbes and plants, humans, then a Mars window about every 779.94 days.

The first turn spends six months and 0.35 billion USD on the analog habitat, and the quarter stays quiet. The second turn seals the habitat for 30 days and succeeds. The engine prints:

```
—— 状态 · 回合 2 · 2026年8月 ——
阶段：地球模拟
国库（十亿美元）：4.56　年预算（十亿美元）：6.00
舆论 52　政治资本 55　地球稳定 82　内部异议 12
可飞乘员：36　近地轨道运力约 234 吨/年
下次火星窗口：2026-10
若把未来十年全部近地轨道运力都拿去送人（化学推进、六人战役级），地球大约能送出 10 人（估计，约束来自质量与窗口）。
火种清单（moon）：0/10
```

同一套起点下，无额外屏蔽的参考合式任务（180+500+180 天）约 982.4 mSv，高于游戏里的 600 mSv 规划帽（那顶帽子是估计）。化学六人战役的初始近地轨道质量约 1375.6 吨；乘上核热系数后约 853 吨，才落进 DRA 5.0 的 800–1200 吨区间。这些数可以用 `scripts/compute.py` 再算一遍。

同目录的 `examples/` 里有这局的场景卡、Δv 图、科技树、栖息地剖面、任务架构和轨道 HTML。提交的存档把内应字段写成了 null。真存档可能有内应；玩的时候不应被念出来，直到事件自己揭开。

On this same start, an unshielded reference conjunction (180+500+180 days) is about 982.4 mSv, over the game's 600 mSv planning cap (the cap is an estimate). A chemical six-person campaign is about 1375.6 t IMLEO. The nuclear-thermal factor brings it to about 853 t, inside the DRA 5.0 band of 800–1200 t. Recompute with `scripts/compute.py`.

`examples/` holds the scene card, delta-v map, tech tree, habitat section, campaign architecture, and orbit page. The committed save redacts the mole. A live save may have one. It stays unspoken until an event reveals it.

## 仓库地图 / Layout

| 路径 | 内容 |
| --- | --- |
| `SKILL.md` | 宿主智能体的玩法说明与触发词 |
| `DESIGN.md` | 阶段、胜负、质量和剂量为什么这样定 |
| `REFERENCES.md` | `source_id` 与文献 |
| `data/` | 科学、科技树、派系、顾问、生物、事件 |
| `i18n/` | 状态行的中文和英文 |
| `scripts/` | 开局、回合、计算、绘图、TTS |
| `tests/` | 方程、剂量、顺序、胜负、样本存档 |
| `examples/` | 种子 7 的样本存档和图 |

## 📄 License

MIT
