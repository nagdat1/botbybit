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
                
                # جدول مستويات Take Profit
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS take_profit_levels (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_id TEXT NOT NULL,
                        level_number INTEGER NOT NULL,
                        price_type TEXT NOT NULL,
                        value REAL NOT NULL,
                        close_percentage REAL NOT NULL,
                        target_price REAL,
                        executed BOOLEAN DEFAULT 0,
                        executed_time TIMESTAMP,
                        executed_price REAL,
                        pnl REAL,
                        FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
                    )
                """)
                
                # جدول Stop Loss
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stop_losses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_id TEXT NOT NULL,
                        price_type TEXT NOT NULL,
                        value REAL NOT NULL,
                        target_price REAL,
                        trailing BOOLEAN DEFAULT 0,
                        trailing_distance REAL,
                        trailing_activated_price REAL,
                        executed BOOLEAN DEFAULT 0,
                        executed_time TIMESTAMP,
                        executed_price REAL,
                        pnl REAL,
                        FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
                    )
                """)
                
                # جدول الإغلاقات الجزئية
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS partial_closes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_id TEXT NOT NULL,
                        close_type TEXT NOT NULL,
                        level INTEGER,
                        price REAL NOT NULL,
                        quantity REAL NOT NULL,
                        percentage REAL NOT NULL,
                        pnl REAL,
                        close_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
                    )
                """)
                
                # تحديث جدول orders لإضافة حقول جديدة
                # التحقق من وجود العمود remaining_quantity
                cursor.execute("PRAGMA table_info(orders)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'remaining_quantity' not in columns:
                    cursor.execute("ALTER TABLE orders ADD COLUMN remaining_quantity REAL DEFAULT 0")
                
                if 'realized_pnl' not in columns:
                    cursor.execute("ALTER TABLE orders ADD COLUMN realized_pnl REAL DEFAULT 0")
                
                if 'unrealized_pnl' not in columns:
                    cursor.execute("ALTER TABLE orders ADD COLUMN unrealized_pnl REAL DEFAULT 0")
                
                if 'current_price' not in columns:
                    cursor.execute("ALTER TABLE orders ADD COLUMN current_price REAL")
                
                conn.commit()
                logger.info("تم تهيئة قاعدة البيانات بنجاح")
                
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
        """تحديث إعدادات المستخدم"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # تحديث إعدادات التداول
                cursor.execute("""
                    UPDATE user_settings 
                    SET market_type = ?, trade_amount = ?, leverage = ?, account_type = ?
                    WHERE user_id = ?
                """, (
                    settings.get('market_type', 'spot'),
                    settings.get('trade_amount', 100.0),
                    settings.get('leverage', 10),
                    settings.get('account_type', 'demo'),
                    user_id
                ))
                
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
    
    # إدارة Take Profit و Stop Loss
    def add_take_profit(self, order_id: str, tp_data: Dict) -> bool:
        """إضافة مستوى Take Profit"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO take_profit_levels (
                        order_id, level_number, price_type, value, 
                        close_percentage, target_price
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    order_id,
                    tp_data['level_number'],
                    tp_data['price_type'],
                    tp_data['value'],
                    tp_data['close_percentage'],
                    tp_data.get('target_price')
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"خطأ في إضافة Take Profit: {e}")
            return False
    
    def add_stop_loss(self, order_id: str, sl_data: Dict) -> bool:
        """إضافة Stop Loss"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO stop_losses (
                        order_id, price_type, value, target_price,
                        trailing, trailing_distance
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    order_id,
                    sl_data['price_type'],
                    sl_data['value'],
                    sl_data.get('target_price'),
                    sl_data.get('trailing', False),
                    sl_data.get('trailing_distance')
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"خطأ في إضافة Stop Loss: {e}")
            return False
    
    def get_order_take_profits(self, order_id: str) -> List[Dict]:
        """الحصول على مستويات Take Profit للصفقة"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM take_profit_levels 
                    WHERE order_id = ?
                    ORDER BY level_number
                """, (order_id,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على Take Profits: {e}")
            return []
    
    def get_order_stop_loss(self, order_id: str) -> Optional[Dict]:
        """الحصول على Stop Loss للصفقة"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM stop_losses 
                    WHERE order_id = ?
                    LIMIT 1
                """, (order_id,))
                
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على Stop Loss: {e}")
            return None
    
    def update_take_profit(self, tp_id: int, updates: Dict) -> bool:
        """تحديث مستوى Take Profit"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
                
                if set_clauses:
                    values.append(tp_id)
                    query = f"UPDATE take_profit_levels SET {', '.join(set_clauses)} WHERE id = ?"
                    
                    cursor.execute(query, values)
                    conn.commit()
                    return cursor.rowcount > 0
                
                return False
                
        except Exception as e:
            logger.error(f"خطأ في تحديث Take Profit: {e}")
            return False
    
    def update_stop_loss(self, sl_id: int, updates: Dict) -> bool:
        """تحديث Stop Loss"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
                
                if set_clauses:
                    values.append(sl_id)
                    query = f"UPDATE stop_losses SET {', '.join(set_clauses)} WHERE id = ?"
                    
                    cursor.execute(query, values)
                    conn.commit()
                    return cursor.rowcount > 0
                
                return False
                
        except Exception as e:
            logger.error(f"خطأ في تحديث Stop Loss: {e}")
            return False
    
    def add_partial_close(self, partial_close_data: Dict) -> bool:
        """إضافة إغلاق جزئي"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO partial_closes (
                        order_id, close_type, level, price, 
                        quantity, percentage, pnl
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    partial_close_data['order_id'],
                    partial_close_data['close_type'],
                    partial_close_data.get('level'),
                    partial_close_data['price'],
                    partial_close_data['quantity'],
                    partial_close_data['percentage'],
                    partial_close_data.get('pnl')
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"خطأ في إضافة إغلاق جزئي: {e}")
            return False
    
    def get_order_partial_closes(self, order_id: str) -> List[Dict]:
        """الحصول على الإغلاقات الجزئية للصفقة"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM partial_closes 
                    WHERE order_id = ?
                    ORDER BY close_time DESC
                """, (order_id,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على الإغلاقات الجزئية: {e}")
            return []
    
    def get_full_order_details(self, order_id: str) -> Optional[Dict]:
        """الحصول على تفاصيل الصفقة الكاملة مع TP/SL"""
        try:
            order = self.get_order(order_id)
            if not order:
                return None
            
            # إضافة TP/SL
            order['take_profits'] = self.get_order_take_profits(order_id)
            order['stop_loss'] = self.get_order_stop_loss(order_id)
            order['partial_closes'] = self.get_order_partial_closes(order_id)
            
            return order
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على تفاصيل الصفقة: {e}")
            return None

# إنشاء مثيل عام لقاعدة البيانات
db_manager = DatabaseManager()
