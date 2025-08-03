import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def analyze_page_structure():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        
        # プリウス専用URL
        prius_url = "https://toyota.jp/ucar/carlist/?car_series=prius"
        await page.goto(prius_url)
        await page.wait_for_timeout(5000)
        
        html = await page.content()
        await browser.close()
    
    soup = BeautifulSoup(html, "html.parser")
    
    # 車両リスト要素を探す
    print("=== 車両リスト構造の分析 ===")
    
    # 一般的な車両リスト要素のパターンを検索
    list_containers = [
        ".p-carlist-list",
        ".carlist-list", 
        ".car-list",
        ".vehicle-list",
        "[class*='carlist']",
        "[class*='vehicle']",
        "[class*='item-list']"
    ]
    
    found_container = None
    for container_sel in list_containers:
        containers = soup.select(container_sel)
        if containers:
            print(f"Found container: {container_sel} ({len(containers)} elements)")
            found_container = containers[0]
            break
    
    if found_container:
        print(f"Container HTML preview: {str(found_container)[:500]}...")
        
        # コンテナ内の直接の子要素を確認
        direct_children = found_container.find_all(recursive=False)
        print(f"\nDirect children: {len(direct_children)}")
        
        for i, child in enumerate(direct_children[:3]):
            print(f"\nChild {i+1}: {child.name} - {child.get('class', [])}")
            print(f"Content preview: {child.get_text(strip=True)[:200]}...")
    
    # 価格と車名を含む要素を直接検索
    print("\n=== 価格情報を含む要素の検索 ===")
    price_elements = soup.find_all(string=lambda text: text and "万円" in text)
    print(f"Found {len(price_elements)} elements containing '万円'")
    
    for i, price_elem in enumerate(price_elements[:5]):
        parent = price_elem.parent
        if parent:
            print(f"Price {i+1}: '{price_elem.strip()}' in <{parent.name}> {parent.get('class', [])}")
    
    # プリウス関連のテキストを検索
    print("\n=== プリウス関連テキストの検索 ===")
    prius_elements = soup.find_all(string=lambda text: text and ("プリウス" in text or "PRIUS" in text.upper()))
    print(f"Found {len(prius_elements)} elements containing 'プリウス' or 'PRIUS'")
    
    for i, prius_elem in enumerate(prius_elements[:5]):
        parent = prius_elem.parent
        if parent:
            print(f"Prius {i+1}: '{prius_elem.strip()}' in <{parent.name}> {parent.get('class', [])}")

if __name__ == "__main__":
    asyncio.run(analyze_page_structure())