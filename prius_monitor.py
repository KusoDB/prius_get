#!/usr/bin/env python3
"""
プリウス中古車監視システム
定期的にトヨタ認定中古車サイトをチェックし、新着車両を通知
"""

import os
import json
import asyncio
import hashlib
from datetime import datetime, timedelta
try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
from pathlib import Path
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests

load_dotenv()

# 設定
YEAR_FROM = "2019"
MAX_PRICE = "160"
DRIVE_TYPE = "2"  # 4WD/e-Four
CHECK_INTERVAL_MINUTES = 30  # 30分間隔でチェック

# ファイルパス
DATA_DIR = Path(__file__).parent / "data"
VEHICLES_DB = DATA_DIR / "vehicles.json"
LOG_FILE = DATA_DIR / "monitor.log"

# データディレクトリ作成
DATA_DIR.mkdir(exist_ok=True)

class PriusMonitor:
    def __init__(self):
        self.search_url = f"https://toyota.jp/ucar/carlist/?Tval=1&chk-detail-tvalue-sp-check=1&Cn=01_プリウス&Ymn={YEAR_FROM}&Drv={DRIVE_TYPE}&Pmx={MAX_PRICE}"
        self.known_vehicles = self.load_known_vehicles()
        
    def load_known_vehicles(self):
        """既知の車両リストを読み込み"""
        if VEHICLES_DB.exists():
            try:
                with open(VEHICLES_DB, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.log(f"車両データ読み込みエラー: {e}")
                return {}
        return {}
    
    def save_known_vehicles(self):
        """車両リストを保存"""
        try:
            with open(VEHICLES_DB, 'w', encoding='utf-8') as f:
                json.dump(self.known_vehicles, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"車両データ保存エラー: {e}")
    
    def log(self, message):
        """ログ出力"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_message + "\n")
        except Exception:
            pass
    
    def generate_vehicle_id(self, vehicle_info):
        """車両情報からユニークIDを生成"""
        return hashlib.md5(vehicle_info.encode('utf-8')).hexdigest()[:8]
    
    async def fetch_current_vehicles(self):
        """現在の車両リストを取得"""
        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto(self.search_url)
                await page.wait_for_timeout(5000)
                
                html = await page.content()
                await browser.close()
                
            return self.parse_vehicles(html)
            
        except Exception as e:
            self.log(f"車両取得エラー: {e}")
            return []
    
    def parse_vehicles(self, html):
        """HTMLから車両情報を解析"""
        soup = BeautifulSoup(html, "html.parser")
        vehicles = []
        
        car_names = soup.select("p.detais-name2")
        
        for name_elem in car_names:
            try:
                car_name = name_elem.get_text(strip=True)
                
                # プリウス以外はスキップ
                if "プリウス" not in car_name:
                    continue
                
                # 価格を探す
                parent = name_elem.parent
                price = "価格不明"
                while parent and parent.name != 'body':
                    price_elem = parent.select_one("p.car-price-sub")
                    if price_elem:
                        price = price_elem.get_text(strip=True)
                        break
                    parent = parent.parent
                
                # 年式を探す
                year = "年式不明"
                if parent:
                    year_elem = parent.select_one("p:contains('年'), span:contains('年')")
                    if year_elem:
                        year_text = year_elem.get_text()
                        if "年" in year_text:
                            year = year_text.strip()
                
                # 新着バッジチェック
                is_new = False
                if parent:
                    context = parent.get_text()
                    is_new = "NEW" in context or "新着" in context
                
                vehicle_info = {
                    "name": car_name,
                    "price": price,
                    "year": year,
                    "is_new": is_new,
                    "detected_at": datetime.now().isoformat(),
                    "url": self.search_url
                }
                
                vehicles.append(vehicle_info)
                
            except Exception as e:
                self.log(f"車両解析エラー: {e}")
                continue
        
        return vehicles
    
    def find_new_vehicles(self, current_vehicles):
        """新着車両を検出"""
        new_vehicles = []
        
        for vehicle in current_vehicles:
            vehicle_id = self.generate_vehicle_id(f"{vehicle['name']}_{vehicle['price']}")
            
            if vehicle_id not in self.known_vehicles:
                # 新しい車両を発見
                self.known_vehicles[vehicle_id] = vehicle
                new_vehicles.append(vehicle)
                self.log(f"新着車両発見: {vehicle['name']} - {vehicle['price']}")
        
        return new_vehicles
    
    def send_slack_notification(self, new_vehicles):
        """Slack通知"""
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not webhook_url:
            return False
        
        try:
            message_parts = ["🚗 **プリウス新着車両発見！**\n"]
            
            for vehicle in new_vehicles:
                new_badge = " 🆕" if vehicle.get('is_new') else ""
                message_parts.append(
                    f"• **{vehicle['name']}**{new_badge}\n"
                    f"  💰 {vehicle['price']}\n"
                    f"  📅 {vehicle['year']}\n"
                )
            
            message_parts.append(f"\n🔗 [検索結果を見る]({self.search_url})")
            message_parts.append(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            message = "".join(message_parts)
            
            response = requests.post(webhook_url, json={"text": message})
            return response.status_code == 200
            
        except Exception as e:
            self.log(f"Slack通知エラー: {e}")
            return False
    
    def send_email_notification(self, new_vehicles):
        """メール通知"""
        if not EMAIL_AVAILABLE:
            return False
            
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        email_user = os.getenv("EMAIL_USER")
        email_password = os.getenv("EMAIL_PASSWORD")
        to_email = os.getenv("TO_EMAIL")
        
        if not all([smtp_server, email_user, email_password, to_email]):
            return False
        
        try:
            msg = MimeMultipart()
            msg['From'] = email_user
            msg['To'] = to_email
            msg['Subject'] = f"プリウス新着車両 {len(new_vehicles)}台発見！"
            
            body_parts = ["プリウス新着車両が見つかりました！\n\n"]
            
            for vehicle in new_vehicles:
                new_badge = " [新着]" if vehicle.get('is_new') else ""
                body_parts.append(
                    f"車名: {vehicle['name']}{new_badge}\n"
                    f"価格: {vehicle['price']}\n"
                    f"年式: {vehicle['year']}\n"
                    f"検出日時: {vehicle['detected_at']}\n\n"
                )
            
            body_parts.append(f"検索結果URL: {self.search_url}\n")
            
            body = "".join(body_parts)
            msg.attach(MimeText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            self.log(f"メール通知エラー: {e}")
            return False
    
    def send_desktop_notification(self, new_vehicles):
        """デスクトップ通知（macOS）"""
        try:
            import subprocess
            
            title = f"プリウス新着 {len(new_vehicles)}台"
            message = f"{new_vehicles[0]['name']} - {new_vehicles[0]['price']}"
            if len(new_vehicles) > 1:
                message += f" 他{len(new_vehicles)-1}台"
            
            # macOSの通知
            subprocess.run([
                "osascript", "-e", 
                f'display notification "{message}" with title "{title}"'
            ], check=True)
            
            return True
            
        except Exception as e:
            self.log(f"デスクトップ通知エラー: {e}")
            return False
    
    async def check_for_new_vehicles(self):
        """新着車両をチェック"""
        self.log("車両チェック開始")
        
        current_vehicles = await self.fetch_current_vehicles()
        self.log(f"現在の該当車両数: {len(current_vehicles)}台")
        
        new_vehicles = self.find_new_vehicles(current_vehicles)
        
        if new_vehicles:
            self.log(f"新着車両 {len(new_vehicles)}台 を発見！")
            
            # 通知送信
            notifications_sent = []
            
            if self.send_slack_notification(new_vehicles):
                notifications_sent.append("Slack")
            
            if self.send_email_notification(new_vehicles):
                notifications_sent.append("Email")
            
            if self.send_desktop_notification(new_vehicles):
                notifications_sent.append("Desktop")
            
            if notifications_sent:
                self.log(f"通知送信完了: {', '.join(notifications_sent)}")
            else:
                self.log("通知送信失敗")
            
            # データ保存
            self.save_known_vehicles()
            
        else:
            self.log("新着車両なし")
        
        return len(new_vehicles)

    async def run_continuous_monitoring(self):
        """継続監視を実行"""
        self.log("プリウス監視システム開始")
        self.log(f"監視条件: {YEAR_FROM}年以降, 4WD/e-Four, {MAX_PRICE}万円以下")
        self.log(f"チェック間隔: {CHECK_INTERVAL_MINUTES}分")
        
        while True:
            try:
                await self.check_for_new_vehicles()
                
                # 次のチェックまで待機
                self.log(f"次回チェック: {CHECK_INTERVAL_MINUTES}分後")
                await asyncio.sleep(CHECK_INTERVAL_MINUTES * 60)
                
            except KeyboardInterrupt:
                self.log("監視システム停止")
                break
            except Exception as e:
                self.log(f"監視エラー: {e}")
                # エラー時は1分後に再試行
                await asyncio.sleep(60)

async def main():
    """メイン関数"""
    import sys
    
    monitor = PriusMonitor()
    
    # コマンドライン引数チェック
    if len(sys.argv) > 1 and sys.argv[1] == "--single-check":
        # 1回だけチェック（cron用）
        await monitor.check_for_new_vehicles()
    else:
        # 継続監視
        await monitor.run_continuous_monitoring()

if __name__ == "__main__":
    asyncio.run(main())