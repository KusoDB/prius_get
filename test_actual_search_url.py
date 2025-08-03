import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def test_actual_search_url():
    # 実際の絞り込み検索URL
    actual_url = "https://toyota.jp/ucar/carlist/?Tval=1&chk-detail-tvalue-sp-check=1&Cn=01_プリウス&Ymn=2019&Sc=0&Drv=2&Pmx=160"
    
    print("=== 実際の検索URLのパラメータ分析 ===")
    print("Tval=1 → トヨタ認定中古車のみ")
    print("chk-detail-tvalue-sp-check=1 → 詳細フィルタチェック")
    print("Cn=01_プリウス → 車名: プリウス")
    print("Ymn=2019 → 年式最小: 2019年")
    print("Sc=0 → 不明（0の意味）")
    print("Drv=2 → 駆動方式: 2（4WD/e-Four?）")
    print("Pmx=160 → 価格最大: 160万円")
    print(f"\nアクセスURL: {actual_url}")
    
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        
        try:
            await page.goto(actual_url)
            await page.wait_for_timeout(5000)
            
            print("\n=== 実際の検索結果を取得 ===")
            
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            
            # まず車両数を確認
            result_count_elem = soup.select_one(".search-result-count, .result-count")
            if result_count_elem:
                print(f"検索結果件数: {result_count_elem.get_text(strip=True)}")
            
            # 153.7万円を探す
            price_153_elements = soup.find_all(string=lambda text: text and "153" in text)
            if price_153_elements:
                print(f"*** 153を含む要素発見: {len(price_153_elements)}個 ***")
                for elem in price_153_elements:
                    print(f"  - '{elem.strip()}'")
                    parent = elem.parent
                    if parent:
                        print(f"    親要素: <{parent.name}> class={parent.get('class', [])}")
            
            # プリウス A ツーリングセレクションを探す
            touring_elements = soup.find_all(string=lambda text: text and "プリウス" in text and ("ツーリング" in text or "A ツー" in text))
            if touring_elements:
                print(f"*** プリウス ツーリング発見: {len(touring_elements)}個 ***")
                for elem in touring_elements:
                    print(f"  - '{elem.strip()}'")
            
            # 車名一覧を取得
            car_names = soup.select("p.detais-name2")
            print(f"\n車名要素: {len(car_names)}個")
            
            found_cars = []
            for name_elem in car_names:
                car_name = name_elem.get_text(strip=True)
                
                # 価格を探す
                parent = name_elem.parent
                price = "価格不明"
                while parent and parent.name != 'body':
                    price_elem = parent.select_one("p.car-price-sub")
                    if price_elem:
                        price = price_elem.get_text(strip=True)
                        break
                    parent = parent.parent
                
                # NEWバッジを確認
                is_new = False
                if parent:
                    context = parent.get_text()
                    is_new = "NEW" in context or "新着" in context
                
                car_info = f"{car_name} — {price}" + (" [NEW]" if is_new else "")
                found_cars.append(car_info)
                print(f"  • {car_info}")
            
            print(f"\n=== 検索結果まとめ ===")
            print(f"条件: プリウス, 2019年以降, 4WD/e-Four, 160万円以下")
            print(f"該当車両: {len(found_cars)}台")
            
            if found_cars:
                print("\n検出された車両:")
                for car in found_cars:
                    print(f"• {car}")
            else:
                print("条件に合う車両が見つかりませんでした")
                
            # HTMLファイルも保存して詳細確認
            with open("actual_search_result.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("\nHTMLファイル保存: actual_search_result.html")
            
        except Exception as e:
            print(f"エラー: {e}")
        
        await browser.close()

    # パラメータを使って他のバリエーションもテスト
    print(f"\n=== パラメータバリエーションテスト ===")
    await test_parameter_variations()

async def test_parameter_variations():
    base_url = "https://toyota.jp/ucar/carlist/"
    
    variations = [
        # 4WD条件を外してテスト
        "?Tval=1&Cn=01_プリウス&Ymn=2019&Pmx=160",
        # 価格上限を上げてテスト
        "?Tval=1&Cn=01_プリウス&Ymn=2019&Drv=2&Pmx=200",
        # 年式条件を外してテスト
        "?Tval=1&Cn=01_プリウス&Drv=2&Pmx=160",
        # 最低限の条件のみ
        "?Tval=1&Cn=01_プリウス&Pmx=160",
    ]
    
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        
        for i, params in enumerate(variations):
            url = base_url + params
            print(f"\nバリエーション {i+1}: {params}")
            
            try:
                await page.goto(url)
                await page.wait_for_timeout(3000)
                
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")
                
                # 153.7万円を探す
                price_153_elements = soup.find_all(string=lambda text: text and "153" in text)
                if price_153_elements:
                    print(f"*** バリエーション {i+1}で153発見! ***")
                    for elem in price_153_elements:
                        print(f"  - {elem.strip()}")
                
                # プリウス数をカウント
                car_names = soup.select("p.detais-name2")
                prius_count = 0
                for name_elem in car_names:
                    if "プリウス" in name_elem.get_text():
                        prius_count += 1
                
                print(f"プリウス発見数: {prius_count}台")
                
            except Exception as e:
                print(f"バリエーション {i+1} でエラー: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_actual_search_url())