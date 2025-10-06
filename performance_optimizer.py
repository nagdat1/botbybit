"""
⚡ Performance Optimizer - محسّن الأداء
تحسين أداء البوت وتقليل وقت الاستجابة
"""
import asyncio
from functools import wraps
import time
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """محسّن الأداء"""
    
    # Cache للبيانات المتكررة
    _cache = {}
    _cache_timestamps = {}
    
    @staticmethod
    def async_cache(ttl: int = 60):
        """Cache decorator للدوال async"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # إنشاء مفتاح cache
                cache_key = f"{func.__name__}_{args}_{kwargs}"
                
                # التحقق من وجود البيانات في الـ cache
                if cache_key in PerformanceOptimizer._cache:
                    timestamp = PerformanceOptimizer._cache_timestamps.get(cache_key, 0)
                    if time.time() - timestamp < ttl:
                        logger.debug(f"Cache hit for {func.__name__}")
                        return PerformanceOptimizer._cache[cache_key]
                
                # تنفيذ الدالة وحفظ النتيجة
                result = await func(*args, **kwargs)
                PerformanceOptimizer._cache[cache_key] = result
                PerformanceOptimizer._cache_timestamps[cache_key] = time.time()
                
                return result
            return wrapper
        return decorator
    
    @staticmethod
    async def run_parallel(tasks: list):
        """تشغيل مهام متعددة بالتوازي"""
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        except Exception as e:
            logger.error(f"Error in run_parallel: {e}")
            return []
    
    @staticmethod
    def measure_time(func: Callable):
        """قياس وقت تنفيذ الدالة"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            result = await func(*args, **kwargs)
            duration = time.time() - start
            
            if duration > 1:
                logger.warning(f"{func.__name__} took {duration:.2f}s")
            else:
                logger.debug(f"{func.__name__} took {duration:.2f}s")
            
            return result
        return wrapper
    
    @staticmethod
    def clear_cache():
        """مسح الـ cache"""
        PerformanceOptimizer._cache.clear()
        PerformanceOptimizer._cache_timestamps.clear()
        logger.info("Cache cleared")
    
    @staticmethod
    def get_cache_stats():
        """إحصائيات الـ cache"""
        return {
            'entries': len(PerformanceOptimizer._cache),
            'size_kb': len(str(PerformanceOptimizer._cache)) / 1024
        }


class RateLimiter:
    """محدد معدل الطلبات"""
    
    def __init__(self, max_calls: int = 10, period: int = 1):
        """
        max_calls: عدد الطلبات المسموحة
        period: الفترة الزمنية بالثواني
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = []
    
    async def acquire(self):
        """الحصول على إذن لتنفيذ طلب"""
        now = time.time()
        
        # إزالة الطلبات القديمة
        self.calls = [call for call in self.calls if now - call < self.period]
        
        # التحقق من الحد الأقصى
        if len(self.calls) >= self.max_calls:
            wait_time = self.period - (now - self.calls[0])
            if wait_time > 0:
                logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                return await self.acquire()
        
        self.calls.append(now)
        return True


# إنشاء rate limiter للـ API calls
api_rate_limiter = RateLimiter(max_calls=20, period=1)


async def throttled_api_call(api_func, *args, **kwargs):
    """استدعاء API مع rate limiting"""
    await api_rate_limiter.acquire()
    return await api_func(*args, **kwargs)


class BatchProcessor:
    """معالج الدفعات - تجميع الطلبات المتشابهة"""
    
    def __init__(self, batch_size: int = 10, max_wait: float = 0.5):
        self.batch_size = batch_size
        self.max_wait = max_wait
        self.pending_items = []
        self.processing = False
    
    async def add_item(self, item: Any, processor: Callable):
        """إضافة عنصر للدفعة"""
        self.pending_items.append((item, processor))
        
        if len(self.pending_items) >= self.batch_size and not self.processing:
            await self.process_batch()
        elif len(self.pending_items) == 1:
            # بدء مؤقت للمعالجة
            asyncio.create_task(self._delayed_process())
    
    async def _delayed_process(self):
        """معالجة متأخرة للدفعة"""
        await asyncio.sleep(self.max_wait)
        if self.pending_items and not self.processing:
            await self.process_batch()
    
    async def process_batch(self):
        """معالجة الدفعة"""
        if self.processing or not self.pending_items:
            return
        
        self.processing = True
        items_to_process = self.pending_items[:]
        self.pending_items = []
        
        try:
            tasks = [processor(item) for item, processor in items_to_process]
            await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            self.processing = False


# معالج دفعات عام
batch_processor = BatchProcessor()


def optimize_query(query_func: Callable):
    """تحسين استعلامات قاعدة البيانات"""
    @wraps(query_func)
    def wrapper(*args, **kwargs):
        # إضافة LIMIT تلقائياً
        if 'limit' not in kwargs:
            kwargs['limit'] = 100
        
        result = query_func(*args, **kwargs)
        return result
    return wrapper


class ConnectionPool:
    """مجمع الاتصالات"""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connections = []
        self.in_use = set()
    
    async def get_connection(self):
        """الحصول على اتصال"""
        # البحث عن اتصال متاح
        for conn in self.connections:
            if conn not in self.in_use:
                self.in_use.add(conn)
                return conn
        
        # إنشاء اتصال جديد
        if len(self.connections) < self.max_connections:
            conn = await self._create_connection()
            self.connections.append(conn)
            self.in_use.add(conn)
            return conn
        
        # الانتظار حتى يتوفر اتصال
        while True:
            await asyncio.sleep(0.1)
            for conn in self.connections:
                if conn not in self.in_use:
                    self.in_use.add(conn)
                    return conn
    
    async def release_connection(self, conn):
        """تحرير اتصال"""
        if conn in self.in_use:
            self.in_use.remove(conn)
    
    async def _create_connection(self):
        """إنشاء اتصال جديد"""
        # يتم تخصيصه حسب نوع الاتصال
        return {"id": len(self.connections)}


# مجمع اتصالات قاعدة البيانات
db_pool = ConnectionPool(max_connections=5)


class MemoryOptimizer:
    """محسّن الذاكرة"""
    
    @staticmethod
    def limit_list_size(lst: list, max_size: int = 1000):
        """تحديد حجم القائمة"""
        if len(lst) > max_size:
            return lst[-max_size:]
        return lst
    
    @staticmethod
    def clear_old_data(data_dict: dict, max_age: int = 3600):
        """مسح البيانات القديمة"""
        now = time.time()
        keys_to_delete = []
        
        for key, (timestamp, _) in data_dict.items():
            if now - timestamp > max_age:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del data_dict[key]
        
        return len(keys_to_delete)


# تصدير الأدوات الرئيسية
__all__ = [
    'PerformanceOptimizer',
    'RateLimiter',
    'BatchProcessor',
    'throttled_api_call',
    'api_rate_limiter',
    'batch_processor',
    'optimize_query',
    'ConnectionPool',
    'db_pool',
    'MemoryOptimizer'
]

