import asyncio
from playwright.async_api import async_playwright

CHECK_URL = "https://toyota.jp/ucar/carlist/?padid=from_jpucar_header_search"

async def debug_site_structure():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(CHECK_URL)
        await page.wait_for_timeout(10000)  # 10秒待ってサイトの構造を確認
        
        # 条件指定関連のボタンを探す
        print("Looking for condition/filter buttons...")
        buttons = await page.query_selector_all("button, a")
        for i, button in enumerate(buttons):
            text = await button.text_content()
            if text and any(keyword in text for keyword in ["条件", "フィルター", "絞り込み", "詳細"]):
                print(f"Button {i}: '{text.strip()}'")
                classes = await button.get_attribute("class")
                print(f"  Classes: {classes}")
        
        # 年式、駆動方式、価格に関連する要素を探す
        print("\nLooking for year, drive type, price elements...")
        all_elements = await page.query_selector_all("*")
        for elem in all_elements:
            text_content = await elem.text_content()
            if text_content and any(keyword in text_content for keyword in ["年式", "駆動", "価格", "万円"]):
                tag_name = await elem.evaluate("el => el.tagName")
                if len(text_content.strip()) < 50:  # 短いテキストのみ表示
                    print(f"{tag_name}: '{text_content.strip()}'")
        
        input("Press Enter to close browser...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_site_structure())