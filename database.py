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
                        initial_quantity REAL NOT NULL,
                        current_quantity REAL NOT NULL,
                        open_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        close_time TIMESTAMP,
                        take_profits TEXT DEFAULT '[]',
                        stop_loss TEXT DEFAULT NULL,
                        partial_closes TEXT DEFAULT '[]',
                        status TEXT DEFAULT 'OPEN',
                        market_type TEXT DEFAULT 'spot',
                        leverage INTEGER DEFAULT 1,
                        unrealized_pnl REAL DEFAULT 0.0,
                        realized_pnl REAL DEFAULT 0.0,
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
                
                quantity = order_data['quantity']
                
                cursor.execute("""
                    INSERT INTO orders (
                        order_id, user_id, symbol, side, entry_price, quantity,
                        initial_quantity, current_quantity, take_profits, stop_loss, 
                        partial_closes, status, market_type, leverage, 
                        unrealized_pnl, realized_pnl, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    order_data['order_id'],
                    order_data['user_id'],
                    order_data['symbol'],
                    order_data['side'],
                    order_data['entry_price'],
                    quantity,
                    order_data.get('initial_quantity', quantity),
                    order_data.get('current_quantity', quantity),
                    json.dumps(order_data.get('take_profits', [])),
                    json.dumps(order_data.get('stop_loss')) if order_data.get('stop_loss') else None,
                    json.dumps(order_data.get('partial_closes', [])),
                    order_data.get('status', 'OPEN'),
                    order_data.get('market_type', 'spot'),
                    order_data.get('leverage', 1),
                    order_data.get('unrealized_pnl', 0.0),
                    order_data.get('realized_pnl', 0.0),
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
                    
                    # تحويل النصوص JSON إلى قوائم/قواميس
                    try:
                        order['take_profits'] = json.loads(order['take_profits']) if order.get('take_profits') else []
                        order['stop_loss'] = json.loads(order['stop_loss']) if order.get('stop_loss') else None
                        order['partial_closes'] = json.loads(order['partial_closes']) if order.get('partial_closes') else []
                    except (json.JSONDecodeError, TypeError):
                        order['take_profits'] = []
                        order['stop_loss'] = None
                        order['partial_closes'] = []
                    
                    # دعم الحقول القديمة للتوافق
                    if 'tps' in order and not order.get('take_profits'):
                        try:
                            order['take_profits'] = json.loads(order['tps']) if order.get('tps') else []
                        except:
                            pass
                    
                    if 'sl' in order and not order.get('stop_loss') and order.get('sl'):
                        order['stop_loss'] = {'value': order['sl'], 'is_percentage_based': False}
                    
                    if 'partial_close' in order and not order.get('partial_closes'):
                        try:
                            order['partial_closes'] = json.loads(order['partial_close']) if order.get('partial_close') else []
                        except:
                            pass
                    
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
                    
                    # تحويل النصوص JSON إلى قوائم/قواميس
                    try:
                        order['take_profits'] = json.loads(order['take_profits']) if order.get('take_profits') else []
                        order['stop_loss'] = json.loads(order['stop_loss']) if order.get('stop_loss') else None
                        order['partial_closes'] = json.loads(order['partial_closes']) if order.get('partial_closes') else []
                    except (json.JSONDecodeError, TypeError):
                        order['take_profits'] = []
                        order['stop_loss'] = None
                        order['partial_closes'] = []
                    
                    # دعم الحقول القديمة للتوافق
                    if 'tps' in order and not order.get('take_profits'):
                        try:
                            order['take_profits'] = json.loads(order['tps']) if order.get('tps') else []
                        except:
                            pass
                    
                    if 'sl' in order and not order.get('stop_loss') and order.get('sl'):
                        order['stop_loss'] = {'value': order['sl'], 'is_percentage_based': False}
                    
                    if 'partial_close' in order and not order.get('partial_closes'):
                        try:
                            order['partial_closes'] = json.loads(order['partial_close']) if order.get('partial_close') else []
                        except:
                            pass
                    
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
                    if key in ['take_profits', 'partial_closes', 'tps', 'partial_close']:
                        set_clauses.append(f"{key} = ?")
                        values.append(json.dumps(value))
                    elif key == 'stop_loss':
                        set_clauses.append(f"{key} = ?")
                        values.append(json.dumps(value) if value is not None else None)
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

# إنشاء مثيل عام لقاعدة البيانات
db_manager = DatabaseManager()
