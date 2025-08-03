"""
検索条件の設定ファイル
"""

# 基本的な検索条件
DEFAULT_SEARCH_CONFIG = {
    "price_max": 150,  # 最高価格（万円）
    "certified_only": True,  # トヨタ認定中古車のみ
    "include_backup_camera": True,  # バックカメラ付きのみ
}

# よく使う検索パターン
SEARCH_PRESETS = {
    "budget_compact": {
        "price_max": 80,
        "body_type": "compact",
        "certified_only": True,
    },
    
    "family_minivan": {
        "price_max": 200,
        "body_type": "minivan",
        "certified_only": True,
    },
    
    "suv_4wd": {
        "price_max": 250,
        "body_type": "4wd",
        "certified_only": True,
    },
    
    "hybrid_eco": {
        "price_max": 180,
        "certified_only": True,
    },
}

# 地域設定（必要に応じて）
PREFERRED_REGIONS = [
    "東京",
    "神奈川", 
    "千葉",
    "埼玉"
]