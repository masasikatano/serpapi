# SEO Rank Checker Skill

## 概要

GitHub Actions + SerpAPI を使ってGoogle検索順位をチェックし、Slackに通知するツール。

## 主要ファイル

- `check_rank.py` - メインスクリプト
- `.github/workflows/seo_slack_notify.yml` - GitHub Actions設定

## 開発時の注意点

1. **APIコール数を増やさない**
   - 1キーワード = 1 APIコール
   - location/deviceパラメータを追加してもコール数は増えない

2. **ドメイン形式**
   - `summonerswar.monster`（プロトコルなし）
   - `mtg.syowa.workers.dev`（サブドメイン対応）

3. **順位変動の保存**
   - `previous_results.json` で前回結果を保持
   - GitHub Actions cacheで永続化

## 環境変数

| 名前 | 種別 | 説明 |
|------|------|------|
| SERPAPI_KEY | Secret | SerpAPIのAPIキー |
| SLACK_WEBHOOK_URL | Secret | Slack Webhook URL |
| TARGETS_JSON | Variable | 検索対象のJSON配列 |
