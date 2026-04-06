# 「昭和mtg」6位報告の調査結果

## 問題
Slack通知で「昭和mtg」が6位と報告されたが、実際にGoogle検索すると6位に該当サイト（mtg.syowa.workers.dev）が見つからない。

## 根本原因

### 1. 検索パーソナライゼーションの違い（主要因）
- **SerpAPI**: 非パーソナライズ化された中立的な結果を返す
- **手動検索**: ユーザーの検索履歴、位置情報、デバイス、ログイン状態に基づいてパーソナライズされる

### 2. ロケーション設定の不足
現在のコード:
```python
params = {
    "gl": "jp",     # 国: 日本
    "hl": "ja",     # 言語: 日本語
    # locationパラメータが欠落
}
```

`gl=jp`と`hl=ja`だけでは、日本国内のどの地域からの検索か指定されておらず、デフォルトの中立位置からの検索結果になります。

### 3. デバイス設定の未指定
- コードでは `device` パラメータが未設定（デフォルト: desktop）
- モバイル検索とデスクトップ検索では結果が異なる

### 4. SERP Featuresの影響
フィーチャースニペット、People Also Ask、ローカルパックなどが表示されると、画面上の見た目の順位とAPIの`position`値が一致しません。

例:
- フィーチャースニペット（position相当）が表示される
- その下にオーガニック結果1位（position=1）が表示
- 画面上では2番目に見えるが、API上はposition=1

### 5. 時間差による変動
検索結果は頻繁に変動します。通知時と確認時の間で順位が変動した可能性があります。

## 推奨対策

### 改善案1: locationパラメータの追加
```python
params = {
    "engine": "google",
    "q": keyword,
    "api_key": SERPAPI_KEY,
    "gl": "jp",
    "hl": "ja",
    "location": "Tokyo,Japan",  # 具体的な地域を指定
    "device": "desktop",         # 明示的にデバイスを指定
    "num": 100
}
```

### 改善案2: 複数パターンで検索
主要な都市（東京、大阪など）とデバイス（desktop/mobile）の組み合わせで検索し、結果を比較する。

### 改善案3: SERP Featuresを考慮した順位表示
```python
def get_ranking_with_context(keyword, target_domain):
    # ... API呼び出し ...
    
    serp_features = []
    if "knowledge_graph" in data:
        serp_features.append("Knowledge Graph")
    if "local_results" in data:
        serp_features.append("Local Pack")
    if "related_questions" in data:
        serp_features.append("PAA")
    
    for result in data.get("organic_results", []):
        if target_domain in result.get("link", ""):
            position = result.get("position")
            features_info = f" (SERP Features: {', '.join(serp_features)})" if serp_features else ""
            return f"{position}位{features_info}"
    
    return "圏外 (100位以降)"
```

### 改善案4: ドメインマッチングの厳密化
```python
from urllib.parse import urlparse

def is_target_domain(link, target_domain):
    """ドメインマッチングを厳密に行う"""
    parsed = urlparse(link)
    hostname = parsed.netloc.lower()
    
    # www. を除去して比較
    hostname = hostname.replace("www.", "")
    target = target_domain.lower().replace("www.", "")
    
    return hostname == target or hostname.endswith(f".{target}")
```

## 結論
SerpAPIの結果と手動検索結果が異なるのは、**検索パーソナライゼーションの違い**が最も大きな要因です。これはSerpAPIのFAQでも「Different results than manual search」として言及されています。より正確な追跡のためには、`location`パラメータの明示的な設定と、複数条件での検索結果の比較が推奨されます。
