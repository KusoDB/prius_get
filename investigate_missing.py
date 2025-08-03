import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def investigate_missing_cars():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        
        # プリウス専用URL
        prius_url = "https://toyota.jp/ucar/carlist/?car_series=prius&year_from=2019&price_max=160"
        await page.goto(prius_url)
        await page.wait_for_timeout(5000)
        
        html = await page.content()
        await browser.close()
    
    soup = BeautifulSoup(html, "html.parser")
    
    print("=== 全価格要素の詳細調査 ===")
    
    # 153.7万円を含む要素を直接検索
    target_price_elements = soup.find_all(string=lambda text: text and "153.7" in text)
    print(f"'153.7'を含む要素: {len(target_price_elements)}個")
    
    for i, elem in enumerate(target_price_elements):
        print(f"\n要素 {i+1}: '{elem.strip()}'")
        parent = elem.parent
        if parent:
            print(f"親要素: <{parent.name}> class={parent.get('class', [])}")
            # 親要素の周辺コンテキストを確認
            context = parent.parent.get_text(strip=True) if parent.parent else ""
            if len(context) > 200:
                context = context[:200] + "..."
            print(f"コンテキスト: {context}")
    
    # 'NEW'バッジを含む要素を検索
    print("\n=== NEWバッジの調査 ===")
    new_elements = soup.find_all(string=lambda text: text and ("NEW" in text.upper() or "新着" in text))
    print(f"NEWバッジ要素: {len(new_elements)}個")
    
    for i, elem in enumerate(new_elements[:5]):
        print(f"\nNEW要素 {i+1}: '{elem.strip()}'")
        parent = elem.parent
        if parent:
            print(f"親要素: <{parent.name}> class={parent.get('class', [])}")
    
    # プリウス A ツーリングセレクションを検索
    print("\n=== プリウス A ツーリングセレクション検索 ===")
    touring_elements = soup.find_all(string=lambda text: text and ("ツーリング" in text or "A ツー" in text))
    print(f"ツーリング関連要素: {len(touring_elements)}個")
    
    for i, elem in enumerate(touring_elements):
        print(f"\nツーリング要素 {i+1}: '{elem.strip()}'")
        parent = elem.parent
        if parent:
            print(f"親要素: <{parent.name}> class={parent.get('class', [])}")
            
    # 現在使用しているセレクタでの結果
    print("\n=== 現在のセレクタでの結果 ===")
    car_names = soup.select("p.detais-name2")
    print(f"車名要素 (p.detais-name2): {len(car_names)}個")
    
    for i, name_elem in enumerate(car_names):
        car_name = name_elem.get_text(strip=True)
        print(f"車名 {i+1}: {car_name}")
        
        # 同じ親から価格を探す
        parent = name_elem.parent
        while parent and parent.name != 'body':
            price_elem = parent.select_one("p.car-price-sub")
            if price_elem:
                price = price_elem.get_text(strip=True)
                print(f"  -> 価格: {price}")
                break
            parent = parent.parent

if __name__ == "__main__":
    asyncio.run(investigate_missing_cars())