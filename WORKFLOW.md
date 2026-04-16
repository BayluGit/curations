# Curation Workflow

A step-by-step guide to creating an art × news curation.

---

## 1. Gather News

Fetch current headlines from a text-friendly news source:

```bash
curl -s "https://lite.cnn.com" 
```

Alternative sources:
- `https://text.npr.org`
- `https://apnews.com` (may need browser)

**Output:** List of 10-20 headlines with brief context. Look for stories with emotional resonance, not just facts.

---

## 2. Query Artworks from objkt.com

### Option A: Community Artists (Recommended)

Use the `curate_community.py` script to pull random artworks from your community:

```bash
cd /home/node/.openclaw/workspace

# Standard curation query: under 10ꜩ, from 30 random artists
python3 curate_community.py tezos_users.csv 60 10 30

# More artists, no price limit
python3 curate_community.py tezos_users.csv 50 "" 25
```

**Arguments:**
1. CSV file with community addresses (default: `tezos_users.csv`)
2. Limit — max artworks to fetch (default: 50)
3. Max price in tez (default: 10ꜩ — use `""` to skip)
4. Artist sample — randomly pick N artists from the pool (optional)

The script:
- Randomly shuffles/samples artists each run
- Filters for pieces with descriptions (>50 chars) — essential for thematic pairing
- Outputs formatted markdown with IPFS links and objkt URLs

**Selection rules:**
- **Different artist for each pairing** — no repeating artists in a single curation
- **Price under 10ꜩ** — keeps art accessible
- **Strong descriptions** — needed for meaningful thematic connections

---

### Option B: General objkt Query

### Basic query (recent pieces with images):
```bash
curl -s -X POST https://data.objkt.com/v3/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ token(limit: 15, order_by: {pk: desc}, where: {name: {_is_null: false}, display_uri: {_is_null: false}}) { name pk fa_contract token_id display_uri artifact_uri description creators { holder { alias address } } } }"}'
```

### Query with price filter (under 10 tez = 10,000,000 mutez):
```bash
curl -s -X POST https://data.objkt.com/v3/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ listing(limit: 30, order_by: {timestamp: desc}, where: {price: {_lt: \"10000000\"}, status: {_eq: \"active\"}, token: {display_uri: {_is_null: false}, name: {_is_null: false}}}) { price token { name pk fa_contract token_id display_uri description creators { holder { alias } } } } }"}'
```

**Key fields:**
- `name` — artwork title
- `display_uri` — IPFS hash for image (prefix with `https://ipfs.io/ipfs/`)
- `description` — artist's description (gold for finding thematic connections)
- `creators.holder.alias` — artist name
- `fa_contract` + `token_id` — for objkt link: `https://objkt.com/tokens/{fa_contract}/{token_id}`

---

## 3. Find Thematic Connections

Look for resonance between:
- **Artwork titles** and news headlines
- **Artist descriptions** and current events
- **Visual metaphors** that map to stories

**Rules:**
- **One artist per pairing** — each artwork must be from a different artist
- **Price under 10ꜩ** — keeps the curation accessible
- **Descriptions matter** — prioritize pieces with rich artist statements

Good pairings feel inevitable, not forced. The art should illuminate the news, not just illustrate it.

---

## 4. Develop a Unifying Concept

After selecting 3-5 pieces, ask: **What thread connects them all?**

Examples:
- "Almost" — the tension of perpetual proximity
- "Surfaces" — what lies beneath appearances
- "The Space Between" — liminality and suspension

The concept shapes:
- Title
- Introduction text
- How you frame each pairing
- Closing summary

---

## 5. Create HTML Structure

### Header
```html
<header>
    <p class="date">April 11, 2026</p>
    <h1>Title Here</h1>
    <p class="subtitle">One-line concept summary.</p>
</header>
```

### Introduction (after header)
```html
<section class="intro container">
    <div class="intro-text">
        <p>Opening hook — the core tension.</p>
        <p>Expand on the theme with current context.</p>
        <p>Set up what the viewer is about to experience.</p>
    </div>
</section>
```

### Each Artwork Entry
```html
<article class="curation-entry">
    <div class="artwork">
        <img src="https://ipfs.io/ipfs/{display_uri_hash}" alt="Title by Artist">
    </div>
    <div class="context">
        <span class="news-tag">Category</span>
        <h2>News-Inspired Headline</h2>
        <p class="commentary">
            2-4 sentences connecting the art to the news. 
            Quote the artist's description if it resonates.
        </p>
        <div class="art-info">
            <p class="art-title">Artwork Title</p>
            <p class="artist">by Artist Name</p>
            <p class="art-description">"Artist's own words"</p>
            <a href="https://objkt.com/tokens/{fa_contract}/{token_id}" class="art-link" target="_blank">View on objkt →</a>
        </div>
    </div>
</article>
```

