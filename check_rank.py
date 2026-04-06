import os
import requests
import json
from urllib.parse import urlparse
from datetime import datetime

# 環境変数からキーとURLを取得
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

# チェック対象のリスト（GitHub Variables の TARGETS_JSON から取得）
# 例: [{"keyword": "キーワード", "domain": "example.com"}]
TARGETS = json.loads(os.environ.get("TARGETS_JSON", "[]"))

def is_target_domain(link, target_domain):
    """ドメインマッチングを厳密に行う"""
    if not link:
        return False
    try:
        parsed = urlparse(link)
        hostname = parsed.netloc.lower()
        target = target_domain.lower()
        
        # www. を除去して比較
        hostname = hostname.replace("www.", "")
        target = target.replace("www.", "")
        
        # 完全一致またはサブドメインとして含まれる場合
        return hostname == target or hostname.endswith(f".{target}")
    except Exception:
        return False

def get_serp_features(data):
    """SERP Featuresの存在を確認"""
    features = []
    if data.get("knowledge_graph"):
        features.append("ナレッジグラフ")
    if data.get("local_results"):
        features.append("ローカルパック")
    if data.get("related_questions"):
        features.append("関連質問")
    if data.get("shopping_results"):
        features.append("ショッピング")
    if data.get("recipes_results"):
        features.append("レシピ")
    return features

def get_ranking(keyword, target_domain):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": keyword,
        "api_key": SERPAPI_KEY,
        "gl": "jp",                 # 日本
        "hl": "ja",                 # 日本語
        "location": "Tokyo,Japan",  # 東京からの検索をシミュレート
        "device": "desktop",        # デスクトップ検索
        "num": 100                  # 100位まで取得
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        result_info = {
            "rank": None,
            "url": None,
            "title": None,
            "serp_features": get_serp_features(data),
            "total_results": data.get("search_information", {}).get("total_results", "N/A"),
            "error": None
        }

        if "organic_results" in data:
            for result in data["organic_results"]:
                if is_target_domain(result.get("link", ""), target_domain):
                    result_info["rank"] = result.get("position")
                    result_info["url"] = result.get("link")
                    result_info["title"] = result.get("title")
                    return result_info
        
        # 結果が見つからない場合
        result_info["rank"] = None
        return result_info
        
    except Exception as e:
        return {
            "rank": None,
            "url": None,
            "title": None,
            "serp_features": [],
            "total_results": "N/A",
            "error": str(e)
        }

def load_previous_results():
    """前回の結果を読み込む"""
    try:
        with open("previous_results.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_current_results(results):
    """現在の結果を保存"""
    with open("previous_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def format_rank_change(current_rank, previous_rank):
    """順位変動をフォーマット"""
    if previous_rank is None or current_rank is None:
        return ""
    
    diff = previous_rank - current_rank  # 上昇はプラス、下降はマイナス
    if diff > 0:
        return f" (↑+{diff})"
    elif diff < 0:
        return f" (↓{diff})"
    return " (→0)"

def send_slack_message(message):
    payload = {"text": message}
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
    if response.status_code != 200:
        print(f"Slack送信エラー: {response.text}")

def format_rank_display(rank_info, previous_rank=None):
    """順位情報を表示用にフォーマット"""
    if rank_info.get("error"):
        return f"取得エラー ({rank_info['error']})"
    
    if rank_info["rank"] is None:
        rank_str = "圏外 (100位以降)"
    else:
        rank_str = f"{rank_info['rank']}位"
        if previous_rank is not None:
            rank_str += format_rank_change(rank_info["rank"], previous_rank)
    
    return rank_str

def build_detail_info(rank_info):
    """詳細情報を構築"""
    details = []
    
    # SERP Features
    if rank_info.get("serp_features"):
        details.append(f"SERP特徴: {', '.join(rank_info['serp_features'])}")
    
    return " | ".join(details) if details else ""

# メイン処理
if __name__ == "__main__":
    # 前回の結果を読み込み
    previous_results = load_previous_results()
    current_results = {}
    
    message_lines = ["*📊 本日の検索順位レポート*"]
    detail_lines = ["\n*詳細情報:*"]
    
    for target in TARGETS:
        keyword = target["keyword"]
        domain = target["domain"]
        target_key = f"{keyword}:{domain}"
        
        # 順位取得
        rank_info = get_ranking(keyword, domain)
        current_results[target_key] = rank_info["rank"]
        
        # 前回の順位を取得
        previous_rank = previous_results.get(target_key)
        
        # 表示用文字列
        rank_display = format_rank_display(rank_info, previous_rank)
        line = f"• 『{keyword}』: *{rank_display}* ({domain})"
        message_lines.append(line)
        print(line)
        
        # 詳細情報
        detail_info = build_detail_info(rank_info)
        if detail_info:
            detail_lines.append(f"• 『{keyword}』: {detail_info}")
    
    # 現在の結果を保存
    save_current_results(current_results)
    
    # メッセージ構築
    final_message = "\n".join(message_lines)
    if len(detail_lines) > 1:
        final_message += "\n" + "\n".join(detail_lines)
    
    # Slack通知
    if SLACK_WEBHOOK_URL:
        send_slack_message(final_message)
        print("\nSlackへ通知を送信しました。")
    else:
        print("\nエラー: SLACK_WEBHOOK_URLが設定されていません。")
