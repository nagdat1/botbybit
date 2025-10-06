"""
💾 قاعدة البيانات - Database Management
إدارة بيانات المستخدمين والصفقات والإشارات
"""
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any
from config import DATABASE_PATH, DEMO_INITIAL_BALANCE, DEMO_CURRENCY


class Database:
    """إدارة قاعدة البيانات"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def get_connection(self):
        """إنشاء اتصال بقاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """إنشاء جداول قاعدة البيانات"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                mode TEXT DEFAULT 'demo',
                demo_balance REAL DEFAULT {DEMO_INITIAL_BALANCE},
                activated_nagdat INTEGER DEFAULT 0,
                webhook_url TEXT UNIQUE,
                webhook_token TEXT UNIQUE,
                api_key TEXT,
                api_secret TEXT,
                api_passphrase TEXT,
                leverage INTEGER DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول الصفقات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                trade_id TEXT PRIMARY KEY,
                user_id INTEGER,
                symbol TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                side TEXT NOT NULL,
                leverage INTEGER DEFAULT 1,
                entry_price REAL NOT NULL,
                current_price REAL,
                quantity REAL NOT NULL,
                stop_loss REAL,
                take_profit REAL,
                trailing_stop REAL,
                trailing_stop_percent REAL,
                status TEXT DEFAULT 'open',
                profit_loss REAL DEFAULT 0,
                profit_loss_percent REAL DEFAULT 0,
                mode TEXT DEFAULT 'demo',
                opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                bybit_order_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # جدول الإشارات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                signal_id TEXT PRIMARY KEY,
                sender_id INTEGER,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                leverage INTEGER DEFAULT 1,
                stop_loss REAL,
                take_profit REAL,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                executed_count INTEGER DEFAULT 0
            )
        """)
        
        # جدول المشتركين في إشارات Nagdat
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nagdat_subscribers (
                user_id INTEGER PRIMARY KEY,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                signals_received INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # جدول الإحصائيات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_profit REAL DEFAULT 0,
                total_loss REAL DEFAULT 0,
                best_trade REAL DEFAULT 0,
                worst_trade REAL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    # ==================== المستخدمين ====================
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """الحصول على بيانات المستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def create_user(self, user_id: int, username: str = None, 
                   first_name: str = None, last_name: str = None) -> Dict:
        """إنشاء مستخدم جديد"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # إنشاء webhook فريد
        webhook_token = str(uuid.uuid4())
        webhook_url = f"/webhook/user/{webhook_token}"
        
        cursor.execute("""
            INSERT INTO users (user_id, username, first_name, last_name, 
                             webhook_url, webhook_token)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, username, first_name, last_name, webhook_url, webhook_token))
        
        # إنشاء إحصائيات المستخدم
        cursor.execute("""
            INSERT INTO statistics (user_id) VALUES (?)
        """, (user_id,))
        
        conn.commit()
        conn.close()
        return self.get_user(user_id)
    
    def update_user_mode(self, user_id: int, mode: str):
        """تحديث نوع الحساب"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET mode = ?, last_active = CURRENT_TIMESTAMP 
            WHERE user_id = ?
        """, (mode, user_id))
        conn.commit()
        conn.close()
    
    def update_user_api(self, user_id: int, api_key: str, 
                       api_secret: str, api_passphrase: str = None):
        """تحديث بيانات API"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET api_key = ?, api_secret = ?, api_passphrase = ?,
                           last_active = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (api_key, api_secret, api_passphrase, user_id))
        conn.commit()
        conn.close()
    
    def update_demo_balance(self, user_id: int, balance: float):
        """تحديث رصيد الحساب التجريبي"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET demo_balance = ?, last_active = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (balance, user_id))
        conn.commit()
        conn.close()
    
    def set_leverage(self, user_id: int, leverage: int):
        """تعيين الرافعة المالية"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET leverage = ?, last_active = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (leverage, user_id))
        conn.commit()
        conn.close()
    
    # ==================== الصفقات ====================
    
    def create_trade(self, user_id: int, symbol: str, trade_type: str,
                    side: str, entry_price: float, quantity: float,
                    leverage: int = 1, stop_loss: float = None,
                    take_profit: float = None, trailing_stop_percent: float = None,
                    mode: str = 'demo', bybit_order_id: str = None) -> str:
        """إنشاء صفقة جديدة"""
        trade_id = str(uuid.uuid4())
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO trades (trade_id, user_id, symbol, trade_type, side,
                              leverage, entry_price, current_price, quantity,
                              stop_loss, take_profit, trailing_stop_percent,
                              mode, bybit_order_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (trade_id, user_id, symbol, trade_type, side, leverage,
              entry_price, entry_price, quantity, stop_loss, take_profit,
              trailing_stop_percent, mode, bybit_order_id))
        
        conn.commit()
        conn.close()
        return trade_id
    
    def get_open_trades(self, user_id: int) -> List[Dict]:
        """الحصول على الصفقات المفتوحة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM trades 
            WHERE user_id = ? AND status = 'open'
            ORDER BY opened_at DESC
        """, (user_id,))
        trades = cursor.fetchall()
        conn.close()
        return [dict(trade) for trade in trades]
    
    def get_trade(self, trade_id: str) -> Optional[Dict]:
        """الحصول على صفقة محددة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades WHERE trade_id = ?", (trade_id,))
        trade = cursor.fetchone()
        conn.close()
        return dict(trade) if trade else None
    
    def update_trade_price(self, trade_id: str, current_price: float, 
                          profit_loss: float, profit_loss_percent: float):
        """تحديث سعر وربح/خسارة الصفقة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE trades 
            SET current_price = ?, profit_loss = ?, profit_loss_percent = ?
            WHERE trade_id = ?
        """, (current_price, profit_loss, profit_loss_percent, trade_id))
        conn.commit()
        conn.close()
    
    def close_trade(self, trade_id: str, close_price: float, 
                   profit_loss: float, profit_loss_percent: float,
                   partial_percent: float = 100):
        """إغلاق صفقة (كلي أو جزئي)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if partial_percent >= 100:
            # إغلاق كامل
            cursor.execute("""
                UPDATE trades 
                SET status = 'closed', current_price = ?, profit_loss = ?,
                    profit_loss_percent = ?, closed_at = CURRENT_TIMESTAMP
                WHERE trade_id = ?
            """, (close_price, profit_loss, profit_loss_percent, trade_id))
        else:
            # إغلاق جزئي - تحديث الكمية
            trade = self.get_trade(trade_id)
            new_quantity = trade['quantity'] * (1 - partial_percent / 100)
            cursor.execute("""
                UPDATE trades 
                SET quantity = ?, profit_loss = profit_loss + ?
                WHERE trade_id = ?
            """, (new_quantity, profit_loss, trade_id))
        
        conn.commit()
        conn.close()
    
    def update_trailing_stop(self, trade_id: str, new_trailing_stop: float):
        """تحديث الإيقاف المتحرك"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE trades SET trailing_stop = ? WHERE trade_id = ?
        """, (new_trailing_stop, trade_id))
        conn.commit()
        conn.close()
    
    # ==================== الإشارات ====================
    
    def create_signal(self, sender_id: int, symbol: str, action: str,
                     leverage: int = 1, stop_loss: float = None,
                     take_profit: float = None, message: str = None) -> str:
        """إنشاء إشارة جديدة"""
        signal_id = str(uuid.uuid4())
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO signals (signal_id, sender_id, symbol, action,
                               leverage, stop_loss, take_profit, message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (signal_id, sender_id, symbol, action, leverage,
              stop_loss, take_profit, message))
        
        conn.commit()
        conn.close()
        return signal_id
    
    def increment_signal_execution(self, signal_id: str):
        """زيادة عداد تنفيذ الإشارة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE signals 
            SET executed_count = executed_count + 1 
            WHERE signal_id = ?
        """, (signal_id,))
        conn.commit()
        conn.close()
    
    # ==================== مشتركي Nagdat ====================
    
    def subscribe_to_nagdat(self, user_id: int):
        """الاشتراك في إشارات Nagdat"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # تحديث جدول المستخدمين
        cursor.execute("""
            UPDATE users SET activated_nagdat = 1 WHERE user_id = ?
        """, (user_id,))
        
        # إضافة للمشتركين
        cursor.execute("""
            INSERT OR IGNORE INTO nagdat_subscribers (user_id) VALUES (?)
        """, (user_id,))
        
        conn.commit()
        conn.close()
    
    def unsubscribe_from_nagdat(self, user_id: int):
        """إلغاء الاشتراك من إشارات Nagdat"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET activated_nagdat = 0 WHERE user_id = ?
        """, (user_id,))
        
        cursor.execute("""
            DELETE FROM nagdat_subscribers WHERE user_id = ?
        """, (user_id,))
        
        conn.commit()
        conn.close()
    
    def get_nagdat_subscribers(self) -> List[int]:
        """الحصول على قائمة المشتركين في إشارات Nagdat"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM nagdat_subscribers")
        subscribers = cursor.fetchall()
        conn.close()
        return [sub['user_id'] for sub in subscribers]
    
    def increment_subscriber_signals(self, user_id: int):
        """زيادة عداد الإشارات المستلمة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE nagdat_subscribers 
            SET signals_received = signals_received + 1 
            WHERE user_id = ?
        """, (user_id,))
        conn.commit()
        conn.close()
    
    # ==================== الإحصائيات ====================
    
    def update_statistics(self, user_id: int, trade_profit: float):
        """تحديث إحصائيات المستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if trade_profit > 0:
            cursor.execute("""
                UPDATE statistics 
                SET total_trades = total_trades + 1,
                    winning_trades = winning_trades + 1,
                    total_profit = total_profit + ?,
                    best_trade = MAX(best_trade, ?),
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (trade_profit, trade_profit, user_id))
        else:
            cursor.execute("""
                UPDATE statistics 
                SET total_trades = total_trades + 1,
                    losing_trades = losing_trades + 1,
                    total_loss = total_loss + ?,
                    worst_trade = MIN(worst_trade, ?),
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (abs(trade_profit), trade_profit, user_id))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self, user_id: int) -> Optional[Dict]:
        """الحصول على إحصائيات المستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM statistics WHERE user_id = ?", (user_id,))
        stats = cursor.fetchone()
        conn.close()
        return dict(stats) if stats else None
    
    # ==================== المطور ====================
    
    def get_all_users_count(self) -> int:
        """عدد المستخدمين الكلي"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users")
        count = cursor.fetchone()['count']
        conn.close()
        return count
    
    def get_active_users_count(self) -> int:
        """عدد المستخدمين النشطين"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as count FROM users 
            WHERE last_active >= datetime('now', '-7 days')
        """)
        count = cursor.fetchone()['count']
        conn.close()
        return count
    
    def get_total_signals_sent(self) -> int:
        """عدد الإشارات المرسلة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM signals")
        count = cursor.fetchone()['count']
        conn.close()
        return count


# إنشاء instance عام
db = Database()
