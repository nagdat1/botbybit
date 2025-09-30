#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام قاعدة البيانات لبوت التداول
يدعم إدارة المستخدمين والصفقات مع بيئات منفصلة
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import threading

logger = logging.getLogger(__name__)

class DatabaseManager:
    """مدير قاعدة البيانات مع دعم متعدد المستخدمين"""

    def __init__(self, db_path: str = "trading_bot.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.pool_size = 5
        self.max_overflow = 10

    def init_database(self, url: str = None, pool_size: int = 5, max_overflow: int = 10):
        """تهيئة قاعدة البيانات وإنشاء الجداول"""
        try:
            # التحقق من صحة المعاملات وإضافة معلومات تشخيصية
            logger.info(f"بدء تهيئة قاعدة البيانات - المعاملات: url={url}, pool_size={pool_size}, max_overflow={max_overflow}")
            logger.info(f"نوع معامل url: {type(url)}")

            if url is not None and not isinstance(url, str):
                error_msg = f"معامل url يجب أن يكون نصاً أو None، لكن تم تمرير: {type(url)} - القيمة: {repr(url)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # تحديث مسار قاعدة البيانات إذا تم تمريره
            if url:
                logger.info(f"تحديث مسار قاعدة البيانات من '{self.db_path}' إلى '{url}'")
                # استخراج مسار الملف من URL SQLite
                if url.startswith("sqlite:///"):
                    self.db_path = url.replace("sqlite:///", "")
                else:
                    self.db_path = url

            # تحديث إعدادات التجمع
            self.pool_size = pool_size
            self.max_overflow = max_overflow

            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # جدول المستخدمين
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        api_key TEXT,
                        api_secret TEXT,
                        settings TEXT DEFAULT '{}',
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # جدول الصفقات
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS orders (
                        order_id TEXT PRIMARY KEY,
                        user_id INTEGER,
                        symbol TEXT NOT NULL,
                        side TEXT NOT NULL,
                        entry_price REAL NOT NULL,
                        quantity REAL NOT NULL,
                        open_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        tps TEXT DEFAULT '[]',
                        sl REAL DEFAULT 0,
                        partial_close TEXT DEFAULT '[]',
                        status TEXT DEFAULT 'open',
                        current_price REAL DEFAULT 0,
                        unrealized_pnl REAL DEFAULT 0,
                        leverage INTEGER DEFAULT 1,
                        margin_amount REAL DEFAULT 0,
                        liquidation_price REAL DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')

                # جدول تاريخ التداول
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trade_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        order_id TEXT,
                        symbol TEXT,
                        side TEXT,
                        entry_price REAL,
                        exit_price REAL,
                        quantity REAL,
                        pnl REAL,
                        leverage INTEGER,
                        margin_amount REAL,
                        trade_type TEXT,
                        closed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id),
                        FOREIGN KEY (order_id) REFERENCES orders (order_id)
                    )
                ''')

                # جدول إحصائيات المستخدمين
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_stats (
                        user_id INTEGER PRIMARY KEY,
                        total_trades INTEGER DEFAULT 0,
                        winning_trades INTEGER DEFAULT 0,
                        losing_trades INTEGER DEFAULT 0,
                        total_pnl REAL DEFAULT 0,
                        balance REAL DEFAULT 10000,
                        available_balance REAL DEFAULT 10000,
                        margin_locked REAL DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')

                conn.commit()
                conn.close()
                logger.info("تم تهيئة قاعدة البيانات بنجاح")

        except Exception as e:
            logger.error(f"خطأ في تهيئة قاعدة البيانات: {e}")
            raise
    
    
    def get_connection(self):
        """الحصول على اتصال قاعدة البيانات"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = (), fetch: bool = False):
        """تنفيذ استعلام قاعدة البيانات"""
        try:
            with self.lock:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute(query, params)
                
                if fetch:
                    result = cursor.fetchall()
                else:
                    conn.commit()
                    result = cursor.rowcount
                
                conn.close()
                return result
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الاستعلام: {e}")
            raise
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> bool:
        """إضافة مستخدم جديد"""
        try:
            # التحقق من وجود المستخدم
            if self.get_user(user_id):
                return True
            
            query = '''
                INSERT INTO users (user_id, username, first_name, last_name, settings)
                VALUES (?, ?, ?, ?, ?)
            '''
            
            default_settings = json.dumps({
                'account_type': 'demo',
                'market_type': 'spot',
                'trade_amount': 100.0,
                'leverage': 10,
                'language': 'ar'
            })
            
            self.execute_query(query, (user_id, username, first_name, last_name, default_settings))
            
            # إضافة إحصائيات المستخدم
            stats_query = '''
                INSERT INTO user_stats (user_id, balance, available_balance)
                VALUES (?, ?, ?)
            '''
            self.execute_query(stats_query, (user_id, 10000, 10000))
            
            logger.info(f"تم إضافة مستخدم جديد: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إضافة المستخدم: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """الحصول على بيانات المستخدم"""
        try:
            query = '''
                SELECT user_id, username, first_name, last_name, api_key, api_secret, 
                       settings, is_active, created_at, updated_at
                FROM users WHERE user_id = ?
            '''
            
            result = self.execute_query(query, (user_id,), fetch=True)
            
            if result:
                row = result[0]
                return {
                    'user_id': row[0],
                    'username': row[1],
                    'first_name': row[2],
                    'last_name': row[3],
                    'api_key': row[4],
                    'api_secret': row[5],
                    'settings': json.loads(row[6]) if row[6] else {},
                    'is_active': bool(row[7]),
                    'created_at': row[8],
                    'updated_at': row[9]
                }
            return None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على بيانات المستخدم: {e}")
            return None
    
    def update_user_api(self, user_id: int, api_key: str, api_secret: str) -> bool:
        """تحديث مفاتيح API للمستخدم"""
        try:
            query = '''
                UPDATE users 
                SET api_key = ?, api_secret = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            '''
            
            self.execute_query(query, (api_key, api_secret, user_id))
            logger.info(f"تم تحديث مفاتيح API للمستخدم: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث مفاتيح API: {e}")
            return False
    
    def update_user_settings(self, user_id: int, settings: Dict) -> bool:
        """تحديث إعدادات المستخدم"""
        try:
            query = '''
                UPDATE users 
                SET settings = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            '''
            
            self.execute_query(query, (json.dumps(settings), user_id))
            logger.info(f"تم تحديث إعدادات المستخدم: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث إعدادات المستخدم: {e}")
            return False
    
    def set_user_active(self, user_id: int, is_active: bool) -> bool:
        """تحديث حالة نشاط المستخدم"""
        try:
            query = '''
                UPDATE users 
                SET is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            '''
            
            self.execute_query(query, (is_active, user_id))
            logger.info(f"تم تحديث حالة نشاط المستخدم {user_id}: {is_active}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث حالة نشاط المستخدم: {e}")
            return False
    
    def add_order(self, order_id: str, user_id: int, symbol: str, side: str, 
                  entry_price: float, quantity: float, leverage: int = 1, 
                  margin_amount: float = 0, liquidation_price: float = 0) -> bool:
        """إضافة صفقة جديدة"""
        try:
            query = '''
                INSERT INTO orders (order_id, user_id, symbol, side, entry_price, 
                                  quantity, leverage, margin_amount, liquidation_price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            self.execute_query(query, (order_id, user_id, symbol, side, entry_price, 
                                     quantity, leverage, margin_amount, liquidation_price))
            
            logger.info(f"تم إضافة صفقة جديدة: {order_id} للمستخدم: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إضافة الصفقة: {e}")
            return False
    
    def get_user_orders(self, user_id: int, status: str = 'open') -> List[Dict]:
        """الحصول على صفقات المستخدم"""
        try:
            query = '''
                SELECT order_id, symbol, side, entry_price, quantity, open_time,
                       tps, sl, partial_close, status, current_price, unrealized_pnl,
                       leverage, margin_amount, liquidation_price
                FROM orders 
                WHERE user_id = ? AND status = ?
                ORDER BY open_time DESC
            '''
            
            result = self.execute_query(query, (user_id, status), fetch=True)
            
            orders = []
            for row in result:
                orders.append({
                    'order_id': row[0],
                    'symbol': row[1],
                    'side': row[2],
                    'entry_price': row[3],
                    'quantity': row[4],
                    'open_time': row[5],
                    'tps': json.loads(row[6]) if row[6] else [],
                    'sl': row[7],
                    'partial_close': json.loads(row[8]) if row[8] else [],
                    'status': row[9],
                    'current_price': row[10],
                    'unrealized_pnl': row[11],
                    'leverage': row[12],
                    'margin_amount': row[13],
                    'liquidation_price': row[14]
                })
            
            return orders
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على صفقات المستخدم: {e}")
            return []
    
    def update_order_price(self, order_id: str, current_price: float, unrealized_pnl: float) -> bool:
        """تحديث سعر الصفقة والربح/الخسارة"""
        try:
            query = '''
                UPDATE orders 
                SET current_price = ?, unrealized_pnl = ?
                WHERE order_id = ?
            '''
            
            self.execute_query(query, (current_price, unrealized_pnl, order_id))
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث سعر الصفقة: {e}")
            return False
    
    def update_order_tps(self, order_id: str, tps: List[Dict]) -> bool:
        """تحديث أهداف الأرباح"""
        try:
            query = '''
                UPDATE orders 
                SET tps = ?
                WHERE order_id = ?
            '''
            
            self.execute_query(query, (json.dumps(tps), order_id))
            logger.info(f"تم تحديث أهداف الأرباح للصفقة: {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث أهداف الأرباح: {e}")
            return False
    
    def update_order_sl(self, order_id: str, sl: float) -> bool:
        """تحديث وقف الخسارة"""
        try:
            query = '''
                UPDATE orders 
                SET sl = ?
                WHERE order_id = ?
            '''
            
            self.execute_query(query, (sl, order_id))
            logger.info(f"تم تحديث وقف الخسارة للصفقة: {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث وقف الخسارة: {e}")
            return False
    
    def partial_close_order(self, order_id: str, percentage: float, pnl: float) -> bool:
        """إغلاق جزئي للصفقة"""
        try:
            # الحصول على البيانات الحالية
            query = '''
                SELECT partial_close FROM orders WHERE order_id = ?
            '''
            result = self.execute_query(query, (order_id,), fetch=True)
            
            if result:
                current_partial = json.loads(result[0][0]) if result[0][0] else []
                current_partial.append({
                    'percentage': percentage,
                    'pnl': pnl,
                    'timestamp': datetime.now().isoformat()
                })
                
                # تحديث البيانات
                update_query = '''
                    UPDATE orders 
                    SET partial_close = ?
                    WHERE order_id = ?
                '''
                
                self.execute_query(update_query, (json.dumps(current_partial), order_id))
                logger.info(f"تم إغلاق جزئي للصفقة: {order_id} بنسبة {percentage}%")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في الإغلاق الجزئي: {e}")
            return False
    
    def close_order(self, order_id: str, exit_price: float, pnl: float) -> bool:
        """إغلاق الصفقة نهائياً"""
        try:
            # الحصول على بيانات الصفقة
            query = '''
                SELECT user_id, symbol, side, entry_price, quantity, leverage, margin_amount
                FROM orders WHERE order_id = ?
            '''
            result = self.execute_query(query, (order_id,), fetch=True)
            
            if not result:
                return False
            
            order_data = result[0]
            user_id = order_data[0]
            
            # إضافة إلى تاريخ التداول
            history_query = '''
                INSERT INTO trade_history (user_id, order_id, symbol, side, entry_price,
                                         exit_price, quantity, pnl, leverage, margin_amount, trade_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            trade_type = 'futures' if order_data[5] > 1 else 'spot'
            self.execute_query(history_query, (
                user_id, order_id, order_data[1], order_data[2], order_data[3],
                exit_price, order_data[4], pnl, order_data[5], order_data[6], trade_type
            ))
            
            # تحديث إحصائيات المستخدم
            self.update_user_stats(user_id, pnl)
            
            # تحديث حالة الصفقة
            update_query = '''
                UPDATE orders 
                SET status = 'closed'
                WHERE order_id = ?
            '''
            self.execute_query(update_query, (order_id,))
            
            logger.info(f"تم إغلاق الصفقة: {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إغلاق الصفقة: {e}")
            return False
    
    def update_user_stats(self, user_id: int, pnl: float):
        """تحديث إحصائيات المستخدم"""
        try:
            # الحصول على الإحصائيات الحالية
            query = '''
                SELECT total_trades, winning_trades, losing_trades, total_pnl, 
                       balance, available_balance, margin_locked
                FROM user_stats WHERE user_id = ?
            '''
            result = self.execute_query(query, (user_id,), fetch=True)
            
            if result:
                stats = result[0]
                total_trades = stats[0] + 1
                winning_trades = stats[1] + (1 if pnl > 0 else 0)
                losing_trades = stats[2] + (1 if pnl < 0 else 0)
                total_pnl = stats[3] + pnl
                balance = stats[4] + pnl
                available_balance = stats[5] + pnl
                
                # تحديث الإحصائيات
                update_query = '''
                    UPDATE user_stats 
                    SET total_trades = ?, winning_trades = ?, losing_trades = ?,
                        total_pnl = ?, balance = ?, available_balance = ?
                    WHERE user_id = ?
                '''
                
                self.execute_query(update_query, (
                    total_trades, winning_trades, losing_trades, 
                    total_pnl, balance, available_balance, user_id
                ))
            
        except Exception as e:
            logger.error(f"خطأ في تحديث إحصائيات المستخدم: {e}")
    
    def get_user_stats(self, user_id: int) -> Optional[Dict]:
        """الحصول على إحصائيات المستخدم"""
        try:
            query = '''
                SELECT total_trades, winning_trades, losing_trades, total_pnl,
                       balance, available_balance, margin_locked
                FROM user_stats WHERE user_id = ?
            '''
            
            result = self.execute_query(query, (user_id,), fetch=True)
            
            if result:
                stats = result[0]
                win_rate = (stats[1] / max(stats[0], 1)) * 100
                
                return {
                    'total_trades': stats[0],
                    'winning_trades': stats[1],
                    'losing_trades': stats[2],
                    'total_pnl': stats[3],
                    'balance': stats[4],
                    'available_balance': stats[5],
                    'margin_locked': stats[6],
                    'win_rate': win_rate
                }
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات المستخدم: {e}")
            return None
    
    def get_trade_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """الحصول على تاريخ التداول"""
        try:
            query = '''
                SELECT order_id, symbol, side, entry_price, exit_price, quantity,
                       pnl, leverage, margin_amount, trade_type, closed_at
                FROM trade_history 
                WHERE user_id = ?
                ORDER BY closed_at DESC
                LIMIT ?
            '''
            
            result = self.execute_query(query, (user_id, limit), fetch=True)
            
            history = []
            for row in result:
                history.append({
                    'order_id': row[0],
                    'symbol': row[1],
                    'side': row[2],
                    'entry_price': row[3],
                    'exit_price': row[4],
                    'quantity': row[5],
                    'pnl': row[6],
                    'leverage': row[7],
                    'margin_amount': row[8],
                    'trade_type': row[9],
                    'closed_at': row[10]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على تاريخ التداول: {e}")
            return []

# إنشاء مثيل عام لمدير قاعدة البيانات
db_manager = DatabaseManager()
