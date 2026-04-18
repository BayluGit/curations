# Curation Quick Reference

## 1. Fetch News + Art (One Command)
```bash
python3 fetch_curation.py
```
Uses community artists only (from `tezos_users.csv`).

**Options:**
- `--limit 80` — more pieces (default 40)
- `--artists 50` — sample more artists (default 30)
- `--max-price 5` — cheaper art (default 10ꜩ)
- `--news-only` / `--art-only` — fetch just one

## 2. Create HTML
```bash
cp curation-template.html curations/YYYY-MM-DD/index.html
```

**Placeholders to fill:**
- `{{DATE_LONG}}` — April 18, 2026
- `{{TITLE}}` / `{{SUBTITLE}}`
- `{{INTRO_1}}` `{{INTRO_2}}` `{{INTRO_3}}`
- Per entry (1-5): `{{TAG_N}}` `{{HEADLINE_N}}` `{{COMMENTARY_N}}`
- Per entry (1-5): `{{IMG_N}}` `{{ART_TITLE_N}}` `{{ARTIST_N}}` `{{ART_DESC_N}}` `{{OBJKT_N}}`
- `{{CLOSING_TITLE}}` `{{CLOSING_1}}` `{{CLOSING_2}}` `{{CLOSING_3}}`
- `{{SHARE_TEXT_ENCODED}}`

Delete unused entries (template has 5).

## 3. Share Text
```
{Title} — {Subtitle}

https://baylu.com/{date}/{slug}.html

Featuring @handle1 @handle2...
```
Lookup handles: `grep -i "artist" tezos_users.csv`

## 4. Checklist
- [ ] Different artist per piece
- [ ] All under 10ꜩ
- [ ] IPFS links work
- [ ] objkt links correct
- [ ] Share button has @handles
- [ ] Added to `curations/index.html`
- [ ] `git add curations/ && git commit && git push`

---
*Full docs: WORKFLOW-FULL.md*
