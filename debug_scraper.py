import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

CHECK_URL = "https://toyota.jp/ucar/carlist/?padid=from_jpucar_header_search"

async def debug_page_structure():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)  # ブラウザを表示して確認
        page = await browser.new_page()
        await page.goto(CHECK_URL)
        await page.wait_for_timeout(5000)  # 5秒待機
        
        # ページの構造を確認
        html = await page.content()
        
        # スクリーンショットを撮って確認
        await page.screenshot(path="toyota_page.png")
        
        # フィルター関連の要素を探す
        filter_buttons = await page.query_selector_all("button")
        print(f"Found {len(filter_buttons)} buttons")
        
        for i, button in enumerate(filter_buttons[:10]):  # 最初の10個だけ表示
            text = await button.text_content()
            if text:
                print(f"Button {i}: {text.strip()}")
        
        # 入力フィールドを探す
        inputs = await page.query_selector_all("input, select")
        print(f"\nFound {len(inputs)} input/select elements")
        
        for i, input_elem in enumerate(inputs[:10]):  # 最初の10個だけ表示
            name = await input_elem.get_attribute("name")
            input_type = await input_elem.get_attribute("type")
            tag_name = await input_elem.evaluate("el => el.tagName")
            if name or input_type:
                print(f"Input {i}: tag={tag_name}, name={name}, type={input_type}")
        
        await browser.close()
    
    # HTMLファイルも保存して詳細確認
    with open("toyota_page.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("\nDebug files created:")
    print("- toyota_page.png (screenshot)")
    print("- toyota_page.html (full HTML)")

if __name__ == "__main__":
    asyncio.run(debug_page_structure())