#!/usr/bin/env python3
"""
トヨタ認定中古車の検索を自動化するスクリプト
"""

import requests
import json
from urllib.parse import urlencode
from typing import Dict, List, Optional
import time
import re
from bs4 import BeautifulSoup


class ToyotaUsedCarSearch:
    def __init__(self):
        self.base_url = "https://gazoo.com/U-Car/"
        self.search_url = "https://gazoo.com/U-Car/search_result"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_cars(self, 
                   price_min: Optional[int] = None,
                   price_max: Optional[int] = None,
                   body_type: Optional[str] = None,
                   certified_only: bool = True,
                   mileage_max: Optional[int] = None,
                   year_min: Optional[int] = None,
                   year_max: Optional[int] = None) -> List[Dict]:
        """
        中古車を検索する
        
        Args:
            price_min: 最低価格（万円）
            price_max: 最高価格（万円）
            body_type: ボディタイプ（'compact', 'sedan', 'suv', 'minivan' など）
            certified_only: トヨタ認定中古車のみ
            mileage_max: 最大走行距離（km）
            year_min: 最低年式
            year_max: 最高年式
        
        Returns:
            検索結果のリスト
        """
        
        params = {}
        
        # 価格条件（最高価格のみ対応）
        if price_max:
            # 価格フィルタは正常に動作するので残す
            params['Pmx'] = price_max  # 万円単位
            params['Tp'] = 1  # 総支払額
            
        # 4WD条件
        if body_type == '4wd':
            params['Drv'] = 2
            
        # スライドドア
        if body_type == 'minivan':
            params['Sdr'] = 1
            
        # トヨタ認定中古車のみ（パラメータ名を確認）
        if certified_only:
            # 認定中古車フィルタのパラメータを調査中
            pass
        
        try:
            print(f"検索URL: {self.search_url}")
            print(f"パラメータ: {params}")
            
            response = self.session.get(self.search_url, params=params, timeout=30)
            response.raise_for_status()
            
            print(f"レスポンスステータス: {response.status_code}")
            
            # HTMLパースして結果を抽出
            results = self._parse_search_results(response.text)
            
            # リクエスト間隔を空ける
            time.sleep(1)
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"検索エラー: {e}")
            return []
    
    def _parse_search_results(self, html_content: str) -> List[Dict]:
        """
        検索結果のHTMLをパースして車両情報を抽出
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            cars = []
            
            # HTMLの構造に基づいて直接車両情報を抽出
            
            # 方法1: おすすめ車両セクション（上部の横スクロール）
            recommended_cars = soup.find_all('li')
            for li in recommended_cars:
                # 車両詳細リンクがあるかチェック
                detail_link = li.find('a', href=lambda x: x and '/U-Car/detail?Id=' in x)
                if not detail_link:
                    continue
                
                try:
                    car_info = {}
                    car_info['url'] = 'https://gazoo.com' + detail_link['href']
                    
                    # 車両名（dt class="carname"内のテキスト）
                    carname_dt = li.find('dt', class_='carname')
                    if carname_dt:
                        carname_link = carname_dt.find('a')
                        if carname_link:
                            # 「トヨタ」を除去して車名のみ取得
                            name_parts = carname_link.get_text().strip().split()
                            if len(name_parts) > 1 and name_parts[0] == 'トヨタ':
                                car_info['name'] = ' '.join(name_parts[1:])
                            else:
                                car_info['name'] = carname_link.get_text().strip()
                    
                    # 価格（dl class="totalprice"内）
                    totalprice_dl = li.find('dl', class_='totalprice')
                    if totalprice_dl:
                        price_dd = totalprice_dl.find('dd')
                        if price_dd:
                            # <span class="value">数値<span class="price_decimal">.小数</span></span>万円
                            value_span = price_dd.find('span', class_='value')
                            if value_span:
                                # まず小数点部分を取得
                                decimal_span = value_span.find('span', class_='price_decimal')
                                if decimal_span:
                                    # 小数点部分のテキストを取得
                                    decimal_text = decimal_span.get_text().strip()
                                    # 小数点部分を一時的に削除してメイン数値を取得
                                    temp_span = value_span.get_text()
                                    main_number = temp_span.replace(decimal_text, '').strip()
                                    # 結合
                                    car_info['price'] = main_number + decimal_text
                                else:
                                    car_info['price'] = value_span.get_text().strip()
                    
                    # 基本情報が取得できた場合のみ追加
                    if 'name' in car_info and 'price' in car_info:
                        cars.append(car_info)
                        
                except Exception as e:
                    continue
            
            # 方法2: メインの検索結果リスト
            # dt要素で車両情報を含むものを探す
            main_results = soup.find_all('dt', class_=lambda x: x is None or 'carname' not in str(x))
            
            for dt in main_results:
                # wrap_linkクラスのaタグを持つdtを探す
                wrap_link = dt.find('a', class_='wrap_link')
                if not wrap_link or '/U-Car/detail?Id=' not in wrap_link.get('href', ''):
                    continue
                
                try:
                    car_info = {}
                    car_info['url'] = 'https://gazoo.com' + wrap_link['href']
                    
                    # 同じdd要素内の情報を取得
                    parent_dd = dt.find_next_sibling('dd')
                    if not parent_dd:
                        continue
                    
                    # 車両名（imgのalt属性から）
                    img_elem = parent_dd.find('img')
                    if img_elem and img_elem.get('alt'):
                        alt_text = img_elem['alt'].strip()
                        # "トヨタ "を除去
                        if alt_text.startswith('トヨタ '):
                            car_info['name'] = alt_text[3:]
                        else:
                            car_info['name'] = alt_text
                    
                    # 価格（支払総額の数値部分）
                    price_area = parent_dd.find('ul', class_='price_area')
                    if price_area:
                        price_number = price_area.find('p', class_='number')
                        if price_number:
                            # 数値部分を抽出
                            price_text = price_number.get_text().replace('万円', '').replace('\n', '').strip()
                            car_info['price'] = price_text
                    
                    # 年式と走行距離（detail_area内のテキストから）
                    detail_area = parent_dd.find('div', class_='detail_area')
                    if detail_area:
                        detail_text = detail_area.get_text()
                        
                        # 年式を抽出
                        year_match = re.search(r'(\d{4})年', detail_text)
                        if year_match:
                            car_info['year'] = year_match.group(1)
                        
                        # 走行距離を抽出
                        mileage_patterns = [
                            r'(\d{1,2}(?:,\d{3})*)\s*km',
                            r'(\d+(?:\.\d+)?)\s*万km'
                        ]
                        for pattern in mileage_patterns:
                            mileage_match = re.search(pattern, detail_text)
                            if mileage_match:
                                if '万km' in mileage_match.group(0):
                                    mileage_num = float(mileage_match.group(1)) * 10000
                                    car_info['mileage'] = f"{int(mileage_num):,}"
                                else:
                                    car_info['mileage'] = mileage_match.group(1)
                                break
                        
                        # 販売店名を抽出
                        dealer_match = re.search(r'トヨタモビリティ[^\n\r]+', detail_text)
                        if dealer_match:
                            car_info['dealer'] = dealer_match.group(0).strip()
                    
                    # 基本情報が取得できた場合のみ追加
                    if 'name' in car_info and 'price' in car_info:
                        cars.append(car_info)
                        
                except Exception as e:
                    continue
            
            print(f"抽出された車両数: {len(cars)}")
            return cars
            
        except Exception as e:
            print(f"HTMLパースエラー: {e}")
            return []
    
    def display_results(self, results: List[Dict]):
        """
        検索結果を見やすく表示
        """
        if not results:
            print("検索結果が見つかりませんでした。")
            return
            
        print(f"\n検索結果: {len(results)}件")
        print("-" * 80)
        
        for i, car in enumerate(results, 1):
            print(f"{i}. {car.get('name', 'N/A')}")
            print(f"   価格: {car.get('price', 'N/A')}万円")
            print(f"   年式: {car.get('year', 'N/A')}")
            print(f"   走行距離: {car.get('mileage', 'N/A')}km")
            print(f"   販売店: {car.get('dealer', 'N/A')}")
            print(f"   URL: {car.get('url', 'N/A')}")
            print()


def main():
    """
    メイン関数 - 使用例
    """
    searcher = ToyotaUsedCarSearch()
    
    # 検索条件の例
    print("トヨタ認定中古車を検索しています...")
    
    # 100万円以下の車両を検索
    results = searcher.search_cars(
        price_max=100,
        certified_only=True
    )
    
    searcher.display_results(results)


if __name__ == "__main__":
    main()