### Closing Summary (before footer)
```html
<section class="summary">
    <div class="summary-text">
        <h3>Closing Title</h3>
        <p>Reflect on what the pieces revealed together.</p>
        <p>What does it mean to sit with this tension?</p>
        <p>End with something that lingers.</p>
    </div>
</section>
```

### Share Button (after summary, before footer)

Add an X/Twitter share button with the curation title, artist handles, and link:

```html
<section class="share-section">
    <a href="https://x.com/intent/tweet?text={ENCODED_TEXT_WITH_URL}" 
       class="share-btn" target="_blank">
        <svg viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
        Share
    </a>
</section>
```

**Share text format:**
```
{Title} — {Subtitle}

{URL}

Featuring @handle1 @handle2 @handle3...
```

**Resolve Twitter handles:**
Look up artist names in `tezos_users.csv` to get their `twitter_handle` column. Use @handles instead of artist names.

```bash
grep -i "artistname" tezos_users.csv
```

**Base URL:** `https://baylu.com/`

**Example share text (before encoding):**
```
Static — When the signal breaks down, something else comes through.

https://baylu.com/2026-04-15/static.html

Featuring @ivnhgo @shojironakaoka @Stalomir @idjasaund @JPCezarx
```

**URL encoding:** Use `%20` for spaces, `%0A` for newlines, `%3A` for `:`, `%2F` for `/`

---

## 6. File Structure

```
curations/
├── WORKFLOW.md          # This file
└── YYYY-MM-DD/
    ├── index.html       # Main curation
    └── [variant].html   # Alternative versions (e.g., affordable.html, static.html)
```

**Naming conventions:**
- `index.html` — primary curation of the day
- `[theme].html` — additional curations (e.g., `fractures.html`, `static.html`)

---

## 7. Checklist

- [ ] Fetched current news (date-relevant)
- [ ] Queried artworks (under 10ꜩ, community script or general objkt API)
- [ ] Selected 3-5 pieces with strong descriptions
- [ ] **Verified each piece is from a different artist**
- [ ] **Verified all pieces are under 10ꜩ**
- [ ] Found thematic thread connecting all pieces
- [ ] Wrote title + subtitle
- [ ] Wrote introduction (3-4 paragraphs)
- [ ] Wrote commentary for each pairing
- [ ] Wrote closing summary
- [ ] Verified all IPFS image links work
- [ ] Verified all objkt links are correct
- [ ] Added share button with artist @handles (from CSV) and curation URL
- [ ] Added to main index (`curations/index.html`)
- [ ] Committed and pushed to remote

---

## 8. Commit & Push

After completing a curation, commit and push to the remote repository.

### Add and commit:
```bash
cd /home/node/.openclaw/workspace

# Stage the new curation
git add curations/

# Commit with descriptive message
git commit -m "Add curation: [Title] — [Date]

[Brief description of the theme and pairings]"
```

### Push to remote:
```bash
git push origin master
```

### Example commit message:
```
Add curation: Witnesses — April 15, 2026

Five works about those who see — silenced, hidden, or unable to look away.
Pairings: journalist detained, hidden archive discovered, allies watching war.
```

### If pushing a batch of curations:
```bash
git add curations/
git commit -m "Add curations: April 11-15, 2026

- Almost: Art for an age of perpetual proximity
- Grund: German news curation on shifting foundations
- Witnesses: Those who see — silenced or unable to look away"
git push origin master
```

**Repository:** https://github.com/BayluGit/curations

---

## Quick Reference: objkt GraphQL

**Endpoint:** `https://data.objkt.com/v3/graphql`

**Useful filters:**
- `price: {_lt: "10000000"}` — under 10 tez
- `status: {_eq: "active"}` — currently listed
- `name: {_is_null: false}` — has a title
- `display_uri: {_is_null: false}` — has an image

**Price conversion:** 1 tez = 1,000,000 mutez

---

## Example: Full API → HTML Flow

1. Run listing query → get JSON with tokens
2. Pick piece: `"Hollow Bloom"` by `roS`, description: `"translating human emotion..."`
3. Match to news: "Consumer sentiment hits record low"
4. Write pairing:
   - News tag: "Economy"
   - Headline: "Consumer Sentiment Hits Record Low"
   - Commentary: Connect the hollow bloom metaphor to economic anxiety
5. Build objkt link: `https://objkt.com/tokens/KT1K1JfvefhycREsF4YDdWspEw2emeY4kufL/11`
6. Build image link: `https://ipfs.io/ipfs/bafybeifarmoh5ue5nd5nwnlaopil7mhv3tozqj2m4tpmhfhqb2d32vjmke`

---

---

## 9. Fonts

Fonts are stored locally in `curations/fonts/`:
- `inter-300.ttf`, `inter-400.ttf`, `inter-500.ttf`
- `playfair-400.ttf`, `playfair-600.ttf`, `playfair-400-italic.ttf`

The `@font-face` declarations are in `styles.css`. No external font requests needed.

---

*Last updated: April 16, 2026*
