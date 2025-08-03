import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def test_with_different_locations():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        
        # 異なる地域からアクセスを試す
        locations = [
            {"name": "東京", "coords": {"latitude": 35.6762, "longitude": 139.6503}},
            {"name": "大阪", "coords": {"latitude": 34.6937, "longitude": 135.5023}},
            {"name": "名古屋", "coords": {"latitude": 35.1815, "longitude": 136.9066}},
            {"name": "福岡", "coords": {"latitude": 33.5904, "longitude": 130.4017}},
        ]
        
        all_results = {}
        
        for location in locations:
            print(f"\n=== {location['name']}からアクセス ===")
            
            # 位置情報を設定
            await page.context.set_geolocation(location['coords'])
            await page.context.grant_permissions(['geolocation'])
            
            try:
                # プリウス検索ページにアクセス
                await page.goto("https://toyota.jp/ucar/carlist/?car_series=prius")
                await page.wait_for_timeout(5000)  # 位置情報取得待ち
                
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")
                
                # 153.7万円を探す
                price_153_elements = soup.find_all(string=lambda text: text and "153" in text)
                if price_153_elements:
                    print(f"*** {location['name']}で153発見! ***")
                    for elem in price_153_elements:
                        print(f"  - {elem.strip()}")
                
                # プリウス一覧を取得
                car_names = soup.select("p.detais-name2")
                location_cars = set()
                
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
                        location_cars.add(car_info)
                
                all_results[location['name']] = location_cars
                
                print(f"{location['name']}で見つかったプリウス: {len(location_cars)}台")
                for car in sorted(location_cars):
                    print(f"  • {car}")
                    
            except Exception as e:
                print(f"{location['name']}でエラー: {e}")
                all_results[location['name']] = set()
        
        await browser.close()
        
        print(f"\n=== 地域別結果比較 ===")
        all_unique_cars = set()
        for location_name, cars in all_results.items():
            all_unique_cars.update(cars)
            print(f"{location_name}: {len(cars)}台")
        
        print(f"\n全地域で発見された車両総数: {len(all_unique_cars)}台")
        
        if len(all_unique_cars) > 3:
            print("*** 地域によって表示が異なることを確認! ***")
            for car in sorted(all_unique_cars):
                print(f"• {car}")
        else:
            print("すべての地域で同じ結果")
            
        # 追加でページネーションも確認
        print(f"\n=== ページネーション確認 ===")
        await check_pagination(pw)

async def check_pagination(pw):
    browser = await pw.chromium.launch()
    page = await browser.new_page()
    
    try:
        await page.goto("https://toyota.jp/ucar/carlist/?car_series=prius")
        await page.wait_for_timeout(3000)
        
        # ページネーションボタンを探す
        next_buttons = await page.query_selector_all("a:has-text('次へ'), a:has-text('>')")
        pagination_links = await page.query_selector_all("a[href*='page=']")
        
        print(f"次へボタン: {len(next_buttons)}個")
        print(f"ページネーションリンク: {len(pagination_links)}個")
        
        if next_buttons or pagination_links:
            print("*** ページネーション発見 - 2ページ目以降を確認 ***")
            if next_buttons:
                await next_buttons[0].click()
                await page.wait_for_timeout(3000)
                
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")
                
                # 2ページ目で153.7万円を探す
                price_153_elements = soup.find_all(string=lambda text: text and "153" in text)
                if price_153_elements:
                    print("*** 2ページ目で153発見! ***")
                    for elem in price_153_elements:
                        print(f"  - {elem.strip()}")
        else:
            print("ページネーションなし - 1ページのみ")
            
    except Exception as e:
        print(f"ページネーション確認エラー: {e}")
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(test_with_different_locations())