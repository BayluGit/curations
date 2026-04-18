#!/usr/bin/env python3
"""
Unified fetch for curation: news + community art in one call.

Usage:
  python3 fetch_curation.py                    # defaults: 40 pieces, 30 artists, 10ꜩ max
  python3 fetch_curation.py --limit 80         # more pieces
  python3 fetch_curation.py --artists 50       # sample more artists
  python3 fetch_curation.py --max-price 5      # cheaper art
  python3 fetch_curation.py --news-only        # just news
  python3 fetch_curation.py --art-only         # just art
"""
import argparse
import csv
import json
import random
import subprocess
import sys
from html.parser import HTMLParser

# ─────────────────────────────────────────────────────────────
# NEWS
# ─────────────────────────────────────────────────────────────

class CNNParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headlines = []
        self.in_link = False
        self.current = None
    
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href', '')
            if href.startswith('/2026/') or href.startswith('/2025/'):
                self.in_link = True
                self.current = {'href': href, 'text': ''}
    
    def handle_endtag(self, tag):
        if tag == 'a' and self.in_link:
            if self.current and self.current['text'].strip():
                self.headlines.append(self.current)
            self.in_link = False
            self.current = None
    
    def handle_data(self, data):
        if self.in_link and self.current:
            self.current['text'] += data

def fetch_news():
    result = subprocess.run(
        ['curl', '-s', 'https://lite.cnn.com'],
        capture_output=True, text=True
    )
    parser = CNNParser()
    parser.feed(result.stdout)
    return parser.headlines[:20]

# ─────────────────────────────────────────────────────────────
# ART - Community Only
# ─────────────────────────────────────────────────────────────

def load_community(csv_file='tezos_users.csv'):
    addresses = []
    try:
        with open(csv_file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                addr = row.get('tz_address', '').strip()
                if addr:
                    addresses.append(addr)
    except FileNotFoundError:
        pass
    return addresses

def query_community(addresses, limit=40, max_price=10):
    addr_json = ', '.join([f'"{a}"' for a in addresses])
    price_filter = f', price: {{_lt: "{int(max_price * 1000000)}"}}' if max_price else ''
    
    query = f'''{{
        token(
            where: {{
                creators: {{holder: {{address: {{_in: [{addr_json}]}}}}}},
                display_uri: {{_is_null: false}},
                name: {{_is_null: false}},
                description: {{_neq: ""}},
                listings: {{status: {{_eq: "active"}}{price_filter}}}
            }},
            limit: {limit},
            order_by: {{pk: desc}}
        ) {{
            name description display_uri pk fa_contract token_id
            creators {{ holder {{ alias address }} }}
            listings(where: {{status: {{_eq: "active"}}}}, limit: 1, order_by: {{price: asc}}) {{ price }}
        }}
    }}'''
    
    payload = json.dumps({"query": query.replace('\n', ' ')})
    result = subprocess.run(
        ['curl', '-s', 'https://data.objkt.com/v3/graphql',
         '-H', 'Content-Type: application/json',
         '-d', payload],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        return data.get('data', {}).get('token', [])
    except:
        return []

# ─────────────────────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────────────────────

def format_token(t, i):
    name = t.get('name', 'Untitled')
    desc = (t.get('description') or '').replace('\n', ' ').strip()
    creator = t['creators'][0]['holder']
    artist = creator.get('alias') or creator['address'][:15]
    
    price_mutez = t['listings'][0]['price'] if t.get('listings') else None
    price_tez = int(price_mutez)/1000000 if price_mutez else 0
    
    display = t.get('display_uri', '').replace('ipfs://', '')
    link = f"https://objkt.com/tokens/{t['fa_contract']}/{t['token_id']}"
    img = f"https://ipfs.io/ipfs/{display}"
    
    # Truncate description for output
    desc_short = desc[:250] + '...' if len(desc) > 250 else desc
    
    return f"""### {i}. {name}
**{artist}** · {price_tez:.1f}ꜩ
> {desc_short}
- img: {img}
- link: {link}
"""

def main():
    parser = argparse.ArgumentParser(description='Fetch news + community art for curation')
    parser.add_argument('--limit', type=int, default=40, help='Max artworks to fetch (default 40)')
    parser.add_argument('--max-price', type=float, default=10, help='Max price in tez (default 10, 0 for any)')
    parser.add_argument('--artists', type=int, default=30, help='Sample N community artists (default 30)')
    parser.add_argument('--csv', default='tezos_users.csv', help='Community CSV file')
    parser.add_argument('--news-only', action='store_true', help='Only fetch news')
    parser.add_argument('--art-only', action='store_true', help='Only fetch art')
    args = parser.parse_args()
    
    max_price = args.max_price if args.max_price > 0 else None
    
    # ─── NEWS ───
    if not args.art_only:
        print("# 📰 News\n")
        headlines = fetch_news()
        if headlines:
            for h in headlines:
                print(f"- {h['text'].strip()}")
            print()
        else:
            print("_Could not fetch news_\n")
    
    # ─── ART ───
    if not args.news_only:
        print("# 🎨 Art (Community)\n")
        
        addresses = load_community(args.csv)
        if not addresses:
            print(f"_Error: No community CSV found at {args.csv}_\n")
            sys.exit(1)
        
        sampled = random.sample(addresses, min(args.artists, len(addresses)))
        print(f"_{len(sampled)} artists · limit {args.limit} · max {max_price or 'any'}ꜩ_\n")
        tokens = query_community(sampled, args.limit, max_price)
        
        # Filter for substantial descriptions
        tokens = [t for t in tokens if len(t.get('description', '') or '') > 50]
        random.shuffle(tokens)
        
        # Dedupe by artist (one per artist)
        seen_artists = set()
        unique = []
        for t in tokens:
            addr = t['creators'][0]['holder']['address']
            if addr not in seen_artists:
                seen_artists.add(addr)
                unique.append(t)
        
        print(f"_{len(unique)} pieces (unique artists)_\n")
        
        for i, t in enumerate(unique[:15], 1):  # Cap at 15 to keep output manageable
            print(format_token(t, i))

if __name__ == '__main__':
    main()
