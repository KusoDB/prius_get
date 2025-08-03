#!/usr/bin/env python3
"""
検索パラメータのテスト用スクリプト
"""

import requests
from bs4 import BeautifulSoup
import time

def test_search_params():
    """
    異なる検索パラメータをテストして結果数を確認
    """
    base_url = "https://gazoo.com/U-Car/search_result"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    test_cases = [
        # ケース1: 基本的な価格フィルタのみ
        {"Pmx": 160, "Tp": 1},
        
        # ケース2: パラメータなし（全件）
        {},
        
        # ケース3: padidを追加
        {"Pmx": 160, "Tp": 1, "padid": "ucarsearch_result"},
        
        # ケース4: 認定中古車フィルタを追加
        {"Pmx": 160, "Tp": 1, "Ntf": 1},
        
        # ケース5: 異なる価格範囲
        {"Pmx": 100, "Tp": 1},
    ]
    
    session = requests.Session()
    session.headers.update(headers)
    
    for i, params in enumerate(test_cases, 1):
        try:
            print(f"\n=== テストケース {i} ===")
            print(f"パラメータ: {params}")
            
            response = session.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 車両詳細ページへのリンク数をカウント
            detail_links = soup.find_all('a', href=lambda x: x and '/U-Car/detail?Id=' in x)
            print(f"車両リンク数: {len(detail_links)}")
            
            # 検索結果数の表示を探す
            result_count_elements = soup.find_all(text=lambda x: x and ('件' in str(x) or '台' in str(x)))
            for element in result_count_elements[:3]:  # 最初の3つだけ表示
                if any(char.isdigit() for char in str(element)):
                    print(f"結果数候補: {element.strip()}")
            
            # おすすめセクション vs メインリストの車両数
            recommended_section = soup.find('ul', id='slick_recommended')
            if recommended_section:
                recommended_cars = recommended_section.find_all('li')
                print(f"おすすめセクション車両数: {len(recommended_cars)}")
            
            # メインリストの車両数
            main_list = soup.find('ul', class_='search-result-list')
            if main_list:
                main_cars = main_list.find_all('li')
                print(f"メインリスト車両数: {len(main_cars)}")
            
            time.sleep(2)  # リクエスト間隔
            
        except Exception as e:
            print(f"エラー: {e}")

if __name__ == "__main__":
    test_search_params()