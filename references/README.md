# BytePlus Reference Assets

ここは人物・場所・商品・音声リファレンスの管理場所です。

## 注意

BytePlusへはローカルWindowsパスをそのまま送れません。次のいずれかにします。

- BytePlus/LAS Material Libraryへアップロードし、`asset://ASSET_ID` を使う
- 認証不要で一時URLが有効な公開HTTPS URLを使う
- 音声・画像は仕様に応じてBase64化する

`BYTEPLUS_REFERENCE_CONTENT` にはカンマ区切りでURLまたは `asset://...` を指定できます。

例:

```env
BYTEPLUS_REFERENCE_CONTENT=asset://character_front,asset://character_45,asset://character_full
```

実ファイルはこのフォルダに保存して構いませんが、アップロード後のAsset IDを `references.json` に記録してください。
