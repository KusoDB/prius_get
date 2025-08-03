#!/usr/bin/env python3
"""
クラウド環境向けプリウス監視システム
GitHub Actions等のサーバーレス環境で動作
"""

import os
import json
import asyncio
import hashlib
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests

# 環境変数読み込み
load_dotenv()

# 設定
YEAR_FROM = "2019"
MAX_PRICE = "160"
DRIVE_TYPE = "2"  # 4WD/e-Four

# ファイルパス（クラウド環境対応）
DATA_DIR = Path("data")
VEHICLES_DB = DATA_DIR / "vehicles.json"
LOG_FILE = DATA_DIR / "monitor.log"

# データディレクトリ作成
DATA_DIR.mkdir(exist_ok=True)

class CloudPriusMonitor:
    def __init__(self):
        self.search_url = f"https://toyota.jp/ucar/carlist/?Tval=1&chk-detail-tvalue-sp-check=1&Cn=01_プリウス&Ymn={YEAR_FROM}&Drv={DRIVE_TYPE}&Pmx={MAX_PRICE}"
        self.known_vehicles = self.load_known_vehicles()
        
    def load_known_vehicles(self):
        """既知の車両リストを読み込み"""
        # まずバックアップファイルをチェック
        backup_file = Path("vehicles_backup.json")
        if backup_file.exists():
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.log(f"バックアップから{len(data)}台の車両データを復元")
                    return data
            except Exception as e:
                self.log(f"バックアップ読み込みエラー: {e}")
        
        # 通常のファイルをチェック
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
        """ログ出力（コンソール＋ファイル）"""
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
                # クラウド環境向けブラウザ設定
                browser = await pw.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding'
                    ]
                )
                
                page = await browser.new_page()
                
                # User-Agentを設定（検出回避）
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                
                self.log(f"アクセス中: {self.search_url}")
                await page.goto(self.search_url)
                await page.wait_for_timeout(8000)  # クラウド環境では長めに待機
                
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
        self.log(f"検出された車名要素: {len(car_names)}個")
        
        for name_elem in car_names:
            try:
                car_name = name_elem.get_text(strip=True)
                
                # プリウス以外はスキップ
                if "プリウス" not in car_name:
                    continue
                
                # 価格を探す
                parent = name_elem.parent
                price = "価格不明"
                attempts = 0
                while parent and parent.name != 'body' and attempts < 10:
                    price_elem = parent.select_one("p.car-price-sub")
                    if price_elem:
                        price = price_elem.get_text(strip=True)
                        break
                    parent = parent.parent
                    attempts += 1
                
                # 新着バッジチェック
                is_new = False
                if parent:
                    context = parent.get_text()
                    is_new = "NEW" in context or "新着" in context
                
                vehicle_info = {
                    "name": car_name,
                    "price": price,
                    "is_new": is_new,
                    "detected_at": datetime.now().isoformat(),
                    "search_url": self.search_url
                }
                
                vehicles.append(vehicle_info)
                
            except Exception as e:
                self.log(f"車両解析エラー: {e}")
                continue
        
        self.log(f"プリウス車両数: {len(vehicles)}台")
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
                self.log(f"🆕 新着車両発見: {vehicle['name']} - {vehicle['price']}")
        
        return new_vehicles
    
    def send_slack_notification(self, new_vehicles, is_status=False):
        """Slack通知"""
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not webhook_url:
            return False
        
        try:
            if is_status:
                # ステータス通知
                message = f"🤖 プリウス監視システム実行完了\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC)\n📊 監視中の車両: {len(self.known_vehicles)}台"
            else:
                # 新着通知
                message_parts = ["🚗 **プリウス新着車両発見！**\n"]
                
                for vehicle in new_vehicles:
                    new_badge = " 🆕" if vehicle.get('is_new') else ""
                    message_parts.append(
                        f"• **{vehicle['name']}**{new_badge}\n"
                        f"  💰 {vehicle['price']}\n"
                    )
                
                message_parts.append(f"\n🔗 [検索結果を見る]({self.search_url})")
                message_parts.append(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC)")
                message = "".join(message_parts)
            
            response = requests.post(webhook_url, json={"text": message}, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            self.log(f"Slack通知エラー: {e}")
            return False
    
    async def run_single_check(self):
        """1回だけのチェック実行（クラウド環境用）"""
        self.log("=== プリウス監視システム開始 ===")
        self.log(f"監視条件: {YEAR_FROM}年以降, 4WD/e-Four, {MAX_PRICE}万円以下")
        
        # 現在の車両を取得
        current_vehicles = await self.fetch_current_vehicles()
        self.log(f"現在の該当車両数: {len(current_vehicles)}台")
        
        if not current_vehicles:
            self.log("⚠️ 車両が検出されませんでした。サイトの構造変更の可能性があります。")
            return
        
        # 新着車両をチェック
        new_vehicles = self.find_new_vehicles(current_vehicles)
        
        if new_vehicles:
            self.log(f"🎉 新着車両 {len(new_vehicles)}台 を発見！")
            
            # 新着通知を送信
            if self.send_slack_notification(new_vehicles):
                self.log("✅ Slack新着通知送信完了")
            else:
                self.log("❌ Slack新着通知送信失敗")
            
            # データ保存
            self.save_known_vehicles()
            
        else:
            self.log("📭 新着車両なし")
        
        # 現在の車両一覧をログ出力
        self.log("📋 現在監視中の車両:")
        for i, vehicle in enumerate(current_vehicles[:5], 1):  # 最大5台まで表示
            self.log(f"  {i}. {vehicle['name']} - {vehicle['price']}")
        
        if len(current_vehicles) > 5:
            self.log(f"  ... 他{len(current_vehicles)-5}台")
        
        # 週1回のサマリー通知（日曜日の18時のみ）
        current_time = datetime.now()
        if current_time.weekday() == 6 and current_time.hour == 9:  # 日曜日の18時（JST）
            summary_message = f"📊 週間サマリー\n監視中のプリウス: {len(self.known_vehicles)}台\n今週の新着: 0台（新着があった場合は個別通知済み）"
            if self.send_slack_notification([], is_status=True):
                self.log("✅ 週間サマリー送信完了")
        
        self.log("=== プリウス監視システム完了 ===")
        return len(new_vehicles)

async def main():
    """メイン関数"""
    monitor = CloudPriusMonitor()
    await monitor.run_single_check()

if __name__ == "__main__":
    asyncio.run(main())