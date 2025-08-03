#!/usr/bin/env python3
"""
簡単に検索を実行するためのスクリプト
"""

from toyota_used_car_search import ToyotaUsedCarSearch
from config import SEARCH_PRESETS, DEFAULT_SEARCH_CONFIG
import sys


def run_preset_search(preset_name: str):
    """
    プリセット検索を実行
    """
    if preset_name not in SEARCH_PRESETS:
        print(f"エラー: プリセット '{preset_name}' が見つかりません")
        print(f"利用可能なプリセット: {', '.join(SEARCH_PRESETS.keys())}")
        return
    
    searcher = ToyotaUsedCarSearch()
    config = SEARCH_PRESETS[preset_name]
    
    print(f"プリセット '{preset_name}' で検索中...")
    print(f"検索条件: {config}")
    
    results = searcher.search_cars(**config)
    searcher.display_results(results)


def run_custom_search():
    """
    カスタム検索を実行
    """
    searcher = ToyotaUsedCarSearch()
    
    print("カスタム検索を実行します")
    print("検索条件を入力してください（空欄でデフォルト値）:")
    
    # 価格上限
    price_input = input(f"価格上限（万円、デフォルト: {DEFAULT_SEARCH_CONFIG['price_max']}): ")
    price_max = int(price_input) if price_input.strip() else DEFAULT_SEARCH_CONFIG['price_max']
    
    # 検索実行
    results = searcher.search_cars(
        price_max=price_max,
        certified_only=DEFAULT_SEARCH_CONFIG['certified_only']
    )
    
    searcher.display_results(results)


def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python run_search.py <preset_name>")
        print("  python run_search.py custom")
        print("\n利用可能なプリセット:")
        for name, config in SEARCH_PRESETS.items():
            print(f"  {name}: {config}")
        return
    
    command = sys.argv[1]
    
    if command == "custom":
        run_custom_search()
    elif command in SEARCH_PRESETS:
        run_preset_search(command)
    else:
        print(f"エラー: 不明なコマンド '{command}'")
        main()


if __name__ == "__main__":
    main()