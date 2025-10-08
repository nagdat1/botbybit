#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
قاعدة بيانات SQLite لإدارة المستخدمين والصفقات في البوت متعدد المستخدمين
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    """مدير قاعدة البيانات للمستخدمين والصفقات"""
    
    def __init__(self, db_path: str = "trading_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """تهيئة قاعدة البيانات وإنشاء الجداول"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # جدول المستخدمين
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        api_key TEXT,
                        api_secret TEXT,
                        balance REAL DEFAULT 10000.0,
                        partial_percents TEXT DEFAULT '[25, 50, 25]',
                        tps_percents TEXT DEFAULT '[1.5, 3.0, 5.0]',
                        is_active BOOLEAN DEFAULT 1,
                        notifications BOOLEAN DEFAULT 1,
                        preferred_symbols TEXT DEFAULT '["BTCUSDT", "ETHUSDT"]',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # جدول الصفقات
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS orders (
                        order_id TEXT PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        symbol TEXT NOT NULL,
                        side TEXT NOT NULL,
                        entry_price REAL NOT NULL,
                        quantity REAL NOT NULL,
                        open_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        close_time TIMESTAMP,
                        tps TEXT DEFAULT '[]',
                        sl REAL DEFAULT 0.0,
                        partial_close TEXT DEFAULT '[]',
                        status TEXT DEFAULT 'OPEN',
                        notes TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                # جدول إعدادات المستخدم
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_settings (
                        user_id INTEGER PRIMARY KEY,
                        market_type TEXT DEFAULT 'spot',
                        trade_amount REAL DEFAULT 100.0,
                        leverage INTEGER DEFAULT 10,
                        account_type TEXT DEFAULT 'demo',
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                # جدول المطورين
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS developers (
                        developer_id INTEGER PRIMARY KEY,
                        developer_name TEXT NOT NULL,
                        developer_key TEXT UNIQUE,
                        webhook_url TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        can_broadcast BOOLEAN DEFAULT 1,
                        auto_broadcast BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # إضافة حقل auto_broadcast إذا لم يكن موجوداً
                try:
                    cursor.execute("ALTER TABLE developers ADD COLUMN auto_broadcast BOOLEAN DEFAULT 0")
                except sqlite3.OperationalError:
                    pass  # الحقل موجود بالفعل
                
                # جدول متابعي المطورين
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS developer_followers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        developer_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        followed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (developer_id) REFERENCES developers (developer_id),
                        FOREIGN KEY (user_id) REFERENCES users (user_id),
                        UNIQUE(developer_id, user_id)
                    )
                """)
                
                # جدول إشارات المطورين
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS developer_signals (
                        signal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        developer_id INTEGER NOT NULL,
                        signal_data TEXT NOT NULL,
                        target_followers TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (developer_id) REFERENCES developers (developer_id)
                    )
                """)
                
                # جدول تسجيل الصفقات المفصل (Trade Log)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trade_logs (
                        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        symbol TEXT NOT NULL,
                        action TEXT NOT NULL,
                        price REAL NOT NULL,
                        account_type TEXT NOT NULL,
                        market_type TEXT NOT NULL,
                        trade_amount REAL NOT NULL,
                        leverage INTEGER NOT NULL,
                        source TEXT NOT NULL,
                        status TEXT DEFAULT 'executed',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                conn.commit()
                logger.info("✅ تم تهيئة قاعدة البيانات بنجاح")
                
        except Exception as e:
            logger.error(f"خطأ في تهيئة قاعدة البيانات: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """الحصول على اتصال قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # للحصول على نتائج كـ dict
        try:
            yield conn
        finally:
            conn.close()
    
    # إدارة المستخدمين
    def create_user(self, user_id: int, api_key: str = None, api_secret: str = None) -> bool:
        """إنشاء مستخدم جديد"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # التحقق من وجود المستخدم
                cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
                if cursor.fetchone():
                    return False  # المستخدم موجود بالفعل
                
                # إنشاء المستخدم الجديد
                cursor.execute("""
                    INSERT INTO users (user_id, api_key, api_secret)
                    VALUES (?, ?, ?)
                """, (user_id, api_key, api_secret))
                
                # إنشاء إعدادات افتراضية للمستخدم
                cursor.execute("""
                    INSERT INTO user_settings (user_id)
                    VALUES (?)
                """, (user_id,))
                
                conn.commit()
                logger.info(f"تم إنشاء مستخدم جديد: {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"خطأ في إنشاء المستخدم {user_id}: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """الحصول على بيانات المستخدم"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT u.*, s.* FROM users u
                    LEFT JOIN user_settings s ON u.user_id = s.user_id
                    WHERE u.user_id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                if row:
                    user_data = dict(row)
                    
                    # تحويل النصوص JSON إلى قوائم
                    try:
                        user_data['partial_percents'] = json.loads(user_data['partial_percents'])
                        user_data['tps_percents'] = json.loads(user_data['tps_percents'])
                        user_data['preferred_symbols'] = json.loads(user_data['preferred_symbols'])
                    except (json.JSONDecodeError, TypeError):
                        user_data['partial_percents'] = [25, 50, 25]
                        user_data['tps_percents'] = [1.5, 3.0, 5.0]
                        user_data['preferred_symbols'] = ["BTCUSDT", "ETHUSDT"]
                    
                    return user_data
                return None
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على المستخدم {user_id}: {e}")
            return None
    
    def update_user_api(self, user_id: int, api_key: str, api_secret: str) -> bool:
        """تحديث API keys للمستخدم"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE users 
                    SET api_key = ?, api_secret = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (api_key, api_secret, user_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"خطأ في تحديث API للمستخدم {user_id}: {e}")
            return False
    
    def update_user_balance(self, user_id: int, balance: float) -> bool:
        """تحديث رصيد المستخدم"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE users 
                    SET balance = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (balance, user_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"خطأ في تحديث الرصيد للمستخدم {user_id}: {e}")
            return False
    
    def toggle_user_active(self, user_id: int) -> bool:
        """تبديل حالة تشغيل/إيقاف المستخدم"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # الحصول على الحالة الحالية
                cursor.execute("SELECT is_active FROM users WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                if not row:
                    return False
                
                current_status = row['is_active']
                new_status = not bool(current_status)
                
                cursor.execute("""
                    UPDATE users 
                    SET is_active = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (new_status, user_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"خطأ في تبديل حالة المستخدم {user_id}: {e}")
            return False
    
    def update_user_settings(self, user_id: int, settings: Dict) -> bool:
        """تحديث إعدادات المستخدم - نظام ذكي يحدث فقط القيم المطلوبة"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 🔥 الحصول على الإعدادات الحالية أولاً
                cursor.execute("""
                    SELECT market_type, trade_amount, leverage, account_type
                    FROM user_settings
                    WHERE user_id = ?
                """, (user_id,))
                
                current = cursor.fetchone()
                if current:
                    # دمج الإعدادات الحالية مع الجديدة
                    market_type = settings.get('market_type', current['market_type'])
                    trade_amount = settings.get('trade_amount', current['trade_amount'])
                    leverage = settings.get('leverage', current['leverage'])
                    account_type = settings.get('account_type', current['account_type'])
                    
                    # تحديث إعدادات التداول
                    cursor.execute("""
                        UPDATE user_settings 
                        SET market_type = ?, trade_amount = ?, leverage = ?, account_type = ?
                        WHERE user_id = ?
                    """, (market_type, trade_amount, leverage, account_type, user_id))
                    
                    logger.info(f"✅ تم تحديث user_settings في DB: market_type={market_type}")
                else:
                    # إنشاء سجل جديد إذا لم يكن موجوداً
                    market_type = settings.get('market_type', 'spot')
                    trade_amount = settings.get('trade_amount', 100.0)
                    leverage = settings.get('leverage', 10)
                    account_type = settings.get('account_type', 'demo')
                    
                    cursor.execute("""
                        INSERT INTO user_settings (user_id, market_type, trade_amount, leverage, account_type)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user_id, market_type, trade_amount, leverage, account_type))
                    
                    logger.info(f"✅ تم إنشاء user_settings جديد في DB: market_type={market_type}")
                
                # تحديث إعدادات المستخدم
                cursor.execute("""
                    UPDATE users 
                    SET partial_percents = ?, tps_percents = ?, notifications = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (
                    json.dumps(settings.get('partial_percents', [25, 50, 25])),
                    json.dumps(settings.get('tps_percents', [1.5, 3.0, 5.0])),
                    settings.get('notifications', True),
                    user_id
                ))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"خطأ في تحديث إعدادات المستخدم {user_id}: {e}")
            return False
    
    # إدارة الصفقات
    def create_order(self, order_data: Dict) -> bool:
        """إنشاء صفقة جديدة"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO orders (
                        order_id, user_id, symbol, side, entry_price, quantity,
                        tps, sl, partial_close, status, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    order_data['order_id'],
                    order_data['user_id'],
                    order_data['symbol'],
                    order_data['side'],
                    order_data['entry_price'],
                    order_data['quantity'],
                    json.dumps(order_data.get('tps', [])),
                    order_data.get('sl', 0.0),
                    json.dumps(order_data.get('partial_close', [])),
                    order_data.get('status', 'OPEN'),
                    order_data.get('notes', '')
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"خطأ في إنشاء الصفقة: {e}")
            return False
    
    def get_user_orders(self, user_id: int, status: str = None) -> List[Dict]:
        """الحصول على صفقات المستخدم"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if status:
                    cursor.execute("""
                        SELECT * FROM orders 
                        WHERE user_id = ? AND status = ?
                        ORDER BY open_time DESC
                    """, (user_id, status))
                else:
                    cursor.execute("""
                        SELECT * FROM orders 
                        WHERE user_id = ?
                        ORDER BY open_time DESC
                    """, (user_id,))
                
                rows = cursor.fetchall()
                orders = []
                
                for row in rows:
                    order = dict(row)
                    
                    # تحويل النصوص JSON إلى قوائم
                    try:
                        order['tps'] = json.loads(order['tps'])
                        order['partial_close'] = json.loads(order['partial_close'])
                    except (json.JSONDecodeError, TypeError):
                        order['tps'] = []
                        order['partial_close'] = []
                    
                    orders.append(order)
                
                return orders
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على صفقات المستخدم {user_id}: {e}")
            return []
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """الحصول على صفقة محددة"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
                row = cursor.fetchone()
                
                if row:
                    order = dict(row)
                    
                    # تحويل النصوص JSON إلى قوائم
                    try:
                        order['tps'] = json.loads(order['tps'])
                        order['partial_close'] = json.loads(order['partial_close'])
                    except (json.JSONDecodeError, TypeError):
                        order['tps'] = []
                        order['partial_close'] = []
                    
                    return order
                return None
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على الصفقة {order_id}: {e}")
            return None
    
    def update_order(self, order_id: str, updates: Dict) -> bool:
        """تحديث صفقة"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # بناء استعلام التحديث
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    if key in ['tps', 'partial_close']:
                        set_clauses.append(f"{key} = ?")
                        values.append(json.dumps(value))
                    else:
                        set_clauses.append(f"{key} = ?")
                        values.append(value)
                
                if set_clauses:
                    values.append(order_id)
                    query = f"UPDATE orders SET {', '.join(set_clauses)} WHERE order_id = ?"
                    
                    cursor.execute(query, values)
                    conn.commit()
                    return cursor.rowcount > 0
                
                return False
                
        except Exception as e:
            logger.error(f"خطأ في تحديث الصفقة {order_id}: {e}")
            return False
    
    def close_order(self, order_id: str, close_price: float, pnl: float) -> bool:
        """إغلاق صفقة"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE orders 
                    SET status = 'CLOSED', close_time = CURRENT_TIMESTAMP
                    WHERE order_id = ?
                """, (order_id,))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"خطأ في إغلاق الصفقة {order_id}: {e}")
            return False
    
    def get_all_active_users(self) -> List[Dict]:
        """الحصول على جميع المستخدمين النشطين"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT u.*, s.* FROM users u
                    LEFT JOIN user_settings s ON u.user_id = s.user_id
                    WHERE u.is_active = 1
                """)
                
                rows = cursor.fetchall()
                users = []
                
                for row in rows:
                    user_data = dict(row)
                    
                    # تحويل النصوص JSON إلى قوائم
                    try:
                        user_data['partial_percents'] = json.loads(user_data['partial_percents'])
                        user_data['tps_percents'] = json.loads(user_data['tps_percents'])
                        user_data['preferred_symbols'] = json.loads(user_data['preferred_symbols'])
                    except (json.JSONDecodeError, TypeError):
                        user_data['partial_percents'] = [25, 50, 25]
                        user_data['tps_percents'] = [1.5, 3.0, 5.0]
                        user_data['preferred_symbols'] = ["BTCUSDT", "ETHUSDT"]
                    
                    users.append(user_data)
                
                return users
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على المستخدمين النشطين: {e}")
            return []
    
    def get_user_statistics(self, user_id: int) -> Dict:
        """الحصول على إحصائيات المستخدم"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # إجمالي الصفقات
                cursor.execute("""
                    SELECT COUNT(*) as total_orders FROM orders WHERE user_id = ?
                """, (user_id,))
                total_orders = cursor.fetchone()['total_orders']
                
                # الصفقات المفتوحة
                cursor.execute("""
                    SELECT COUNT(*) as open_orders FROM orders 
                    WHERE user_id = ? AND status = 'OPEN'
                """, (user_id,))
                open_orders = cursor.fetchone()['open_orders']
                
                # الصفقات المغلقة
                cursor.execute("""
                    SELECT COUNT(*) as closed_orders FROM orders 
                    WHERE user_id = ? AND status = 'CLOSED'
                """, (user_id,))
                closed_orders = cursor.fetchone()['closed_orders']
                
                return {
                    'total_orders': total_orders,
                    'open_orders': open_orders,
                    'closed_orders': closed_orders
                }
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات المستخدم {user_id}: {e}")
            return {
                'total_orders': 0,
                'open_orders': 0,
                'closed_orders': 0
            }
    
    # إدارة المطورين
    def create_developer(self, developer_id: int, developer_name: str, 
                        developer_key: str = None, webhook_url: str = None) -> bool:
        """إنشاء مطور جديد"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # التحقق من وجود المطور
                cursor.execute("SELECT developer_id FROM developers WHERE developer_id = ?", (developer_id,))
                if cursor.fetchone():
                    return False  # المطور موجود بالفعل
                
                # إنشاء المطور الجديد
                cursor.execute("""
                    INSERT INTO developers (developer_id, developer_name, developer_key, webhook_url)
                    VALUES (?, ?, ?, ?)
                """, (developer_id, developer_name, developer_key, webhook_url))
                
                conn.commit()
                logger.info(f"تم إنشاء مطور جديد: {developer_id} - {developer_name}")
                return True
                
        except Exception as e:
            logger.error(f"خطأ في إنشاء المطور {developer_id}: {e}")
            return False
    
    def get_developer(self, developer_id: int) -> Optional[Dict]:
        """الحصول على بيانات المطور"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM developers WHERE developer_id = ?", (developer_id,))
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على المطور {developer_id}: {e}")
            return None
    
    def get_all_developers(self) -> List[Dict]:
        """الحصول على جميع المطورين"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM developers")
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على المطورين: {e}")
            return []
    
    def update_developer(self, developer_id: int, updates: Dict) -> bool:
        """تحديث معلومات المطور"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # بناء استعلام التحديث
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    if key in ['developer_name', 'developer_key', 'webhook_url', 'is_active', 'can_broadcast']:
                        set_clauses.append(f"{key} = ?")
                        values.append(value)
                
                if set_clauses:
                    set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                    values.append(developer_id)
                    query = f"UPDATE developers SET {', '.join(set_clauses)} WHERE developer_id = ?"
                    
                    cursor.execute(query, values)
                    conn.commit()
                    return cursor.rowcount > 0
                
                return False
                
        except Exception as e:
            logger.error(f"خطأ في تحديث المطور {developer_id}: {e}")
            return False
    
    def toggle_developer_active(self, developer_id: int) -> bool:
        """تبديل حالة تشغيل/إيقاف المطور"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT is_active FROM developers WHERE developer_id = ?", (developer_id,))
                row = cursor.fetchone()
                if not row:
                    return False
                
                current_status = row['is_active']
                new_status = not bool(current_status)
                
                cursor.execute("""
                    UPDATE developers 
                    SET is_active = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE developer_id = ?
                """, (new_status, developer_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"خطأ في تبديل حالة المطور {developer_id}: {e}")
            return False
    
    def toggle_auto_broadcast(self, developer_id: int) -> bool:
        """تبديل حالة التوزيع التلقائي للإشارات"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT auto_broadcast FROM developers WHERE developer_id = ?", (developer_id,))
                row = cursor.fetchone()
                if not row:
                    return False
                
                current_status = row['auto_broadcast']
                new_status = not bool(current_status)
                
                cursor.execute("""
                    UPDATE developers 
                    SET auto_broadcast = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE developer_id = ?
                """, (new_status, developer_id))
                
                conn.commit()
                logger.info(f"✅ تم تبديل التوزيع التلقائي للمطور {developer_id} إلى: {new_status}")
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"خطأ في تبديل التوزيع التلقائي للمطور {developer_id}: {e}")
            return False
    
    def get_auto_broadcast_status(self, developer_id: int) -> bool:
        """الحصول على حالة التوزيع التلقائي للإشارات"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT auto_broadcast FROM developers WHERE developer_id = ?", (developer_id,))
                row = cursor.fetchone()
                
                if row:
                    return bool(row['auto_broadcast'])
                return False
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على حالة التوزيع التلقائي للمطور {developer_id}: {e}")
            return False
    
    def add_developer_follower(self, developer_id: int, user_id: int) -> bool:
        """إضافة متابع للمطور"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR IGNORE INTO developer_followers (developer_id, user_id)
                    VALUES (?, ?)
                """, (developer_id, user_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"خطأ في إضافة متابع للمطور {developer_id}: {e}")
            return False
    
    def remove_developer_follower(self, developer_id: int, user_id: int) -> bool:
        """إزالة متابع من المطور"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM developer_followers 
                    WHERE developer_id = ? AND user_id = ?
                """, (developer_id, user_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"خطأ في إزالة متابع من المطور {developer_id}: {e}")
            return False
    
    def get_developer_followers(self, developer_id: int) -> List[int]:
        """الحصول على قائمة متابعي المطور"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT user_id FROM developer_followers 
                    WHERE developer_id = ?
                """, (developer_id,))
                
                rows = cursor.fetchall()
                return [row['user_id'] for row in rows]
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على متابعي المطور {developer_id}: {e}")
            return []
    
    def create_developer_signal(self, developer_id: int, signal_data: Dict, 
                               target_followers: List[int]) -> Optional[int]:
        """حفظ إشارة من المطور"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO developer_signals (developer_id, signal_data, target_followers)
                    VALUES (?, ?, ?)
                """, (developer_id, json.dumps(signal_data), json.dumps(target_followers)))
                
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            logger.error(f"خطأ في حفظ إشارة المطور {developer_id}: {e}")
            return None
    
    def get_developer_signal_count(self, developer_id: int) -> int:
        """الحصول على عدد إشارات المطور"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT COUNT(*) as signal_count FROM developer_signals 
                    WHERE developer_id = ?
                """, (developer_id,))
                
                row = cursor.fetchone()
                return row['signal_count'] if row else 0
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على عدد إشارات المطور {developer_id}: {e}")
            return 0
    
    def save_developer_signal(self, developer_id: int, signal_data: Dict) -> bool:
        """حفظ إشارة من المطور في قاعدة البيانات"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # الحصول على قائمة المتابعين
                cursor.execute("""
                    SELECT user_id FROM developer_followers 
                    WHERE developer_id = ?
                """, (developer_id,))
                
                followers = [row['user_id'] for row in cursor.fetchall()]
                
                # حفظ الإشارة
                cursor.execute("""
                    INSERT INTO developer_signals (developer_id, signal_data, target_followers)
                    VALUES (?, ?, ?)
                """, (developer_id, json.dumps(signal_data), json.dumps(followers)))
                
                conn.commit()
                logger.info(f"✅ تم حفظ إشارة المطور {developer_id} بنجاح")
                return True
                
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ إشارة المطور {developer_id}: {e}")
            return False
    
    def log_trade(self, user_id: int, trade_data: Dict) -> bool:
        """
        حفظ سجل صفقة في قاعدة البيانات
        
        Args:
            user_id: معرف المستخدم
            trade_data: بيانات الصفقة (symbol, action, price, account_type, market_type, trade_amount, leverage, source)
        
        Returns:
            bool: True إذا تم الحفظ بنجاح
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO trade_logs 
                    (user_id, symbol, action, price, account_type, market_type, 
                     trade_amount, leverage, source, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    trade_data.get('symbol', ''),
                    trade_data.get('action', ''),
                    trade_data.get('price', 0),
                    trade_data.get('account_type', 'demo'),
                    trade_data.get('market_type', 'spot'),
                    trade_data.get('trade_amount', 0),
                    trade_data.get('leverage', 1),
                    trade_data.get('source', 'direct'),
                    trade_data.get('status', 'executed')
                ))
                
                conn.commit()
                logger.info(f"✅ تم حفظ سجل صفقة للمستخدم {user_id}: {trade_data.get('symbol')} {trade_data.get('action')}")
                return True
                
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ سجل صفقة للمستخدم {user_id}: {e}")
            return False
    
    def get_user_trade_logs(self, user_id: int, limit: int = 50) -> List[Dict]:
        """
        الحصول على سجل صفقات المستخدم
        
        Args:
            user_id: معرف المستخدم
            limit: عدد السجلات المراد إرجاعها
        
        Returns:
            List[Dict]: قائمة بسجلات الصفقات
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM trade_logs
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (user_id, limit))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على سجل صفقات المستخدم {user_id}: {e}")
            return []
    
    def get_trade_statistics(self, user_id: int) -> Dict:
        """
        الحصول على إحصائيات الصفقات للمستخدم
        
        Args:
            user_id: معرف المستخدم
        
        Returns:
            Dict: إحصائيات الصفقات
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # إجمالي الصفقات
                cursor.execute("""
                    SELECT COUNT(*) as total_trades,
                           SUM(CASE WHEN action = 'buy' THEN 1 ELSE 0 END) as buy_trades,
                           SUM(CASE WHEN action = 'sell' THEN 1 ELSE 0 END) as sell_trades,
                           SUM(CASE WHEN market_type = 'spot' THEN 1 ELSE 0 END) as spot_trades,
                           SUM(CASE WHEN market_type = 'futures' THEN 1 ELSE 0 END) as futures_trades,
                           SUM(CASE WHEN account_type = 'real' THEN 1 ELSE 0 END) as real_trades,
                           SUM(CASE WHEN account_type = 'demo' THEN 1 ELSE 0 END) as demo_trades
                    FROM trade_logs
                    WHERE user_id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                else:
                    return {
                        'total_trades': 0,
                        'buy_trades': 0,
                        'sell_trades': 0,
                        'spot_trades': 0,
                        'futures_trades': 0,
                        'real_trades': 0,
                        'demo_trades': 0
                    }
                
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على إحصائيات الصفقات للمستخدم {user_id}: {e}")
            return {}

# إنشاء مثيل عام لقاعدة البيانات
db_manager = DatabaseManager()
