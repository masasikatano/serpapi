# アーキテクチャ

## システム構成図

```
┌─────────────────┐     ┌─────────────┐     ┌─────────────┐
│ GitHub Actions  │────▶│   SerpAPI   │────▶│    Slack    │
│  (スケジュuled)  │     │  (Google検索) │     │  (通知送信)  │
└─────────────────┘     └─────────────┘     └─────────────┘
         │
         ▼
┌─────────────────┐
│ previous_results │  (前回結果のキャッシュ)
│    .json        │
└─────────────────┘
```

## データフロー

1. **GitHub Actions** が日本時間12時にトリガー
2. `check_rank.py` が各キーワードでSerpAPIを呼び出し
3. 順位を解析し、前回結果と比較
4. Slackに通知メッセージを送信
5. 現在結果を `previous_results.json` に保存

## 主要コンポーネント

| コンポーネント | 責務 |
|--------------|------|
| `get_ranking()` | SerpAPI呼び出し、順位抽出 |
| `is_target_domain()` | ドメインマッチング（厳密） |
| `get_serp_features()` | SERP Features検出 |
| `format_rank_change()` | 順位変動フォーマット |

## APIパラメータ

```python
{
    "engine": "google",
    "gl": "jp",              # 国: 日本
    "hl": "ja",              # 言語: 日本語
    "location": "Tokyo,Japan", # 地域: 東京
    "device": "desktop",      # デバイス: デスクトップ
    "num": 100                # 取得件数: 100件
}
```
