# テスト実行

ローカルでテストを実行します。

```bash
# 環境変数を設定してテスト
export SERPAPI_KEY="your_key"
export SLACK_WEBHOOK_URL="your_webhook"
export TARGETS_JSON='[{"keyword": "テスト", "domain": "example.com"}]'

python check_rank.py
```
