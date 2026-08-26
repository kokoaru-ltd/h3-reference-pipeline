"""Normalize an official TikTok Creative Center Top Ads export.

This intentionally does not bypass login, bot checks, or private endpoints.
Export/save the records from TikTok Top Ads, then run:
  python tiktok_topads_ingest.py export.json --out tiktok_jp_topads_manifest.json
"""
from __future__ import annotations
import argparse, csv, json, os, re
from datetime import datetime, timezone

ALLOWED_CATEGORIES = {
    'beauty', '日用品', 'household', '食品', 'food', 'ガジェット', 'gadget',
    'ファッション', 'fashion', 'アプリ', 'app', '求人', 'recruiting'
}

def load_rows(path: str):
    if path.lower().endswith('.csv'):
        with open(path, encoding='utf-8-sig', newline='') as f:
            return list(csv.DictReader(f))
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        for key in ('ads', 'items', 'data', 'results'):
            if isinstance(data.get(key), list):
                return data[key]
        return [data]
    return data

def first(row, *keys):
    for key in keys:
        value = row.get(key) if isinstance(row, dict) else None
        if value not in (None, ''):
            return value
    return None

def number(value):
    if value in (None, ''):
        return None
    m = re.search(r'-?\d+(?:\.\d+)?', str(value).replace(',', ''))
    return float(m.group(0)) if m else None

def normalize(row, source_index):
    region = first(row, 'region', '地域', 'country', 'country_code')
    industry = first(row, 'industry', '業種', 'category', 'カテゴリ')
    return {
        'source_index': source_index,
        'ad_id': first(row, 'ad_id', 'asset_id', 'creative_id', 'id'),
        'brand': first(row, 'brand', 'brand_name', 'ブランド'),
        'product': first(row, 'product', 'product_name', '商品'),
        'region': region,
        'industry': industry,
        'objective': first(row, 'objective', '目的'),
        'language': first(row, 'language', '広告言語'),
        'ad_format': first(row, 'ad_format', 'format', '広告フォーマット'),
        'video_url': first(row, 'video_url', 'video', '動画URL', 'asset_url'),
        'landing_page': first(row, 'landing_page', 'landingPage', '遷移先'),
        'thumbnail_url': first(row, 'thumbnail_url', 'thumbnail', 'cover_url', 'サムネイルURL'),
        'caption': first(row, 'caption', 'ad_caption', 'テキスト'),
        'duration_sec': number(first(row, 'duration_sec', 'duration', '尺')),
        'likes': number(first(row, 'likes', 'いいね数')),
        'ctr_percentile': number(first(row, 'ctr_percentile', 'ctr_top', 'CTR', 'クリック率')),
        'two_sec_view_rate': number(first(row, 'two_sec_view_rate', '2s_views_rate', '2秒視聴率')),
        'six_sec_view_rate': number(first(row, 'six_sec_view_rate', '6s_views_rate', '6秒視聴率')),
        'cvr': number(first(row, 'cvr', 'CVR', 'コンバージョン率')),
        'budget_level': first(row, 'budget_level', 'budget', '予算'),
        'source': 'TikTok Creative Center Top Ads export',
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('--out', default='tiktok_jp_topads_manifest.json')
    ap.add_argument('--region', default='JP')
    ap.add_argument('--min-per-category', type=int, default=0)
    args = ap.parse_args()
    raw = load_rows(args.input)
    rows = [normalize(r, i + 1) for i, r in enumerate(raw)]
    filtered = []
    for r in rows:
        region = str(r['region'] or '').lower()
        if region and region not in (args.region.lower(), 'jp', 'japan', '日本'):
            continue
        filtered.append(r)
    categories = {}
    for r in filtered:
        key = str(r['industry'] or 'unknown').lower()
        categories[key] = categories.get(key, 0) + 1
    if args.min_per_category:
        missing = [c for c in ALLOWED_CATEGORIES if categories.get(c, 0) < args.min_per_category]
        if missing:
            raise SystemExit('category quota not met: ' + ', '.join(sorted(missing)))
    manifest = {
        'schema_version': 'tiktok_jp_topads.v1',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'region': args.region,
        'source_policy': 'official_export_only_no_endpoint_bypass',
        'count': len(filtered),
        'category_counts': categories,
        'ads': filtered,
    }
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(json.dumps({'out': os.path.abspath(args.out), 'count': len(filtered), 'category_counts': categories}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
