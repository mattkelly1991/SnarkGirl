# 🪂 Battle Royale — Fix List (from the commit 7d10fe5 match + Matt's ringside notes)

Spoils of the death match + spectator notes. Full battle context: `%TEMP%\snark-girl-reviews\BATTLE-ROYALE-commit-7d10fe5-20260611.md`

## 🎮 Game Rule Changes (SKILL.md)

- [ ] **Escalating hunger** — hunger cost grows +1 each round (turn 1 = 1🍖, turn 2 = 2🍖, turn 3 = 3🍖, …). Replaces flat 1/turn + manual endgame doubling.
- [ ] **Punish invalid findings** — an invalid/hallucinated finding costs **−1🍖** (on top of earning nothing). Better safe than sorry. Better honest than dead.
- [ ] **Escalating skirmish stakes** — losing a skirmish costs **2^(round−1)** rations (1, 2, 4, 8, …) instead of flat 2.
- [ ] **No food in closing zones** — when a zone flips to `closing`, its food should be gone. The zone closes BECAUSE it's looted; arena.html should stop scattering food there (currently only `closed` zones skip food, line ~596).

## 🗺️ Arena Visual Fixes (arena.html)

- [ ] **Feasting overlap** — multiple contestants feasting on the same food stack on top of each other. Make them *surround* the food instead.
- [ ] **Roaming overlap** — wandering contestants float on top of each other; spread their home spots out more within a zone.
- [ ] **Skirmish duo stacking** — multiple fighting pairs in one region pile up; spread the duos apart.
- [ ] **3-way fight animation** — a triple skirmish has no proper animation; with 3 fighters one guy just chills. Support N-way clash (triangle formation?).
- [ ] **Food scales with zone size** — bigger zones should spawn more food. 1 food in a small zone vs 1 food in a huge zone makes no sense (weight-proportional scatter).
- [ ] **New-since-last-read separator** — add a separator line in the Kill Feed / Events between updates so the spectator can tell what's new since they last looked.
- [ ] **Combatant emojis in sidebar** — show each contestant's emoji next to their name in the combatants list.
- [ ] **Victory report centering** — 🏆 report isn't centered (probably the `< Back to arena` button pushing it over).

## ⚠️ Battle Findings — Important (11 survived contested skirmishes)

- [ ] **f1** `arena.html:738` — actx() ignores async `resume()`; state-check race drops first sounds. Await resume or queue sfx until `running`.
- [ ] **f3** `arena.html:653` — corpses hard-filtered when zone missing from `s.zones`; alive tokens get a fallback row, dead don't. Give corpses the same fallback.
- [ ] **f7** `arena.html:996` — replay autoplay skips step-0 dwell (`play()` ticks immediately after `show(0)`). Let the interval fire first.
- [ ] **f17** `arena.html:707` — replay scrub jumps draw fake movement trails between unrelated steps. Suppress `drawTrail` on non-sequential `show()`.
- [ ] **f23** `arena.html:864` — open Victory Report goes stale when finished-phase updates arrive. Re-call `renderVictory(s)` while showing.
- [ ] **f26** `arena.html:938` — polling race: late stale fetch can overwrite a newer render. Skip if in-flight / ignore older `updatedAt`.
- [ ] **f30** `arena.html:680` — clash pair animations desynced (per-tribute random delay) so fighters never actually collide. Share one delay per pair.
- [ ] **f31** `arena.html:339` — `#replay-bar` z-60 paints over battle-done modal (z-55) in replay mode. Lower to 51 (above victory 50, below battle-done 55).
- [ ] **f36** `arena.html:507-510` — snapSplit clamp inversion in the window `GRID < hi-lo < 2*GRID`; guard slips inverted values through. Check `lo+GRID < hi-GRID` first.
- [ ] **f39** `arena.html:564` — homeSpot min offsets exceed tiny zones; tokens can overflow the zone/viewBox. Clamp spot into the zone rect. *(Pairs with the roaming-overlap note above.)*
- [ ] **f41** `arena.html:190` — modals lack focus trap / `aria-modal`; keyboard + SR focus escapes. `role="dialog" aria-modal="true"` + trap.

## 💅 Battle Findings — Nitpicks (worth batching)

- [ ] **Replay keyboard layer** (survived 4 challenges combined): **f4/f8** `arena.html:1010-1019` — focused-scrub arrow keys double-fire the replay step; only Space gets `preventDefault`. Guard against focused form controls.
- [ ] **Unconditional innerHTML rebuilds** (one root cause): **f43** announcement re-animates every poll (`:823`), **f27** feed scroll resets (`:832`), **f18** full rerender per scrub input (`:1010`). Diff-guard the DOM writes.
- [ ] **f33** `arena.html:808` — `slice(-3)` silently drops cannon/clash sound cues on busy ticks. Queue all fresh events with bounded spacing.
- [ ] **f2** `:804` sound detection misses same-length feed replacement · **f5** `:621` asymmetric opponent drags bystander into clash anim · **f25** `:640` feasting anim without food · **f34** `:1011` speed change drops dwell · **f28** `:870` bd-sub trapped in doneSeen guard · **f32** `:941` lastOk set before parse · **f19** `:702` token z-order frozen at spawn · **f24** `:564,600` undelimited hash seeds · **f22** `:584` zone labels overflow · **f11** `:600` food scatter collapses in tiny zones · **f37** `:592` foodByZone id type guard · **f38** `:520` sub-pixel territory seams · **f40** `:648` fallback row off-canvas · **f9** `#v-close` float vs sticky · **f12/f13** SKILL.md doc gaps.

---
*From the SnarkGirl Battle Royale, 7 turns, 34 battle-tested findings. The arena has spoken. 👑*
