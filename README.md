# SEO Rank Checker

GitHub Actions + SerpAPI を使って、指定したキーワードで自分のサイトが Google 何位に表示されているかを毎日チェックし、結果を Slack に通知するツール。

## 機能

- 毎日日本時間 **午後12時**（UTC 3:00）に自動実行
- GitHub の画面から **手動実行**も可能
- 指定したキーワード × ドメインの組み合わせで Google 検索順位（最大100位まで）を取得
- 結果を Slack に投稿
- **前回との順位変動を表示** (↑↓)
- **SERP Features（ナレッジグラフ、ローカルパック等）の検出**
- **東京からのデスクトップ検索をシミュレート**（locationパラメータ指定）
- **厳密なドメインマッチング**（サブドメイン対応）

## セットアップ

### 1. GitHub Secrets / Variables の設定

リポジトリの **Settings > Secrets and variables > Actions** に以下を登録する。

**Secrets**（機密情報）

| Secret 名           | 説明                                          |
| ------------------- | --------------------------------------------- |
| `SERPAPI_KEY`       | SerpAPI の API キー                           |
| `SLACK_WEBHOOK_URL` | Slack の Incoming Webhook URL                 |

**Variables**（非機密の設定値）

| Variable 名    | 説明                                                    |
| -------------- | ------------------------------------------------------- |
| `TARGETS_JSON` | チェック対象のキーワードとドメインを JSON 配列で指定する |

`TARGETS_JSON` の値の例：

```json
[
  {"keyword": "チェックしたいキーワード", "domain": "example.com"},
  {"keyword": "別のキーワード", "domain": "example.com"}
]
```

### 2. 実行確認

Actions タブから **SEO Rank Checker to Slack** を選択し、**Run workflow** で手動実行して動作を確認する。

## 必要な環境変数一覧

| 種別     | 変数名              | 取得・設定場所                                                      |
| -------- | ------------------- | ------------------------------------------------------------------- |
| Secret   | `SERPAPI_KEY`       | [SerpAPI](https://serpapi.com/) のダッシュボード > API Key          |
| Secret   | `SLACK_WEBHOOK_URL` | Slack App の **Incoming Webhooks** で作成した Webhook URL           |
| Variable | `TARGETS_JSON`      | GitHub の **Variables** に JSON 配列で直接入力（上記フォーマット参照）|

## ファイル構成

```
.
├── check_rank.py                          # 順位チェック & Slack 通知スクリプト
├── check_rank_investigation.md            # 調査レポート（参考資料）
├── previous_results.json                  # 前回の検索結果（自動生成・GitHub Actionsで保持）
└── .github/workflows/seo_slack_notify.yml # GitHub Actions ワークフロー定義
```

### previous_results.json について
- 前回の順位情報を保存し、順位変動（↑↓）を検出するために使用
- GitHub Actionsの`actions/cache`またはartifactで永続化
- 初回実行時は変動表示なし、2回目以降から比較表示

### 順位変動の見方
- `(↑+2)` → 前回より2位上昇
- `(↓-3)` → 前回より3位下降
- `(→0)` → 順位変動なし
