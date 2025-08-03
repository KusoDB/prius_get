import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def debug_real_search():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)  # ブラウザを表示
        page = await browser.new_page()
        
        print("=== 実際の手動検索を再現 ===")
        
        # まず基本のプリウス検索ページにアクセス
        base_url = "https://toyota.jp/ucar/carlist/?padid=from_jpucar_header_search"
        await page.goto(base_url)
        await page.wait_for_timeout(3000)
        
        print("1. 基本ページにアクセス完了")
        
        # 検索条件変更ボタンを探してクリック
        try:
            # より具体的なセレクタで試す
            change_button = page.locator("text=検索条件を変更する").first
            await change_button.wait_for(state="visible", timeout=10000)
            await change_button.click()
            await page.wait_for_timeout(2000)
            print("2. 検索条件変更ボタンをクリック成功")
            
            # メーカー・車種でプリウスを選択
            prius_option = page.locator("text=プリウス").first
            if await prius_option.is_visible():
                await prius_option.click()
                print("3. プリウスを選択")
            
            # 価格設定（160万円以下）
            price_max_input = page.locator("input").filter(has_text="最高価格")
            if await price_max_input.count() > 0:
                await price_max_input.fill("160")
                print("4. 最高価格160万円を設定")
            
            # 年式設定（2019年以降）
            year_select = page.locator("select").filter(has_text="年式")
            if await year_select.count() > 0:
                await year_select.select_option("2019")
                print("5. 年式2019年以降を設定")
            
            # 検索実行
            search_button = page.locator("text=この条件で検索").first
            if await search_button.is_visible():
                await search_button.click()
                await page.wait_for_timeout(5000)
                print("6. 検索実行完了")
            
        except Exception as e:
            print(f"手動検索再現エラー: {e}")
            print("フィルタなしでプリウス専用URLに直接アクセス")
            await page.goto("https://toyota.jp/ucar/carlist/?car_series=prius")
            await page.wait_for_timeout(5000)
        
        # 現在のURLを確認
        current_url = page.url
        print(f"現在のURL: {current_url}")
        
        # スクリーンショット撮影
        await page.screenshot(path="current_search_result.png")
        print("スクリーンショット保存: current_search_result.png")
        
        # ページのHTMLを取得して詳細分析
        html = await page.content()
        
        input("ブラウザで結果を確認してからEnterを押してください...")
        await browser.close()
    
    # HTMLを詳細分析
    soup = BeautifulSoup(html, "html.parser")
    
    print("\n=== 153.7万円の車両を直接検索 ===")
    price_153_elements = soup.find_all(string=lambda text: text and ("153" in text or "153.7" in text))
    print(f"'153'を含む要素: {len(price_153_elements)}個")
    
    for elem in price_153_elements:
        print(f"発見: '{elem.strip()}'")
        parent = elem.parent
        if parent:
            print(f"  親要素: <{parent.name}> class={parent.get('class', [])}")
            # 周辺コンテキストを確認
            context = parent.parent.get_text(strip=True)[:300] if parent.parent else ""
            print(f"  コンテキスト: {context}")
    
    print("\n=== プリウス A ツーリングセレクションを検索 ===")
    touring_elements = soup.find_all(string=lambda text: text and ("A ツーリング" in text or "Aツーリング" in text))
    print(f"'A ツーリング'を含む要素: {len(touring_elements)}個")
    
    for elem in touring_elements:
        print(f"発見: '{elem.strip()}'")
        parent = elem.parent
        if parent:
            print(f"  親要素: <{parent.name}> class={parent.get('class', [])}")
    
    # すべての価格要素を一覧表示
    print("\n=== すべての価格要素（万円）===")
    all_prices = soup.find_all(string=lambda text: text and "万円" in text)
    unique_prices = set()
    for price in all_prices:
        price_text = price.strip()
        if len(price_text) < 20 and price_text not in unique_prices:  # 短い価格文字列のみ
            unique_prices.add(price_text)
            print(f"価格: {price_text}")
    
    print(f"\n発見された価格の種類: {len(unique_prices)}個")

if __name__ == "__main__":
    asyncio.run(debug_real_search())