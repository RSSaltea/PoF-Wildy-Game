# Wilderness Browser Game Art

New browser-game art goes here so it can replace the older wiki images without
breaking the Discord bot or generated wiki pages.

- `characters/player-base.png` - modular player model used behind equipment
- `items/<item-slug>.png` - item icons and equipment layer source art
- `npcs/<npc-slug>.png` - NPC battle sprites

Run `python cogs/wildygame/docs/game/export_game_data.py` after adding art.
The exporter refreshes `game-data.js`, `asset-manifest.json`, and
`art-prompts.jsonl`. The browser game prefers these new paths and falls back to
existing wiki art when a new file has not been added yet.

The current art set was imported from generated old-school fantasy MMORPG
sprite sheets, then chroma-keyed into transparent PNGs. The source sheets live
in `docs/game/_imagegen_sheets/`.

To rebuild those imports from the saved sheets, run:

```powershell
python cogs\wildygame\docs\game\import_imagegen_sheets.py
python cogs\wildygame\docs\game\fix_imagegen_blanks.py
python cogs\wildygame\docs\game\export_game_data.py
```

The importer now does the soft chroma-key matte and neighbor-fragment cleanup.
`fix_imagegen_blanks.py` also applies targeted transparent PNG overrides for
known bad generated cells, including the shifted Super Strength/Thornweave/
Tidestaff/Tiny Dark Archer run, the Netharis equipment set, and the emerald
icons. NPCs are rebuilt from the saved NPC sheets, with Lord Valthyros using
`docs/game/_imagegen_sheets/lord-valthyros-single.png` as a full-body vampire
lord override with exactly one Amulet of Seeping.
Use `clean_chroma_fringe.py` only as an extra repair pass if a future generated
sheet still leaves visible green edge spill.

To regenerate the older procedural fallback set instead, run:

```powershell
python cogs\wildygame\docs\game\generate_game_art.py
python cogs\wildygame\docs\game\export_game_data.py
```
