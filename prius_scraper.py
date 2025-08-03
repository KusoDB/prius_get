import os
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()  # .env に SLACK_WEBHOOK_URL などを設定しておく

CHECK_URL = "https://toyota.jp/ucar/carlist/?padid=from_jpucar_header_search"
YEAR_FROM = "2019"
DRIVE_TYPE_VALUE = "4WD"   # e-Four は 4WD の中に含まれるケースが多い
MAX_PRICE = "160"          # 単位：万円

async def fetch_listings():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        
        # 正しいパラメータでプリウス検索
        prius_url = f"https://toyota.jp/ucar/carlist/?Tval=1&chk-detail-tvalue-sp-check=1&Cn=01_プリウス&Ymn={YEAR_FROM}&Drv=2&Pmx={MAX_PRICE}"
        print(f"検索条件: プリウス, {YEAR_FROM}年以降, 4WD/e-Four, {MAX_PRICE}万円以下")
        print(f"アクセスURL: {prius_url}")
        await page.goto(prius_url)
        await page.wait_for_timeout(5000)  # サイト読み込み待機
        
        print("プリウス専用ページにアクセス中...")
        
        html = await page.content()
        await browser.close()
    return html

def parse_new_listings(html):
    soup = BeautifulSoup(html, "html.parser")
    cars = []
    
    print("プリウス車両情報を解析中...")
    
    # 実際の構造に基づいて、車名と価格を直接取得
    car_names = soup.select("p.detais-name2")  # プリウス車名
    car_prices = soup.select("p.car-price-sub")  # 価格情報
    
    print(f"車名要素: {len(car_names)}件, 価格要素: {len(car_prices)}件")
    
    # 新着バッジを探す
    new_badges = soup.find_all(string=lambda text: text and ("新着" in text or "NEW" in text.upper()))
    
    # 車名から車両情報をペアにする
    processed_cars = set()  # 重複を避ける
    
    for name_elem in car_names:
        try:
            car_name = name_elem.get_text(strip=True)
            
            # 同じ親要素または近くの要素から価格を探す
            price = "価格不明"
            
            # 親要素から価格を探す
            parent = name_elem.parent
            while parent and parent.name != 'body':
                price_elem = parent.select_one("p.car-price-sub")
                if price_elem:
                    price = price_elem.get_text(strip=True)
                    break
                parent = parent.parent
            
            # 新着チェック（名前の近くに新着バッジがあるか）
            is_new = False
            context = name_elem.parent.get_text() if name_elem.parent else ""
            is_new = "新着" in context or "NEW" in context.upper()
            
            # プリウスが含まれている場合のみ追加
            if "プリウス" in car_name or "PRIUS" in car_name.upper():
                car_info = f"{car_name} — {price}" + (" [新着]" if is_new else "")
                if car_info not in processed_cars:
                    processed_cars.add(car_info)
                    cars.append(car_info)
                    print(f"追加: {car_info}")
                
        except Exception as e:
            print(f"車両解析エラー: {e}")
            continue
    
    # 価格で160万円以下のものだけフィルタリング
    if cars:
        filtered_cars = []
        for car in cars:
            try:
                # 価格から数値を抽出
                import re
                price_match = re.search(r'(\d+(?:\.\d+)?)万円', car)
                if price_match:
                    price_value = float(price_match.group(1))
                    if price_value <= float(MAX_PRICE):
                        filtered_cars.append(car)
                else:
                    filtered_cars.append(car)  # 価格不明の場合も含める
            except:
                filtered_cars.append(car)  # エラーの場合も含める
        
        cars = filtered_cars
    
    return cars

async def main():
    html = await fetch_listings()
    all_cars = parse_new_listings(html)

    if not all_cars:
        print("条件に合うプリウスが見つかりませんでした")
        return

    print(f"\n=== 検索結果 ===")
    print(f"条件: プリウス、{MAX_PRICE}万円以下")
    print(f"該当車両: {len(all_cars)}台\n")
    
    for car in all_cars:
        print(f"• {car}")

    # 新着のみ抽出
    new_cars = [car for car in all_cars if "[新着]" in car]
    
    if new_cars:
        body = f"プリウス新着候補 ({len(new_cars)}台):\n" + "\n".join(new_cars)
        print(f"\n{body}")

        # ── Slack 通知 ──
        import requests
        webhook = os.getenv("SLACK_WEBHOOK_URL")
        if webhook:
            try:
                response = requests.post(webhook, json={"text": body})
                if response.status_code == 200:
                    print("Slack通知を送信しました")
                else:
                    print(f"Slack通知エラー: {response.status_code}")
            except Exception as e:
                print(f"Slack通知送信失敗: {e}")
        else:
            print("Slack Webhook URLが設定されていません")
    else:
        print("新着車両はありませんでした")

if __name__ == "__main__":
    asyncio.run(main())