import os
import requests
import json

# 環境変数からキーとURLを取得
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

# チェック対象のリスト（GitHub Variables の TARGETS_JSON から取得）
# 例: [{"keyword": "キーワード", "domain": "example.com"}]
TARGETS = json.loads(os.environ.get("TARGETS_JSON", "[]"))

def get_ranking(keyword, target_domain):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": keyword,
        "api_key": SERPAPI_KEY,
        "gl": "jp",     # 日本
        "hl": "ja",     # 日本語
        "num": 100      # 100位まで取得
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # エラーがあれば例外を発生させる
        data = response.json()

        if "organic_results" in data:
            for result in data["organic_results"]:
                if target_domain in result.get("link", ""):
                    return f"{result.get('position')}位"
        return "圏外 (100位以降)"
    except Exception as e:
        return f"取得エラー ({e})"

def send_slack_message(message):
    payload = {"text": message}
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
    if response.status_code != 200:
        print(f"Slack送信エラー: {response.text}")

# メイン処理
if __name__ == "__main__":
    message_lines = ["*📊 本日の検索順位レポート*"]
    
    for target in TARGETS:
        rank = get_ranking(target["keyword"], target["domain"])
        line = f"• 『{target['keyword']}』: *{rank}* ({target['domain']})"
        message_lines.append(line)
        print(line) # GitHub Actionsのログ確認用
    
    # リストを改行で結合してSlackへ送信
    final_message = "\n".join(message_lines)
    
    if SLACK_WEBHOOK_URL:
        send_slack_message(final_message)
        print("Slackへ通知を送信しました。")
    else:
        print("エラー: SLACK_WEBHOOK_URLが設定されていません。")
