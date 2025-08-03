import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def comprehensive_search():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        
        # 複数の検索パターンを試す
        search_patterns = [
            # 基本のプリウス検索
            "https://toyota.jp/ucar/carlist/?car_series=prius",
            # 価格条件付き
            "https://toyota.jp/ucar/carlist/?car_series=prius&price_max=200",
            # 年式条件付き  
            "https://toyota.jp/ucar/carlist/?car_series=prius&year_from=2019",
            # 価格・年式両方
            "https://toyota.jp/ucar/carlist/?car_series=prius&price_max=200&year_from=2019",
            # 新着のみ
            "https://toyota.jp/ucar/carlist/?car_series=prius&new_arrival=1",
            # 基本検索（車種指定なし）
            "https://toyota.jp/ucar/carlist/",
            # プリウス + 全価格帯
            "https://toyota.jp/ucar/carlist/?car_series=prius&price_max=1000",
        ]
        
        all_found_cars = set()
        
        for i, url in enumerate(search_patterns):
            print(f"\n=== パターン {i+1}: {url} ===")
            try:
                await page.goto(url)
                await page.wait_for_timeout(4000)
                
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")
                
                # 153.7万円を探す
                price_153_elements = soup.find_all(string=lambda text: text and ("153" in text))
                if price_153_elements:
                    print(f"*** 153を含む要素発見: {len(price_153_elements)}個 ***")
                    for elem in price_153_elements:
                        print(f"  - {elem.strip()}")
                
                # プリウス A ツーリングを探す
                touring_elements = soup.find_all(string=lambda text: text and "プリウス" in text and ("ツーリング" in text or "A ツー" in text))
                if touring_elements:
                    print(f"*** プリウス ツーリング発見: {len(touring_elements)}個 ***")
                    for elem in touring_elements:
                        print(f"  - {elem.strip()}")
                
                # 車名一覧を取得
                car_names = soup.select("p.detais-name2")
                print(f"車名要素: {len(car_names)}個")
                
                pattern_cars = set()
                for name_elem in car_names:
                    car_name = name_elem.get_text(strip=True)
                    if "プリウス" in car_name:
                        # 価格を探す
                        parent = name_elem.parent
                        price = "価格不明"
                        while parent and parent.name != 'body':
                            price_elem = parent.select_one("p.car-price-sub")
                            if price_elem:
                                price = price_elem.get_text(strip=True)
                                break
                            parent = parent.parent
                        
                        car_info = f"{car_name} — {price}"
                        pattern_cars.add(car_info)
                        all_found_cars.add(car_info)
                
                if pattern_cars:
                    print("このパターンで見つかったプリウス:")
                    for car in sorted(pattern_cars):
                        print(f"  • {car}")
                else:
                    print("プリウスが見つかりませんでした")
                    
            except Exception as e:
                print(f"パターン {i+1} でエラー: {e}")
        
        await browser.close()
        
        print(f"\n=== 総合結果 ===")
        print(f"全パターンで発見されたプリウス: {len(all_found_cars)}種類")
        
        if all_found_cars:
            print("\n発見されたすべてのプリウス:")
            for car in sorted(all_found_cars):
                print(f"• {car}")
        
        # 153.7万円が見つからない場合の追加調査
        print(f"\n*** 153.7万円のプリウス A ツーリングセレクションが見つからない理由 ***")
        print("1. 地域限定表示の可能性")
        print("2. 売約済みになった可能性") 
        print("3. 異なる検索条件が必要な可能性")
        print("4. ページネーション（2ページ目以降）の可能性")
        print("5. JavaScriptによる動的読み込みの可能性")

if __name__ == "__main__":
    asyncio.run(comprehensive_search())