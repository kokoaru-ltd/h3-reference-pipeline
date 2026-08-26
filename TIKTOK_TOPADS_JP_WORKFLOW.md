# TikTok JP Top Ads 教師データ化

## 現在確認できたこと

公式Top Adsでは、地域、業種、目的、期間、広告言語、フォーマットを指定でき、リーチ/CTRで並び替え、2秒視聴率・6秒視聴率・CVR・いいね数を確認できる。Top Adsの掲載は広告主の許可が必要で、ログイン後に検索できる広告がある。旧Creative Center版は今後更新されず、TikTok One Inspirationへ移行中。

## 取得方法

1. [TikTok Top Ads日本語ページ](https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/ja)を開く。
2. 地域=日本、業種=Beauty/日用品/食品/ガジェット/ファッション/アプリに設定する。求人は別セットにする。
3. CTRで並び替え、各広告の「分析を確認」からCTR、2秒/6秒視聴率、CVR、広告尺、広告URL、サムネイルURLを保存する。
4. 50〜100本をCSVまたはJSONで保存し、次を実行する。

```powershell
python tiktok_topads_ingest.py .\topads_jp_export.json --out .\tiktok_jp_topads_manifest.json
```

この正規化器はログイン、CAPTCHA、bot検知、非公開APIの回避を行わない。取得できない場合は「取得不能」と記録し、ゼロ件とは扱わない。

## 下流解析

`tiktok_jp_topads_manifest.json`の各 `video_url` を動画解析器へ渡し、0/2/5/8/10/12/15秒フレーム、Scene Detect、Hook、商品登場秒、カメラ、字幕、Pattern interrupt、CTAを記録する。勝ちパターンは広告単位ではなく、`JP_BEAUTY_UGC_001` のようなRecipe単位へクラスタリングする。

