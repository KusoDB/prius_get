#!/usr/bin/env python3
"""
プリウス認定中古車の監視・通知システム
条件: 年式2019以降、e-Four、支払総額160万円以下
"""

import json
import os
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import schedule
import time
import logging

from toyota_used_car_search import ToyotaUsedCarSearch


class PriusMonitor:
    def __init__(self, config_file: str = 'prius_config.json'):
        self.config_file = config_file
        self.data_file = 'prius_data.json'
        self.config = self.load_config()
        self.searcher = ToyotaUsedCarSearch()
        
        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('prius_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self) -> Dict:
        """設定ファイルを読み込み"""
        default_config = {
            "search_conditions": {
                "car_name": "プリウス",
                "price_max": 160,
                "year_min": 2019,
                "drive_type": "e-Four",
                "certified_only": True
            },
            "notification": {
                "email_enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "",
                "sender_password": "",
                "recipient_email": "",
                "subject": "プリウス中古車情報更新"
            },
            "schedule": {
                "check_time": "09:00",
                "timezone": "Asia/Tokyo"
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # デフォルト設定をマージ
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
            except Exception as e:
                self.logger.error(f"設定ファイル読み込みエラー: {e}")
                return default_config
        else:
            # 初回実行時に設定ファイルを作成
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config: Dict):
        """設定ファイルを保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"設定ファイル保存エラー: {e}")
    
    def search_prius(self) -> List[Dict]:
        """プリウスを検索"""
        try:
            conditions = self.config['search_conditions']
            self.logger.info(f"プリウス検索開始: {conditions}")
            
            # 基本検索実行
            results = self.searcher.search_cars(
                price_max=conditions['price_max'],
                certified_only=conditions['certified_only']
            )
            
            # プリウスのみフィルタ
            prius_results = []
            for car in results:
                car_name = car.get('name', '').lower()
                if 'プリウス' in car_name or 'prius' in car_name:
                    # 年式フィルタ
                    year = car.get('year')
                    if year and int(year) >= conditions['year_min']:
                        # e-Fourフィルタ（車名にe-Fourが含まれるかチェック）
                        if conditions['drive_type'].lower() in car_name:
                            # 価格フィルタ（再確認）
                            price = car.get('price')
                            if price:
                                try:
                                    price_num = float(price.replace(',', ''))
                                    if price_num <= conditions['price_max']:
                                        prius_results.append(car)
                                except ValueError:
                                    continue
            
            self.logger.info(f"条件に合うプリウス: {len(prius_results)}件")
            return prius_results
            
        except Exception as e:
            self.logger.error(f"検索エラー: {e}")
            return []
    
    def load_previous_data(self) -> Dict:
        """前回の検索データを読み込み"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"データファイル読み込みエラー: {e}")
        return {"last_check": None, "cars": [], "car_hashes": []}
    
    def save_current_data(self, cars: List[Dict]):
        """現在の検索データを保存"""
        try:
            # 車両データのハッシュを生成（変更検知用）
            car_hashes = []
            for car in cars:
                car_str = json.dumps(car, sort_keys=True, ensure_ascii=False)
                car_hash = hashlib.md5(car_str.encode()).hexdigest()
                car_hashes.append(car_hash)
            
            data = {
                "last_check": datetime.now().isoformat(),
                "cars": cars,
                "car_hashes": car_hashes
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"データファイル保存エラー: {e}")
    
    def detect_changes(self, current_cars: List[Dict], previous_data: Dict) -> Dict:
        """変更を検知"""
        changes = {
            "new_cars": [],
            "removed_cars": [],
            "total_current": len(current_cars),
            "total_previous": len(previous_data.get('cars', []))
        }
        
        if not previous_data.get('cars'):
            # 初回実行
            changes["new_cars"] = current_cars
            return changes
        
        # 現在の車両ハッシュ
        current_hashes = []
        for car in current_cars:
            car_str = json.dumps(car, sort_keys=True, ensure_ascii=False)
            car_hash = hashlib.md5(car_str.encode()).hexdigest()
            current_hashes.append(car_hash)
        
        previous_hashes = previous_data.get('car_hashes', [])
        previous_cars = previous_data.get('cars', [])
        
        # 新規車両
        for i, hash_val in enumerate(current_hashes):
            if hash_val not in previous_hashes:
                changes["new_cars"].append(current_cars[i])
        
        # 削除された車両
        for i, hash_val in enumerate(previous_hashes):
            if hash_val not in current_hashes and i < len(previous_cars):
                changes["removed_cars"].append(previous_cars[i])
        
        return changes
    
    def send_notification(self, changes: Dict):
        """メール通知を送信"""
        if not self.config['notification']['email_enabled']:
            return
        
        if not changes["new_cars"] and not changes["removed_cars"]:
            self.logger.info("変更なし - 通知をスキップ")
            return
        
        try:
            # メール本文作成
            subject = self.config['notification']['subject']
            body = self.create_email_body(changes)
            
            # メール送信
            msg = MIMEMultipart()
            msg['From'] = self.config['notification']['sender_email']
            msg['To'] = self.config['notification']['recipient_email']
            msg['Subject'] = f"{subject} - {datetime.now().strftime('%Y/%m/%d')}"
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(
                self.config['notification']['smtp_server'],
                self.config['notification']['smtp_port']
            )
            server.starttls()
            server.login(
                self.config['notification']['sender_email'],
                self.config['notification']['sender_password']
            )
            
            text = msg.as_string()
            server.sendmail(
                self.config['notification']['sender_email'],
                self.config['notification']['recipient_email'],
                text
            )
            server.quit()
            
            self.logger.info("通知メール送信完了")
            
        except Exception as e:
            self.logger.error(f"メール送信エラー: {e}")
    
    def create_email_body(self, changes: Dict) -> str:
        """メール本文を作成"""
        body = f"プリウス中古車情報更新 - {datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n\n"
        
        body += f"検索条件:\n"
        body += f"- 車種: {self.config['search_conditions']['car_name']}\n"
        body += f"- 年式: {self.config['search_conditions']['year_min']}年以降\n"
        body += f"- 駆動方式: {self.config['search_conditions']['drive_type']}\n"
        body += f"- 支払総額: {self.config['search_conditions']['price_max']}万円以下\n\n"
        
        body += f"現在の該当車両数: {changes['total_current']}件\n"
        body += f"前回チェック時: {changes['total_previous']}件\n\n"
        
        if changes["new_cars"]:
            body += f"【新規追加車両: {len(changes['new_cars'])}件】\n"
            body += "-" * 50 + "\n"
            for i, car in enumerate(changes["new_cars"], 1):
                body += f"{i}. {car.get('name', 'N/A')}\n"
                body += f"   価格: {car.get('price', 'N/A')}万円\n"
                body += f"   年式: {car.get('year', 'N/A')}\n"
                body += f"   走行距離: {car.get('mileage', 'N/A')}km\n"
                body += f"   販売店: {car.get('dealer', 'N/A')}\n"
                body += f"   URL: {car.get('url', 'N/A')}\n\n"
        
        if changes["removed_cars"]:
            body += f"【削除された車両: {len(changes['removed_cars'])}件】\n"
            body += "-" * 50 + "\n"
            for i, car in enumerate(changes["removed_cars"], 1):
                body += f"{i}. {car.get('name', 'N/A')} - {car.get('price', 'N/A')}万円\n"
        
        body += "\n" + "=" * 60 + "\n"
        body += "※このメールは自動送信です。"
        
        return body
    
    def run_check(self):
        """チェック実行"""
        self.logger.info("プリウス監視チェック開始")
        
        try:
            # 現在の検索結果を取得
            current_cars = self.search_prius()
            
            # 前回のデータと比較
            previous_data = self.load_previous_data()
            changes = self.detect_changes(current_cars, previous_data)
            
            # 結果をログ出力
            self.logger.info(f"新規: {len(changes['new_cars'])}件, 削除: {len(changes['removed_cars'])}件")
            
            # 通知送信
            self.send_notification(changes)
            
            # データ保存
            self.save_current_data(current_cars)
            
            self.logger.info("プリウス監視チェック完了")
            
        except Exception as e:
            self.logger.error(f"チェック実行エラー: {e}")
    
    def setup_schedule(self):
        """スケジュール設定"""
        check_time = self.config['schedule']['check_time']
        schedule.every().day.at(check_time).do(self.run_check)
        self.logger.info(f"スケジュール設定完了: 毎日 {check_time}")
    
    def run_daemon(self):
        """デーモンとして実行"""
        self.setup_schedule()
        self.logger.info("デーモン開始")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1分間隔でチェック


def main():
    """メイン関数"""
    import sys
    
    monitor = PriusMonitor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "check":
            # 即座にチェック実行
            monitor.run_check()
        elif command == "daemon":
            # デーモンとして実行
            monitor.run_daemon()
        elif command == "config":
            # 設定ファイルのパスを表示
            print(f"設定ファイル: {monitor.config_file}")
            print("設定を編集して再実行してください。")
        else:
            print("使用方法:")
            print("  python prius_monitor.py check   # 即座にチェック")
            print("  python prius_monitor.py daemon  # デーモンとして実行")
            print("  python prius_monitor.py config  # 設定ファイル確認")
    else:
        # デフォルトは即座にチェック
        monitor.run_check()


if __name__ == "__main__":
    main()